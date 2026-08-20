import streamlit as st
import json
import numpy as np
from PIL import Image
from tensorflow.keras.models import load_model
import shap
import cv2
import matplotlib.pyplot as plt


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="PlantDoc AI | Plant Disease Detection",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="collapsed"
)


# =========================================================
# CUSTOM CSS
# =========================================================

st.markdown("""
<style>

@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

.stApp {
    background:
        radial-gradient(circle at 10% 10%, rgba(70, 180, 100, 0.10), transparent 25%),
        radial-gradient(circle at 90% 20%, rgba(50, 130, 255, 0.08), transparent 25%),
        linear-gradient(135deg, #07110c 0%, #0b1110 45%, #07100b 100%);
}

/* Remove default top padding */
.block-container {
    padding-top: 2rem;
    padding-bottom: 3rem;
    max-width: 1400px;
}

/* Main Header */
.hero {
    padding: 30px 35px;
    border-radius: 25px;
    background:
        linear-gradient(135deg,
        rgba(24, 53, 35, 0.95),
        rgba(11, 24, 17, 0.92));
    border: 1px solid rgba(100, 220, 130, 0.20);
    box-shadow: 0 15px 50px rgba(0,0,0,0.35);
    margin-bottom: 25px;
}

.logo-title {
    font-size: 42px;
    font-weight: 800;
    color: #f4fff5;
    margin: 0;
}

.logo-title span {
    color: #73e695;
}

.subtitle {
    color: #a8b9ae;
    font-size: 17px;
    margin-top: 8px;
}

.badge {
    display: inline-block;
    padding: 7px 13px;
    border-radius: 20px;
    background: rgba(93, 225, 126, 0.12);
    border: 1px solid rgba(93, 225, 126, 0.25);
    color: #7bea98;
    font-size: 13px;
    font-weight: 600;
    margin-top: 15px;
}

/* Section titles */

.section-title {
    font-size: 25px;
    font-weight: 750;
    color: #f1fff4;
    margin-top: 25px;
    margin-bottom: 15px;
}

.section-subtitle {
    color: #91a49a;
    font-size: 14px;
    margin-top: -8px;
    margin-bottom: 18px;
}

/* Cards */

.card {
    background: rgba(17, 27, 21, 0.85);
    border: 1px solid rgba(125, 220, 145, 0.14);
    border-radius: 20px;
    padding: 22px;
    box-shadow: 0 12px 35px rgba(0,0,0,0.25);
    height: 100%;
}

.prediction-card {
    background: linear-gradient(
        135deg,
        rgba(31, 72, 45, 0.70),
        rgba(14, 31, 21, 0.90)
    );
    border: 1px solid rgba(105, 230, 130, 0.25);
    border-radius: 22px;
    padding: 25px;
    box-shadow: 0 15px 40px rgba(0,0,0,0.30);
}

.prediction-title {
    color: #91f3a8;
    font-size: 14px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 1px;
}

.prediction-name {
    color: #ffffff;
    font-size: 28px;
    font-weight: 800;
    margin-top: 8px;
}

.confidence {
    font-size: 36px;
    font-weight: 800;
    color: #7bea98;
}

.confidence-label {
    color: #8ea296;
    font-size: 13px;
}

/* Top prediction rows */

.top-row {
    background: rgba(255,255,255,0.025);
    border: 1px solid rgba(255,255,255,0.06);
    padding: 15px;
    border-radius: 15px;
    margin-bottom: 10px;
}

/* XAI */

.xai-card {
    background: linear-gradient(
        135deg,
        rgba(18, 35, 48, 0.85),
        rgba(12, 25, 20, 0.90)
    );
    border: 1px solid rgba(100, 190, 255, 0.16);
    border-radius: 20px;
    padding: 25px;
}

.xai-point {
    padding: 12px 15px;
    margin: 8px 0;
    border-radius: 12px;
    background: rgba(255,255,255,0.035);
    border-left: 3px solid #6fe58d;
    color: #d5e5da;
    font-size: 14px;
}

/* Info boxes */

.info-box {
    padding: 18px;
    border-radius: 15px;
    background: rgba(60, 150, 255, 0.08);
    border: 1px solid rgba(60, 150, 255, 0.18);
    color: #bcdcff;
}

/* Footer */

.footer {
    margin-top: 50px;
    padding: 20px;
    text-align: center;
    color: #65766b;
    border-top: 1px solid rgba(255,255,255,0.06);
    font-size: 13px;
}

/* Upload area */

[data-testid="stFileUploader"] {
    background: rgba(18, 30, 23, 0.85);
    border: 1px dashed rgba(110, 225, 135, 0.35);
    border-radius: 20px;
    padding: 10px;
}

/* Buttons */

.stButton > button {
    width: 100%;
    border-radius: 12px;
    border: 1px solid rgba(110, 225, 135, 0.3);
    background: linear-gradient(135deg, #1e6d3a, #248b4a);
    color: white;
    font-weight: 700;
    padding: 12px;
}

.stButton > button:hover {
    border-color: #73e695;
    box-shadow: 0 0 20px rgba(80,220,110,0.2);
}

/* Hide Streamlit menu */
#MainMenu {
    visibility: hidden;
}

footer {
    visibility: hidden;
}

</style>
""", unsafe_allow_html=True)


# =========================================================
# LOAD MODEL
# =========================================================

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

    st.error("❌ Model could not be loaded.")
    st.code(str(e))
    st.stop()


# =========================================================
# IMAGE PREPROCESSING
# =========================================================

def preprocess_image(image):

    image = image.convert("RGB")

    resized = image.resize((224, 224))

    arr = np.array(resized).astype("float32") / 255.0

    arr = np.expand_dims(arr, axis=0)

    return arr


# =========================================================
# CLEAN CLASS NAME
# =========================================================

def clean_class_name(name):

    return (
        name.replace("___", " → ")
            .replace("_", " ")
            .replace("(including sour)", "(including sour)")
    )


# =========================================================
# SHAP EXPLANATION
# =========================================================

@st.cache_data(show_spinner=False)
def generate_shap_explanation(image_array, predicted_index):

    masker = shap.maskers.Image(
        "blur(32,32)",
        image_array[0].shape
    )

    explainer = shap.Explainer(
        model,
        masker,
        output_names=class_names
    )

    shap_values = explainer(
        image_array,
        max_evals=100,
        batch_size=1
    )

    values = shap_values.values

    # -----------------------------------------------------
    # Get SHAP values for predicted class
    # -----------------------------------------------------

    if values.ndim == 5:

        class_shap = values[
            0,
            :,
            :,
            :,
            predicted_index
        ]

    else:

        class_shap = values[0]

    # -----------------------------------------------------
    # Convert RGB SHAP to intensity map
    # -----------------------------------------------------

    heatmap = np.mean(
        np.abs(class_shap),
        axis=-1
    )

    heatmap = np.nan_to_num(heatmap)

    if heatmap.max() > 0:

        heatmap = heatmap / heatmap.max()

    # Smooth heatmap
    heatmap = cv2.GaussianBlur(
        heatmap.astype(np.float32),
        (0, 0),
        3
    )

    # -----------------------------------------------------
    # Resize to original image size
    # -----------------------------------------------------

    heatmap = cv2.resize(
        heatmap,
        (224, 224)
    )

    # -----------------------------------------------------
    # Create colored SHAP heatmap
    # -----------------------------------------------------

    heat_uint8 = np.uint8(
        heatmap * 255
    )

    colored_heatmap = cv2.applyColorMap(
        heat_uint8,
        cv2.COLORMAP_JET
    )

    colored_heatmap = cv2.cvtColor(
        colored_heatmap,
        cv2.COLOR_BGR2RGB
    )

    # -----------------------------------------------------
    # Original image
    # -----------------------------------------------------

    original = np.array(
        Image.fromarray(
            np.uint8(image_array[0] * 255)
        ).resize((224, 224))
    )

    # -----------------------------------------------------
    # Overlay
    # -----------------------------------------------------

    overlay = cv2.addWeighted(
        original,
        0.55,
        colored_heatmap,
        0.45,
        0
    )

    # -----------------------------------------------------
    # IMPORTANT REGION MASK
    # -----------------------------------------------------

    threshold = np.percentile(
        heatmap,
        85
    )

    mask = heatmap >= threshold

    # Clean mask
    mask_uint8 = (
        mask.astype(np.uint8) * 255
    )

    kernel = np.ones(
        (5, 5),
        np.uint8
    )

    mask_uint8 = cv2.morphologyEx(
        mask_uint8,
        cv2.MORPH_OPEN,
        kernel
    )

    mask_uint8 = cv2.morphologyEx(
        mask_uint8,
        cv2.MORPH_CLOSE,
        kernel
    )

    # -----------------------------------------------------
    # Highlight important regions
    # -----------------------------------------------------

    highlighted = original.copy()

    highlighted[mask_uint8 > 0] = (
        highlighted[mask_uint8 > 0] * 0.35
        + np.array([255, 60, 60]) * 0.65
    ).astype(np.uint8)

    # Add contours
    contours, _ = cv2.findContours(
        mask_uint8,
        cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE
    )

    highlighted = cv2.drawContours(
        highlighted,
        contours,
        -1,
        (255, 40, 40),
        2
    )

    return overlay, highlighted, heatmap


# =========================================================
# HEADER
# =========================================================

st.markdown("""
<div class="hero">

    <div class="logo-title">
        🌿 PlantDoc <span>AI</span>
    </div>

    <div class="subtitle">
        AI-Based Plant Disease Detection & Explainable Artificial Intelligence
    </div>

    <div class="badge">
        ⚡ Deep Learning &nbsp; • &nbsp;
        🔍 SHAP Explainability &nbsp; • &nbsp;
        🌱 Plant Health Analysis
    </div>

</div>
""", unsafe_allow_html=True)


# =========================================================
# INTRO
# =========================================================

st.markdown("""
<div class="section-title">
    🔬 Analyze Your Plant Leaf
</div>

<div class="section-subtitle">
    Upload a clear leaf image and let PlantDoc AI identify the most likely
    plant condition and explain which visual regions influenced the prediction.
</div>
""", unsafe_allow_html=True)


# =========================================================
# UPLOAD
# =========================================================

uploaded_file = st.file_uploader(
    "📤 Upload Leaf Image",
    type=["jpg", "jpeg", "png"],
    help="Upload a clear image of a single plant leaf."
)


# =========================================================
# NO IMAGE
# =========================================================

if uploaded_file is None:

    st.markdown("""
    <div class="info-box">
        👆 <b>Upload a leaf image above</b> to start the AI analysis.
        <br><br>
        For best results, use a clear image where the leaf is visible properly.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="footer">
        🌿 PlantDoc AI &nbsp; | &nbsp;
        AI-Based Plant Disease Detection &nbsp; | &nbsp;
        Explainable AI
    </div>
    """, unsafe_allow_html=True)

    st.stop()


# =========================================================
# READ IMAGE
# =========================================================

try:

    image = Image.open(uploaded_file).convert("RGB")

except Exception:

    st.error("Unable to read this image.")
    st.stop()


# =========================================================
# PREPROCESS
# =========================================================

img_array = preprocess_image(image)


# =========================================================
# ORIGINAL IMAGE
# =========================================================

st.markdown("""
<div class="section-title">
    🖼️ Uploaded Leaf
</div>
""", unsafe_allow_html=True)

col_img, col_info = st.columns(
    [1.5, 1]
)

with col_img:

    st.image(
        image,
        use_container_width=True
    )

with col_info:

    st.markdown("""
    <div class="card">

    <h3 style="color:#8df2a5;">
    📋 Image Information
    </h3>

    <p style="color:#aabbb0;">
    <b>File:</b> {}</p>

    <p style="color:#aabbb0;">
    <b>Original Size:</b> {} × {} px</p>

    <p style="color:#aabbb0;">
    <b>Model Input:</b> 224 × 224 px</p>

    <p style="color:#aabbb0;">
    <b>Analysis:</b> RGB Leaf Image</p>

    </div>
    """.format(
        uploaded_file.name,
        image.width,
        image.height
    ), unsafe_allow_html=True)


# =========================================================
# AI PREDICTION
# =========================================================

with st.spinner("🧠 PlantDoc AI is analyzing the leaf..."):

    predictions = model.predict(
        img_array,
        verbose=0
    )[0]


# =========================================================
# TOP 3
# =========================================================

top_indices = np.argsort(
    predictions
)[::-1][:3]

top_predictions = [
    (
        class_names[i],
        float(predictions[i])
    )
    for i in top_indices
]


predicted_index = top_indices[0]

predicted_class = class_names[
    predicted_index
]

predicted_confidence = float(
    predictions[predicted_index]
)


# =========================================================
# MAIN RESULT
# =========================================================

st.markdown("""
<div class="section-title">
    🧠 AI Diagnosis
</div>
""", unsafe_allow_html=True)


result_col, top_col = st.columns(
    [1.2, 1]
)


# ---------------------------------------------------------
# Main prediction
# ---------------------------------------------------------

with result_col:

    st.markdown(f"""
    <div class="prediction-card">

        <div class="prediction-title">
            MOST LIKELY CONDITION
        </div>

        <div class="prediction-name">
            {clean_class_name(predicted_class)}
        </div>

        <br>

        <div class="confidence">
            {predicted_confidence * 100:.2f}%
        </div>

        <div class="confidence-label">
            Model confidence score
        </div>

    </div>
    """, unsafe_allow_html=True)


# ---------------------------------------------------------
# Top 3
# ---------------------------------------------------------

with top_col:

    st.markdown("""
    <div class="card">

    <h3 style="color:#8df2a5;">
    🏆 Top 3 Predictions
    </h3>
    """, unsafe_allow_html=True)

    for rank, (name, prob) in enumerate(
        top_predictions,
        start=1
    ):

        st.markdown(
            f"""
            <div class="top-row">

                <div style="color:#dcebe0;font-weight:600;">
                    #{rank} &nbsp; {clean_class_name(name)}
                </div>

                <div style="
                    color:#78e997;
                    font-weight:700;
                    margin-top:5px;">
                    {prob * 100:.2f}%
                </div>

            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown(
        "</div>",
        unsafe_allow_html=True
    )


# =========================================================
# SHAP ANALYSIS
# =========================================================

st.markdown("""
<div class="section-title">
    🔍 Explainable AI — Why did the model predict this?
</div>

<div class="section-subtitle">
    SHAP highlights the image regions that contributed most strongly
    to the model's prediction.
</div>
""", unsafe_allow_html=True)


with st.spinner(
    "🔬 Generating AI explanation and important-region map..."
):

    try:

        overlay, highlighted, heatmap = (
            generate_shap_explanation(
                img_array,
                int(predicted_index)
            )
        )

    except Exception as e:

        st.error(
            "SHAP explanation could not be generated."
        )

        st.code(str(e))

        overlay = None
        highlighted = None


# =========================================================
# XAI IMAGES
# =========================================================

if overlay is not None:

    image_col1, image_col2 = st.columns(
        2
    )

    with image_col1:

        st.markdown("""
        <div class="card">

        <h3 style="color:#8df2a5;">
        🌈 AI Attention Map
        </h3>

        <p style="color:#8ea296;font-size:13px;">
        Red/yellow regions indicate stronger model influence.
        </p>

        </div>
        """, unsafe_allow_html=True)

        st.image(
            overlay,
            use_container_width=True
        )

    with image_col2:

        st.markdown("""
        <div class="card">

        <h3 style="color:#ff8585;">
        🎯 Important / Suspected Region
        </h3>

        <p style="color:#8ea296;font-size:13px;">
        Red outlined regions show areas that strongly influenced
        the model's decision.
        </p>

        </div>
        """, unsafe_allow_html=True)

        st.image(
            highlighted,
            use_container_width=True
        )


# =========================================================
# EXPLANATION POINTS
# =========================================================

st.markdown("""
<div class="section-title">
    💡 AI Explanation
</div>
""", unsafe_allow_html=True)


explanation_points = [

    f"The model identified <b>{clean_class_name(predicted_class)}</b> as the most likely class.",

    f"The model assigned a confidence score of <b>{predicted_confidence * 100:.2f}%</b> to this prediction.",

    "The SHAP attention map shows which visual regions contributed most strongly to the prediction.",

    "Red and yellow areas represent regions with stronger influence on the model's decision.",

    "The highlighted-region image marks the most influential areas detected by the XAI analysis.",

    "These highlighted areas should be interpreted as <b>model-important regions</b>, not as a medically verified disease boundary.",

    "The explanation makes the AI system more transparent by showing why the model reached its prediction."
]


st.markdown(
    '<div class="xai-card">',
    unsafe_allow_html=True
)

for i, point in enumerate(
    explanation_points,
    start=1
):

    st.markdown(
        f"""
        <div class="xai-point">
            <b>{i}.</b> {point}
        </div>
        """,
        unsafe_allow_html=True
    )

st.markdown(
    '</div>',
    unsafe_allow_html=True
)


# =========================================================
# COLOR LEGEND
# =========================================================

st.markdown("""
<div class="section-title">
    🎨 How to Read the AI Map
</div>
""", unsafe_allow_html=True)


legend1, legend2, legend3 = st.columns(3)


with legend1:

    st.markdown("""
    <div class="card">
    <h3 style="color:#ff4b4b;">🔴 Red</h3>
    <p style="color:#aabbb0;">
    Strong model attention / highly influential region.
    </p>
    </div>
    """, unsafe_allow_html=True)


with legend2:

    st.markdown("""
    <div class="card">
    <h3 style="color:#ffd84d;">🟡 Yellow</h3>
    <p style="color:#aabbb0;">
    Medium-to-high model attention.
    </p>
    </div>
    """, unsafe_allow_html=True)


with legend3:

    st.markdown("""
    <div class="card">
    <h3 style="color:#4285ff;">🔵 Blue</h3>
    <p style="color:#aabbb0;">
    Lower contribution to the selected prediction.
    </p>
    </div>
    """, unsafe_allow_html=True)


# =========================================================
# IMPORTANT DISCLAIMER
# =========================================================

st.markdown("""
<br>

<div class="info-box">

⚠️ <b>Important:</b>

The highlighted region represents areas that influenced the
AI model's prediction. It should not be considered a clinically
verified disease boundary or a replacement for expert agricultural
diagnosis.

</div>
""", unsafe_allow_html=True)


# =========================================================
# FOOTER
# =========================================================

st.markdown("""
<div class="footer">

🌿 <b>PlantDoc AI</b>

<br><br>

AI-Based Plant Disease Detection • Deep Learning • SHAP Explainable AI

<br><br>

Major Project — CSE / AI & ML

</div>
""", unsafe_allow_html=True)