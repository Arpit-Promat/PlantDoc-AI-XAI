# PlantDoc - Ready-to-Run Plant Disease Detection

A Flask + TensorFlow project using MobileNetV2 transfer learning.

## 1. Dataset

Download the PlantDoc dataset from its original GitHub repository and place the
training class folders inside:

dataset/train/

Example:

dataset/train/
├── Tomato_Early_blight/
│   ├── image1.jpg
│   └── image2.jpg
├── Tomato_Late_blight/
│   └── ...
└── Apple_Scab/
    └── ...

The folder name becomes the predicted class name.

## 2. Create virtual environment (recommended)

Windows:

python -m venv venv
venv\Scripts\activate

## 3. Install libraries

pip install -r requirements.txt

## 4. Train model

python train.py

The trained model will be saved as:

models/plantdoc_model.keras

## 5. Run web application

python app.py

Open:

http://127.0.0.1:5000

## 6. Command-line prediction

python predict.py path/to/leaf.jpg

## Important

The ZIP contains the complete application code, but not the large PlantDoc
image dataset itself. Add the downloaded dataset to dataset/train/ before
training.
