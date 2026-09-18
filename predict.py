import os
import json
import sys
import numpy as np
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image

if len(sys.argv) != 2:
    print("Usage: python predict.py path/to/leaf.jpg")
    raise SystemExit(1)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "models", "plantdoc_model.keras")
CLASS_NAMES_PATH = os.path.join(BASE_DIR, "models", "class_names.json")

model = load_model(MODEL_PATH)
with open(CLASS_NAMES_PATH, encoding="utf-8") as f:
    classes = json.load(f)

img = image.load_img(sys.argv[1], target_size=(224, 224))
arr = image.img_to_array(img) / 255.0
pred = model.predict(np.expand_dims(arr, 0), verbose=0)[0]
idx = int(np.argmax(pred))

print(f"Prediction: {classes[idx]}")
print(f"Confidence: {pred[idx] * 100:.2f}%")
