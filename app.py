import os
import json
import uuid
import numpy as np

from flask import Flask, render_template, request
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image

from database import configure_database
from security import configure_security, limiter, validate_uploaded_image
from management_api import register_management_routes
from model_registry import get_model_spec
from prediction_engine import (
    CONFIDENCE_THRESHOLD,
    MARGIN_THRESHOLD,
    assess_prediction,
)


app = Flask(__name__)
configure_database(app)
configure_security(app)
register_management_routes(app)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

GENERAL_SPEC = get_model_spec("general")
GENERAL_MODEL_PATH = os.path.join(BASE_DIR, GENERAL_SPEC.model_path)
GENERAL_CLASS_PATH = os.path.join(BASE_DIR, GENERAL_SPEC.class_names_path)
general_model = load_model(GENERAL_MODEL_PATH, compile=False)
with open(GENERAL_CLASS_PATH, encoding="utf-8") as f:
    general_class_names = json.load(f)

MANGO_SPEC = get_model_spec("mango")
MANGO_MODEL_PATH = os.path.join(BASE_DIR, MANGO_SPEC.model_path)
MANGO_CLASS_PATH = os.path.join(BASE_DIR, MANGO_SPEC.class_names_path)
mango_model = load_model(MANGO_MODEL_PATH, compile=False)
with open(MANGO_CLASS_PATH, encoding="utf-8") as f:
    mango_class_names = json.load(f)

LEAF_SPEC = get_model_spec("leaf_detector")
LEAF_DETECTOR_MODEL_PATH = os.path.join(BASE_DIR, LEAF_SPEC.model_path)
LEAF_DETECTOR_CLASSES_PATH = os.path.join(BASE_DIR, LEAF_SPEC.class_names_path)
leaf_detector_model = load_model(LEAF_DETECTOR_MODEL_PATH, compile=False)
with open(LEAF_DETECTOR_CLASSES_PATH, encoding="utf-8") as f:
    leaf_detector_class_indices = json.load(f)

LEAF_INDEX = leaf_detector_class_indices.get("leaf", 0)
LEAF_DETECTOR_THRESHOLD = 0.5
ALLOWED_PLANT_TYPES = {"general", "mango"}


def get_model_and_classes(plant_type):
    if plant_type == "mango":
        return mango_model, mango_class_names
    return general_model, general_class_names


def get_model_key(plant_type):
    return "mango" if plant_type == "mango" else "general"


def is_leaf_image(input_image_array):
    pred = leaf_detector_model.predict(input_image_array, verbose=0)[0][0]
    if LEAF_INDEX == 0:
        leaf_probability = 1.0 - float(pred)
    else:
        leaf_probability = float(pred)
    print(f"Leaf detector probability (leaf): {leaf_probability * 100:.2f}%")
    return leaf_probability >= LEAF_DETECTOR_THRESHOLD, leaf_probability


def get_confidence_level(confidence_value):
    if confidence_value >= 85:
        return "high", "High Confidence"
    if confidence_value >= 70:
        return "moderate", "Moderate Confidence"
    return "low", "Low Confidence"


def generate_shap(model, class_names, img_arr, predicted_index):
    import shap
    import cv2

    print("Generating SHAP explanation...")
    print("Please wait...")
    masker = shap.maskers.Image("blur(32,32)", img_arr[0].shape)
    explainer = shap.Explainer(model, masker, output_names=class_names)
    shap_values = explainer(img_arr, max_evals=30, batch_size=1)
    values = shap_values.values

    if values.ndim == 5:
        class_shap = values[0, :, :, :, predicted_index]
    else:
        class_shap = values[0]

    heatmap = np.abs(class_shap).sum(axis=-1)
    heatmap = heatmap - heatmap.min()
    if heatmap.max() > 0:
        heatmap = heatmap / heatmap.max()

    heatmap = cv2.GaussianBlur(heatmap.astype(np.float32), (0, 0), sigmaX=8)
    if heatmap.max() > 0:
        heatmap = heatmap / heatmap.max()

    heatmap_color = cv2.applyColorMap(np.uint8(255 * heatmap), cv2.COLORMAP_JET)
    heatmap_color = cv2.cvtColor(heatmap_color, cv2.COLOR_BGR2RGB)
    original = np.uint8(img_arr[0] * 255)
    overlay = cv2.addWeighted(original, 0.60, heatmap_color, 0.40, 0)

    os.makedirs(os.path.join(BASE_DIR, "static"), exist_ok=True)
    shap_path = os.path.join(BASE_DIR, "static", "shap_output.jpg")
    cv2.imwrite(shap_path, cv2.cvtColor(overlay, cv2.COLOR_RGB2BGR))
    print("SHAP explanation saved.")
    return "/static/shap_output.jpg"


@app.route("/", methods=["GET", "POST"])
@limiter.limit("20 per minute", methods=["POST"])
def index():
    prediction = None
    confidence = None
    confidence_level = None
    confidence_label = None
    error = None
    shap_image = None
    original_image = None
    ai_explanation = []
    selected_plant_type = "general"

    if request.method == "POST":
        selected_plant_type = request.form.get("plant_type", "general").strip().lower()

        if selected_plant_type not in ALLOWED_PLANT_TYPES:
            error = "Invalid plant type selected."
        elif "image" not in request.files:
            error = "Please select an image."
        else:
            file = request.files["image"]
            valid_image, validation_result = validate_uploaded_image(file)

            if not valid_image:
                error = validation_result
            else:
                try:
                    model, class_names = get_model_and_classes(selected_plant_type)
                    model_key = get_model_key(selected_plant_type)
                    upload_folder = os.path.join(BASE_DIR, "static", "uploads")
                    os.makedirs(upload_folder, exist_ok=True)

                    safe_name = validation_result
                    extension = safe_name.rsplit(".", 1)[-1].lower()
                    unique_name = f"{uuid.uuid4().hex}.{extension}"
                    original_path = os.path.join(upload_folder, unique_name)

                    file.seek(0)
                    file.save(original_path)
                    img = image.load_img(original_path, target_size=(224, 224))
                    arr = image.img_to_array(img) / 255.0
                    input_image = np.expand_dims(arr, axis=0)

                    is_leaf, _leaf_probability = is_leaf_image(input_image)
                    if not is_leaf:
                        print("Rejected by leaf detector — not a leaf image.")
                        error = "This doesn't look like a leaf. Please upload a clear photo of a plant leaf."
                    else:
                        original_image = f"/static/uploads/{unique_name}"
                        raw_pred = model.predict(input_image, verbose=0)[0]
                        result = assess_prediction(raw_pred, class_names, model_key, top_k=3)
                        idx = result["predicted_index"]
                        prediction = result["prediction"]
                        confidence = result["confidence"]
                        margin = result["margin"]

                        print(f"Plant type: {selected_plant_type}")
                        print(f"Model: {result['model_version']}")
                        print(f"Prediction: {prediction}")
                        print(f"Confidence: {confidence}%")
                        print(f"Margin (top1 - top2): {margin}%")

                        if not result["accepted"]:
                            print("Rejected — confidence or margin below threshold.")
                            error = "The image is unclear, or the disease could not be identified confidently. Please upload a clearer photo of the leaf."
                            prediction = None
                            confidence = None
                            original_image = None
                        else:
                            confidence_level = result["confidence_level"]
                            confidence_label = result["confidence_label"]
                            ai_explanation = [
                                f"The model predicted {prediction} as the most likely class.",
                                f"The model assigned a confidence score of {confidence}%, indicating strong classification confidence.",
                                "SHAP highlights the image regions that contributed most to the model's prediction.",
                                "The highlighted regions help identify which visible leaf features influenced the classification.",
                                "This explanation improves model transparency by showing why the AI reached its prediction instead of only giving the final disease name.",
                            ]
                            shap_image = generate_shap(model, class_names, input_image, idx)

                except Exception as exc:
                    print(f"Prediction error: {exc}")
                    error = "Unable to process the image right now. Please try again with a valid leaf image."

    return render_template(
        "index.html",
        prediction=prediction,
        confidence=confidence,
        confidence_level=confidence_level,
        confidence_label=confidence_label,
        error=error,
        shap_image=shap_image,
        original_image=original_image,
        ai_explanation=ai_explanation,
        selected_plant_type=selected_plant_type,
    )


if __name__ == "__main__":
    app.run(
        debug=os.getenv("FLASK_DEBUG", "0") == "1",
        host=os.getenv("FLASK_HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", "5000")),
        use_reloader=False,
    )
