import streamlit as st
import json
import numpy as np
import cv2
import shap

from PIL import Image
from tensorflow.keras.models import load_model


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="PlantDoc AI",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="collapsed"
)


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(
    """
    <style>

    /* Main background */
    .stApp {
        background:
            radial-gradient(circle at 10% 10%, rgba(30, 100, 65, 0.20), transparent 30%),
            radial-gradient(circle at 90% 20%, rgba(20, 80, 70, 0.18), transparent 30%),
            #07120f;
        color: #f5fff8;
    }

    /* Hide Streamlit default menu/footer */
    #MainMenu {
        visibility: hidden;
    }

    footer {
        visibility: hidden;
    }

    header {
        background: transparent !important;
    }

    /* Main container */
    .block-container {
        max-width: 1250px;
        padding-top: 2rem;
        padding-bottom: 4rem;
    }

    /* Hero */
    .hero {
        padding: 34px;
        border-radius: 28px;
        background:
            linear-gradient(
                135deg,
                rgba(19, 67, 44, 0.92),
                rgba(7, 25, 20, 0.96)
            );
        border: 1px solid rgba(92, 220, 137, 0.25);
        box-shadow: 0 20px 60px rgba(0,0,0,0.30);
        margin-bottom: 35px;
    }

    .hero-title {
        font-size: 44px;
        font-weight: 800;
        letter-spacing: -1px;
        margin-bottom: 8px;
        color: #f5fff8;
    }

    .hero-title span {
        color: #73f59a;
    }

    .hero-subtitle {
        font-size: 18px;
        color: #b7d4c2;
        margin-bottom: 22px;
    }

    .badge-row {
        display: flex;
        flex-wrap: wrap;
        gap: 10px;
    }

    .badge {
        padding: 8px 14px;
        border-radius: 999px;
        background: rgba(105, 240, 145, 0.09);
        border: 1px solid rgba(105, 240, 145, 0.22);
        color: #bafacb;
        font-size: 13px;
        font-weight: 600;
    }

    /* Section headings */
    .section-title {
        font-size: 28px;
        font-weight: 750;
        margin-top: 18px;
        margin-bottom: 5px;
        color: #f5fff8;
    }

    .section-subtitle {
        color: #9fc0aa;
        font-size: 15px;
        margin-bottom: 20px;
    }

    /* Cards */
    .card {
        background: rgba(12, 32, 25, 0.90);
        border: 1px solid rgba(105, 240, 145, 0.16);
        border-radius: 22px;
        padding: 24px;
        box-shadow: 0 14px 40px rgba(0,0,0,0.22);
        margin-bottom: 20px;
    }

    .card-title {
        font-size: 20px;
        font-weight: 700;
        color: #ecfff1;
        margin-bottom: 14px;
    }

    /* Diagnosis */
    .diagnosis-card {
        background:
            linear-gradient(
                135deg,
                rgba(17, 72, 45, 0.90),
                rgba(10, 31, 24, 0.95)
            );
        border: 1px solid rgba(100, 240, 140, 0.28);
        border-radius: 24px;
        padding: 28px;
        min-height: 230px;
    }

    .diagnosis-label {
        font-size: 12px;
        font-weight: 700;
        color: #8fd8a6;
        letter-spacing: 1.5px;
        margin-bottom: 12px;
    }

    .diagnosis-name {
        font-size: 30px;
        font-weight: 800;
        color: #ffffff;
        margin-bottom: 14px;
    }

    .confidence-number {
        font-size: 42px;
        font-weight: 850;
        color: #75f39c;
    }

    .confidence-label {
        color: #9fc0aa;
        font-size: 13px;
        margin-top: -5px;
    }

    /* Prediction rows */
    .prediction-row {
        padding: 15px 0;
        border-bottom: 1px solid rgba(255,255,255,0.07);
    }

    .prediction-row:last-child {
        border-bottom: none;
    }

    .prediction-name {
        font-weight: 650;
        color: #eaffef;
        font-size: 15px;
    }

    .prediction-percent {
        color: #75f39c;
        font-weight: 800;
        font-size: 16px;
    }

    /* Explanation */
    .explanation-item {
        background: rgba(22, 49, 37, 0.70);
        border: 1px solid rgba(105, 240, 145, 0.12);
        border-radius: 14px;
        padding: 14px 16px;
        margin-bottom: 10px;
        color: #d8eee0;
        font-size: 14px;
        line-height: 1.55;
    }

    .explanation-number {
        color: #73f59a;
        font-weight: 800;
    }

    /* Info boxes */
    .info-box {
        padding: 16px 18px;
        border-radius: 15px;
        background: rgba(16, 52, 36, 0.65);
        border: 1px solid rgba(100, 230, 140, 0.15);
        color: #c9e8d2;
        line-height: 1.5;
        margin-top: 10px;
    }

    /* Image labels */
    .image-label {
        font-size: 17px;
        font-weight: 700;
        color: #eaffef;
        margin-bottom: 10px;
    }

    /* Footer */
    .footer {
        text-align: center;
        color: #6f8e79;
        font-size: 13px;
        padding-top: 30px;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# HEADER
# ============================================================

st.markdown(
    """
    <div class="hero">

        <div class="hero-title">
            🌿 PlantDoc <span>AI</span>
        </div>

        <div class="hero-subtitle">
            AI-Based Plant Disease Detection & Explainable Artificial Intelligence
        </div>

        <div class="badge-row">
            <div class="badge">🧠 Deep Learning</div>
            <div class="badge">🔬 Explainable AI</div>
            <div class="badge">🌱 Plant Health Analysis</div>
            <div class="badge">🎯 SHAP Visualization</div>
        </div>

    </div>
    """,
    unsafe_allow_html=True
)


# ============================================================
# MODEL LOADING
# ============================================================

@st.cache_resource
def load_ai_model():

    model = load_model(
        "models/plantdoc_model.keras",
        compile=False
    )

    with open("models/class_names.json", "r") as f:
        class_names = json.load(f)

    return model, class_names


try:

    model, class_names = load_ai_model()

except Exception as e:

    st.error("❌ AI model could not be loaded.")

    st.code(str(e))

    st.stop()


# ============================================================
# IMAGE PREPROCESSING
# ============================================================

IMG_SIZE = 224


def preprocess_image(image):

    image_rgb = image.convert("RGB")

    resized = image_rgb.resize(
        (IMG_SIZE, IMG_SIZE)
    )

    array = np.array(resized).astype(np.float32)

    array = array / 255.0

    array = np.expand_dims(
        array,
        axis=0
    )

    return array


# ============================================================
# CLEAN CLASS NAME
# ============================================================

def clean_class_name(name):

    name = str(name)

    name = name.replace("___", " → ")

    name = name.replace("__", " ")

    name = name.replace("_", " ")

    return name.strip()


# ============================================================
# SHAP HEATMAP
# ============================================================

@st.cache_data(show_spinner=False)
def generate_explanation(image_array, predicted_index):

    try:

        # Small background sample
        background = image_array.copy()

        masker = shap.maskers.Image(
            "blur(32,32)",
            image_array.shape[1:]
        )

        explainer = shap.Explainer(
            model,
            masker,
            output_names=class_names
        )

        shap_values = explainer(
            image_array,
            max_evals=150,
            outputs=[predicted_index]
        )

        values = shap_values.values

        # Handle SHAP output dimensions
        if values.ndim == 5:
            heat = values[0, :, :, :, 0]
        elif values.ndim == 4:
            heat = values[0]
        else:
            return None

        # Convert RGB channels into one importance map
        if heat.ndim == 3:
            heat = np.mean(
                np.abs(heat),
                axis=-1
            )

        heat = np.nan_to_num(
            heat,
            nan=0.0,
            posinf=0.0,
            neginf=0.0
        )

        # Normalize
        heat = np.abs(heat)

        if np.max(heat) > 0:

            heat = heat / np.max(heat)

        heat = (heat * 255).astype(
            np.uint8
        )

        # Smooth
        heat = cv2.GaussianBlur(
            heat,
            (0, 0),
            sigmaX=7
        )

        # Resize
        heat = cv2.resize(
            heat,
            (IMG_SIZE, IMG_SIZE)
        )

        # Threshold to focus on strongest regions
        threshold = np.percentile(
            heat,
            65
        )

        mask = heat >= threshold

        # Create heatmap
        color_map = cv2.applyColorMap(
            heat,
            cv2.COLORMAP_JET
        )

        color_map = cv2.cvtColor(
            color_map,
            cv2.COLOR_BGR2RGB
        )

        original = (
            image_array[0] * 255
        ).astype(np.uint8)

        # Keep only important regions
        highlighted = original.copy()

        highlighted[mask] = (
            0.45 * original[mask]
            + 0.55 * color_map[mask]
        ).astype(np.uint8)

        # Create outline around important regions
        mask_uint8 = (
            mask.astype(np.uint8) * 255
        )

        contours, _ = cv2.findContours(
            mask_uint8,
            cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE
        )

        cv2.drawContours(
            highlighted,
            contours,
            -1,
            (255, 255, 255),
            1
        )

        return highlighted

    except Exception:

        return None


# ============================================================
# UPLOAD SECTION
# ============================================================

st.markdown(
    '<div class="section-title">🔬 Analyze Your Plant Leaf</div>',
    unsafe_allow_html=True
)

st.markdown(
    """
    <div class="section-subtitle">
        Upload a clear leaf image and let PlantDoc AI identify
        the most likely plant condition and explain the visual regions
        that influenced the prediction.
    </div>
    """,
    unsafe_allow_html=True
)


uploaded_file = st.file_uploader(
    "📤 Upload Leaf Image",
    type=["jpg", "jpeg", "png"],
    help="Upload a clear JPG or PNG leaf image."
)


# ============================================================
# ANALYSIS
# ============================================================

if uploaded_file is None:

    st.info(
        "👆 Upload a leaf image above to start the AI analysis."
    )

    st.markdown(
        """
        <div class="info-box">
            💡 <b>Tip:</b> Use a clear image where the leaf is
            clearly visible. Better image quality generally gives
            better visual explanations.
        </div>
        """,
        unsafe_allow_html=True
    )

else:

    # Load image
    image = Image.open(
        uploaded_file
    ).convert("RGB")

    # Preprocess
    input_array = preprocess_image(
        image
    )

    # Prediction
    with st.spinner(
        "🧠 PlantDoc AI is analyzing the leaf..."
    ):

        predictions = model.predict(
            input_array,
            verbose=0
        )[0]

    # Convert predictions to probabilities
    predictions = np.asarray(
        predictions
    ).astype(float)

    # Softmax if required
    if (
        np.max(predictions) > 1.0
        or
        np.sum(predictions) < 0.9
        or
        np.sum(predictions) > 1.1
    ):

        exp_values = np.exp(
            predictions - np.max(predictions)
        )

        predictions = (
            exp_values
            / np.sum(exp_values)
        )

    # Top 3
    top_indices = np.argsort(
        predictions
    )[::-1][:3]

    predicted_index = int(
        top_indices[0]
    )

    predicted_name = clean_class_name(
        class_names[predicted_index]
    )

    confidence = float(
        predictions[predicted_index] * 100
    )


    # ========================================================
    # IMAGE SECTION
    # ========================================================

    st.markdown(
        '<div class="section-title">🖼️ Visual Analysis</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <div class="section-subtitle">
            Compare the original leaf with the AI-generated
            important-region visualization.
        </div>
        """,
        unsafe_allow_html=True
    )


    # Generate explanation image
    with st.spinner(
        "🔎 Generating infected/important area visualization..."
    ):

        explanation_image = generate_explanation(
            input_array,
            predicted_index
        )


    col1, col2 = st.columns(
        2,
        gap="large"
    )


    with col1:

        st.markdown(
            '<div class="image-label">🌿 Original Leaf</div>',
            unsafe_allow_html=True
        )

        st.image(
            image,
            use_container_width=True
        )


    with col2:

        st.markdown(
            '<div class="image-label">🔥 AI Important Area Map</div>',
            unsafe_allow_html=True
        )

        if explanation_image is not None:

            st.image(
                explanation_image,
                use_container_width=True
            )

            st.caption(
                "Red/yellow regions represent areas that contributed "
                "more strongly to the model's visual decision."
            )

        else:

            st.warning(
                "⚠️ Visual explanation could not be generated for this image."
            )


    # ========================================================
    # DIAGNOSIS
    # ========================================================

    st.markdown(
        '<div class="section-title">🧠 AI Diagnosis</div>',
        unsafe_allow_html=True
    )

    diagnosis_col, prediction_col = st.columns(
        [1.15, 0.85],
        gap="large"
    )


    with diagnosis_col:

        st.markdown(
            f"""
            <div class="diagnosis-card">

                <div class="diagnosis-label">
                    MOST LIKELY CONDITION
                </div>

                <div class="diagnosis-name">
                    {predicted_name}
                </div>

                <div class="confidence-number">
                    {confidence:.2f}%
                </div>

                <div class="confidence-label">
                    Model confidence score
                </div>

            </div>
            """,
            unsafe_allow_html=True
        )


    with prediction_col:

        st.markdown(
            """
            <div class="card">
                <div class="card-title">
                    🏆 Top 3 Predictions
                </div>
            """,
            unsafe_allow_html=True
        )

        for rank, idx in enumerate(
            top_indices,
            start=1
        ):

            name = clean_class_name(
                class_names[int(idx)]
            )

            score = (
                float(predictions[int(idx)])
                * 100
            )

            st.markdown(
                f"""
                <div class="prediction-row">

                    <div class="prediction-name">
                        #{rank} &nbsp; {name}
                    </div>

                    <div class="prediction-percent">
                        {score:.2f}%
                    </div>

                </div>
                """,
                unsafe_allow_html=True
            )

        st.markdown(
            "</div>",
            unsafe_allow_html=True
        )


    # ========================================================
    # XAI EXPLANATION
    # ========================================================

    st.markdown(
        '<div class="section-title">🔍 Explainable AI</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <div class="section-subtitle">
            SHAP highlights the visual regions that were most influential
            in the AI prediction.
        </div>
        """,
        unsafe_allow_html=True
    )


    # Explanation points
    explanation_points = [

        f"The AI classified the leaf most strongly as "
        f"<b>{predicted_name}</b>.",

        "Highlighted red and yellow regions represent "
        "visually important areas used during the prediction.",

        "The model focuses on visible leaf characteristics "
        "such as spots, discoloration, texture and damaged regions.",

        "Green or less-highlighted areas contributed relatively "
        "less to the final visual decision.",

        f"The model's estimated confidence for the top prediction "
        f"is <b>{confidence:.2f}%</b>.",

        "The highlighted image is an AI explanation map, "
        "not a medical-style measurement of the exact infected area."

    ]


    for i, point in enumerate(
        explanation_points,
        start=1
    ):

        st.markdown(
            f"""
            <div class="explanation-item">
                <span class="explanation-number">
                    {i}.
                </span>
                &nbsp;
                {point}
            </div>
            """,
            unsafe_allow_html=True
        )


    # ========================================================
    # DISCLAIMER
    # ========================================================

    st.markdown(
        """
        <div class="info-box">
            ⚠️ <b>Important:</b> PlantDoc AI provides an AI-based
            visual classification and explanation. The highlighted
            regions indicate model attention and should not be treated
            as an exact biological measurement of disease severity.
        </div>
        """,
        unsafe_allow_html=True
    )


# ============================================================
# FOOTER
# ============================================================

st.markdown(
    """
    <div class="footer">
        🌿 PlantDoc AI &nbsp;•&nbsp;
        Deep Learning + Explainable AI
    </div>
    """,
    unsafe_allow_html=True
)