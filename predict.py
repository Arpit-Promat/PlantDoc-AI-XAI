import json
import sys
import numpy as np
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image

if len(sys.argv) != 2:
    print("Usage: python predict.py path/to/leaf.jpg")
    raise SystemExit(1)

model = load_model("models/plantdoc_model.keras")
with open("models/class_names.json", encoding="utf-8") as f:
    classes = json.load(f)

img = image.load_img(sys.argv[1], target_size=(224, 224))
arr = image.img_to_array(img) / 255.0
pred = model.predict(np.expand_dims(arr, 0), verbose=0)[0]
idx = int(np.argmax(pred))

print(f"Prediction: {classes[idx]}")
print(f"Confidence: {pred[idx] * 100:.2f}%")
