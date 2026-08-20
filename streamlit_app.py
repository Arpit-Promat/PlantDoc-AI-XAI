import streamlit as st
import json
import numpy as np
from PIL import Image
from tensorflow.keras.models import load_model


# =========================
# PAGE CONFIG
# =========================

st.set_page_config(
    page_title="PlantDoc AI",
    page_icon="🌿",
    layout="wide"
)


# =========================
# LOAD MODEL
# =========================

@st.cache_resource
def load_plant_model():

    model = load_model(
        "models/plantdoc_model.keras"
    )

    with open(
        "models/class_names.json",
        encoding="utf-8"
    ) as f:

        classes = json.load(f)

    return model, classes


model, class_names = load_plant_model()


# =========================
# TITLE
# =========================

st.title("🌿 PlantDoc AI")

st.subheader(
    "AI-Based Plant Disease Detection"
)

st.write(
    "Upload a plant leaf image to analyze its health."
)


# =========================
# IMAGE UPLOAD
# =========================

uploaded_file = st.file_uploader(
    "Upload Leaf Image",
    type=["jpg", "jpeg", "png"]
)


if uploaded_file is not None:

    # Load image
    img = Image.open(
        uploaded_file
    ).convert("RGB")


    # =========================
    # ORIGINAL IMAGE
    # =========================

    st.subheader("🌿 Uploaded Leaf")

    st.image(
        img,
        caption="Original Leaf Image",
        use_container_width=True
    )


    # =========================
    # PREPROCESS
    # =========================

    resized_img = img.resize(
        (224, 224)
    )

    arr = np.array(
        resized_img
    ).astype("float32") / 255.0

    input_image = np.expand_dims(
        arr,
        axis=0
    )


    # =========================
    # PREDICTION
    # =========================

    with st.spinner(
        "AI is analyzing the leaf..."
    ):

        pred = model.predict(
            input_image,
            verbose=0
        )[0]


    # =========================
    # TOP 3
    # =========================

    top_indices = np.argsort(
        pred
    )[-3:][::-1]


    st.subheader(
        "🤖 AI Prediction"
    )


    # Main prediction

    main_idx = int(
        top_indices[0]
    )

    prediction = (
        class_names[main_idx]
        if main_idx < len(class_names)
        else f"Class {main_idx}"
    )

    confidence = (
        float(pred[main_idx]) * 100
    )


    st.success(
        f"Prediction: {prediction}"
    )

    st.metric(
        "Confidence",
        f"{confidence:.2f}%"
    )


    # =========================
    # TOP 3 PREDICTIONS
    # =========================

    st.subheader(
        "📊 Top 3 Predictions"
    )


    for rank, idx in enumerate(
        top_indices,
        start=1
    ):

        label = (
            class_names[int(idx)]
            if int(idx) < len(class_names)
            else f"Class {idx}"
        )

        percentage = (
            float(pred[idx]) * 100
        )

        st.write(
            f"**{rank}. {label} — "
            f"{percentage:.2f}%**"
        )

        st.progress(
            min(
                percentage / 100,
                1.0
            )
        )


    # =========================
    # AI EXPLANATION
    # =========================

    st.subheader(
        "🧠 AI Explanation"
    )


    explanations = [

        f"The AI classified the uploaded leaf as "
        f"**{prediction}**.",

        f"The model's calculated confidence for "
        f"the top prediction is **{confidence:.2f}%**.",

        "The prediction is based on visual patterns "
        "learned from the training dataset.",

        "The model analyzes leaf texture, color, "
        "shape and visible disease-related patterns.",

        "Different regions of the leaf can contribute "
        "differently to the final classification."
    ]


    for i, explanation in enumerate(
        explanations,
        start=1
    ):

        st.write(
            f"**{i}.** {explanation}"
        )


    # =========================
    # DISCLAIMER
    # =========================

    st.info(
        "⚠️ This AI prediction is an automated "
        "screening result and should not replace "
        "professional agricultural diagnosis."
    )