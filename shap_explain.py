import json
import numpy as np
import matplotlib.pyplot as plt
import shap
import cv2

from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image


# =========================
# LOAD MODEL
# =========================
model = load_model("models/plantdoc_model.keras")

# =========================
# LOAD CLASS NAMES
# =========================
with open("models/class_names.json", encoding="utf-8") as f:
    classes = json.load(f)

# =========================
# IMAGE
# =========================
img_path = "test_leaf_apple.JPG"

img = image.load_img(
    img_path,
    target_size=(224, 224)
)

img_arr = image.img_to_array(img) / 255.0
input_img = np.expand_dims(img_arr, axis=0)

# =========================
# PREDICTION
# =========================
prediction = model.predict(input_img, verbose=0)[0]

predicted_index = int(np.argmax(prediction))
predicted_class = classes[predicted_index]
confidence = prediction[predicted_index] * 100

print("Prediction:", predicted_class)
print(f"Confidence: {confidence:.2f}%")

# =========================
# SHAP
# =========================
print("\nGenerating SHAP explanation...")
print("Please wait... CPU processing may take some time.")

masker = shap.maskers.Image(
    "blur(32,32)",
    input_img[0].shape
)

explainer = shap.Explainer(
    model,
    masker,
    output_names=classes
)

shap_values = explainer(
    input_img,
    max_evals=100,
    batch_size=1
)

# =========================
# GET PREDICTED CLASS SHAP
# =========================
values = shap_values.values

if values.ndim == 5:
    class_shap = values[0, :, :, :, predicted_index]
else:
    class_shap = values[0]

# =========================
# CREATE HEATMAP
# =========================
heatmap = np.abs(class_shap).sum(axis=-1)

# Normalize
heatmap = heatmap - heatmap.min()

if heatmap.max() > 0:
    heatmap = heatmap / heatmap.max()

# Smooth the heatmap
heatmap = cv2.GaussianBlur(
    heatmap.astype(np.float32),
    (0, 0),
    sigmaX=8
)

# Normalize again
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
# OVERLAY
# =========================
original = np.uint8(img_arr * 255)

overlay = cv2.addWeighted(
    original,
    0.60,
    heatmap_color,
    0.40,
    0
)

# =========================
# SAVE RESULT
# =========================
plt.figure(figsize=(9, 9))

plt.imshow(overlay)
plt.axis("off")

plt.title(
    f"SHAP Explanation\n"
    f"Prediction: {predicted_class}\n"
    f"Confidence: {confidence:.2f}%"
)

plt.tight_layout()

plt.savefig(
    "shap_output.png",
    dpi=200,
    bbox_inches="tight"
)

plt.show()

print("\nSHAP explanation saved as:")
print("shap_output.png")