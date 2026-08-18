import os
import json
import numpy as np
import shap
import cv2

from flask import Flask, render_template, request
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image


# =========================
# FLASK APP
# =========================

app = Flask(__name__)


# =========================
# MODEL & CLASS NAMES
# =========================

MODEL_PATH = "models/plantdoc_model.keras"
CLASS_PATH = "models/class_names.json"

model = load_model(MODEL_PATH)

with open(CLASS_PATH, encoding="utf-8") as f:
    class_names = json.load(f)


# =========================
# SHAP EXPLANATION FUNCTION
# =========================

def generate_shap(img_arr, predicted_index):

    print("Generating SHAP explanation...")
    print("Please wait...")

    masker = shap.maskers.Image(
        "blur(32,32)",
        img_arr[0].shape
    )

    explainer = shap.Explainer(
        model,
        masker,
        output_names=class_names
    )

    shap_values = explainer(
        img_arr,
        max_evals=100,
        batch_size=1
    )

    values = shap_values.values

    # Get SHAP values for predicted class
    if values.ndim == 5:
        class_shap = values[0, :, :, :, predicted_index]
    else:
        class_shap = values[0]

    # =========================
    # CREATE HEATMAP
    # =========================

    heatmap = np.abs(class_shap).sum(axis=-1)

    heatmap = heatmap - heatmap.min()

    if heatmap.max() > 0:
        heatmap = heatmap / heatmap.max()

    # Smooth heatmap
    heatmap = cv2.GaussianBlur(
        heatmap.astype(np.float32),
        (0, 0),
        sigmaX=8
    )

    if heatmap.max() > 0:
        heatmap = heatmap / heatmap.max()

    # Convert to color heatmap
    heatmap_color = cv2.applyColorMap(
        np.uint8(255 * heatmap),
        cv2.COLORMAP_JET
    )

    heatmap_color = cv2.cvtColor(
        heatmap_color,
        cv2.COLOR_BGR2RGB
    )

    # =========================
    # ORIGINAL IMAGE
    # =========================

    original = np.uint8(img_arr[0] * 255)

    # =========================
    # OVERLAY
    # =========================

    overlay = cv2.addWeighted(
        original,
        0.60,
        heatmap_color,
        0.40,
        0
    )

    # =========================
    # SAVE SHAP IMAGE
    # =========================

    os.makedirs("static", exist_ok=True)

    shap_path = os.path.join(
        "static",
        "shap_output.jpg"
    )

    cv2.imwrite(
        shap_path,
        cv2.cvtColor(
            overlay,
            cv2.COLOR_RGB2BGR
        )
    )

    print("SHAP explanation saved.")

    return "/static/shap_output.jpg"


# =========================
# HOME / PREDICTION ROUTE
# =========================

@app.route("/", methods=["GET", "POST"])
def index():

    prediction = None
    confidence = None
    error = None
    shap_image = None
    original_image = None
    ai_explanation = []


    # =========================
    # POST REQUEST
    # =========================

    if request.method == "POST":

        if "image" not in request.files:

            error = "Please select an image."

        else:

            file = request.files["image"]

            if file.filename == "":

                error = "Please select an image."

            else:

                try:

                    # =========================
                    # SAVE ORIGINAL IMAGE
                    # =========================

                    upload_folder = os.path.join(
                        "static",
                        "uploads"
                    )

                    os.makedirs(
                        upload_folder,
                        exist_ok=True
                    )

                    original_path = os.path.join(
                        upload_folder,
                        "original_leaf.jpg"
                    )

                    file.seek(0)

                    file.save(original_path)

                    original_image = (
                        "/static/uploads/original_leaf.jpg"
                    )


                    # =========================
                    # LOAD IMAGE FOR PREDICTION
                    # =========================

                    img = image.load_img(
                        original_path,
                        target_size=(224, 224)
                    )


                    # =========================
                    # CONVERT IMAGE TO ARRAY
                    # =========================

                    arr = (
                        image.img_to_array(img)
                        / 255.0
                    )

                    input_image = np.expand_dims(
                        arr,
                        axis=0
                    )


                    # =========================
                    # MODEL PREDICTION
                    # =========================

                    pred = model.predict(
                        input_image,
                        verbose=0
                    )[0]

                    idx = int(
                        np.argmax(pred)
                    )


                    # =========================
                    # PREDICTION NAME
                    # =========================

                    prediction = (
                        class_names[idx]
                        if idx < len(class_names)
                        else f"Class {idx}"
                    )


                    # =========================
                    # CONFIDENCE
                    # =========================

                    confidence = round(
                        float(pred[idx]) * 100,
                        2
                    )


                    print(
                        f"Prediction: {prediction}"
                    )

                    print(
                        f"Confidence: {confidence}%"
                    )


                    # =========================
                    # AI EXPLANATION
                    # =========================

                    ai_explanation = [

                        f"The model predicted "
                        f"{prediction} as the most likely class.",

                        f"The model assigned a confidence "
                        f"score of {confidence}%, indicating "
                        f"strong classification confidence.",

                        "SHAP highlights the image regions "
                        "that contributed most to the model's "
                        "prediction.",

                        "The highlighted regions help identify "
                        "which visible leaf features influenced "
                        "the classification.",

                        "This explanation improves model "
                        "transparency by showing why the AI "
                        "reached its prediction instead of "
                        "only giving the final disease name."
                    ]


                    # =========================
                    # SHAP EXPLANATION
                    # =========================

                    shap_image = generate_shap(
                        input_image,
                        idx
                    )


                except Exception as exc:

                    error = (
                        f"Prediction error: {exc}"
                    )


    # =========================
    # RENDER HTML
    # =========================

    return render_template(
        "index.html",
        prediction=prediction,
        confidence=confidence,
        error=error,
        shap_image=shap_image,
        original_image=original_image,
        ai_explanation=ai_explanation
    )


# =========================
# RUN APP
# =========================

if __name__ == "__main__":

    app.run(
        debug=True
    )