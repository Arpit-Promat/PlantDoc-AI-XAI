import tensorflow as tf

model = tf.keras.models.load_model("models/plantdoc_model.keras")

print("Model loaded successfully!")