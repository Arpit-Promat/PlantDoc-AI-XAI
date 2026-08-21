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

st.markdown("""
<style>

    /* ---------- GLOBAL ---------- */

    .stApp {
        background:
            radial-gradient(circle at 85% 5%, rgba(0, 80, 70, 0.25), transparent 30%),
            radial-gradient(circle at 10% 40%, rgba(0, 55, 45, 0.18), transparent 35%),
            #020b0b;
        color: #e8fff2;
    }

    .main .block-container {
        max-width: 1250px;
        padding-top: 2rem;
        padding-bottom: 2rem;
    }

    h1, h2, h3 {
        color: #f2fff7 !important;
    }

    p, label, .stMarkdown {
        color: #c7d9d2;
    }


    /* ---------- HEADER ---------- */

    .hero-title {
        font-size: 48px;
        font-weight: 800;
        letter-spacing: -1px;
        margin-bottom: 5px;
        color: #f5fff9;
    }

    .hero-title span {
        color: #39e56f;
    }

    .hero-subtitle {
        font-size: 18px;
        color: #d3e8df;
        margin-bottom: 18px;
    }

    .badge-row {
        display: flex;
        gap: 10px;
        flex-wrap: wrap;
    }

    .badge {
        padding: 8px 15px;
        border-radius: 30px;
        background: rgba(10, 75, 60, 0.45);
        border: 1px solid rgba(45, 220, 120, 0.35);
        color: #caffdf;
        font-size: 14px;
        font-weight: 600;
    }


    /* ---------- CARDS ---------- */

    div[data-testid="stVerticalBlockBorderWrapper"] {
        border-radius: 16px !important;
        border: 1px solid rgba(40, 190, 110, 0.22) !important;
        background: rgba(5, 30, 27, 0.65) !important;
    }

    .section-title {
        color: #64ee83;
        font-size: 23px;
        font-weight: 750;
        margin-bottom: 4px;
    }

    .section-subtitle {
        color: #9eb8ad;
        font-size: 14px;
        margin-bottom: 15px;
    }


    /* ---------- UPLOAD ---------- */

    div[data-testid="stFileUploader"] {
        background: rgba(5, 40, 34, 0.55);
        border: 1px dashed rgba(53, 222, 113, 0.55);
        border-radius: 14px;
        padding: 8px;
    }

    div[data-testid="stFileUploader"] section {
        background: transparent !important;
    }

    div[data-testid="stFileUploaderDropzone"] {
        background: transparent !important;
    }


    /* ---------- IMAGE ---------- */

    div[data-testid="stImage"] img {
        border-radius: 12px;
    }


    /* ---------- METRIC ---------- */

    div[data-testid="stMetric"] {
        background: rgba(4, 38, 32, 0.7);
        border: 1px solid rgba(50, 200, 110, 0.22);
        border-radius: 14px;
        padding: 15px;
    }

    div[data-testid="stMetricLabel"] {
        color: #9eb8ad !important;
    }

    div[data-testid="stMetricValue"] {
        color: #55ed78 !important;
    }


    /* ---------- PROGRESS ---------- */

    div[data-testid="stProgressBar"] > div {
        background-color: rgba(70, 100, 90, 0.25);
        border-radius: 20px;
    }

    div[data-testid="stProgressBar"] > div > div {
        background: linear-gradient(
            90deg,
            #20c969,
            #61f184
        );
        border-radius: 20px;
    }


    /* ---------- SUCCESS / WARNING ---------- */

    div[data-testid="stAlert"] {
        border-radius: 12px;
    }


    /* ---------- FOOTER ---------- */

    .footer {
        text-align: center;
        padding: 20px 0 5px 0;
        color: #718d82;
        font-size: 13px;
    }

    .footer strong {
        color: #4ee978;
    }

</style>
""", unsafe_allow_html=True)


# ============================================================
# HEADER
# ============================================================

st.markdown("""
<div class="hero-title">🌿 PlantDoc <span>AI</span></div>

<div class="hero-subtitle">
AI-Based Plant Disease Detection & Explainable Artificial Intelligence
</div>

<div class="badge-row">
    <div class="badge">⚡ Deep Learning</div>
    <div class="badge">🔍 SHAP Explainability</div>
    <div class="badge">🌱 Plant Health Analysis</div>
</div>
""", unsafe_allow_html=True)

st.write("")


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
    st.error(str(e))
    st.stop()


# ============================================================
# CONSTANTS
# ============================================================

IMG_SIZE = 224


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def clean_class_name(name):

    name = str(name)

    name = name.replace("___", " → ")
    name = name.replace("__", " ")
    name = name.replace("_", " ")

    return name.strip()


def preprocess_image(image):

    image = image.convert("RGB")

    resized = image.resize(
        (IMG_SIZE, IMG_SIZE)
    )

    array = np.array(
        resized
    ).astype(np.float32)

    array = array / 255.0

    array = np.expand_dims(
        array,
        axis=0
    )

    return array


def get_predictions(image_array):

    predictions = model.predict(
        image_array,
        verbose=0
    )[0]

    predictions = np.asarray(
        predictions
    ).astype(np.float64)

    if (
        np.any(predictions < 0)
        or
        np.max(predictions) > 1.0
        or
        not np.isclose(
            np.sum(predictions),
            1.0,
            atol=0.05
        )
    ):

        exp_values = np.exp(
            predictions - np.max(predictions)
        )

        predictions = (
            exp_values /
            np.sum(exp_values)
        )

    else:

        total = np.sum(predictions)

        if total > 0:

            predictions = (
                predictions /
                total
            )

    top_indices = np.argsort(
        predictions
    )[::-1][:3]

    return predictions, top_indices


# ============================================================
# SHAP EXPLANATION
# ============================================================

def generate_shap_heatmap(
    image_array,
    predicted_index
):

    try:

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
            max_evals=100
        )

        values = shap_values.values

        if values.ndim == 5:

            if predicted_index < values.shape[-1]:

                heat = values[
                    0,
                    :,
                    :,
                    :,
                    predicted_index
                ]

            else:

                heat = values[0]

        elif values.ndim == 4:

            heat = values[0]

        else:

            return None

        if heat.ndim == 3:

            heat = np.mean(
                np.abs(heat),
                axis=-1
            )

        heat = np.abs(heat)

        heat = np.nan_to_num(
            heat,
            nan=0.0,
            posinf=0.0,
            neginf=0.0
        )

        if np.max(heat) <= 0:

            return None

        heat = (
            heat /
            np.max(heat)
        )

        heat = (
            heat * 255
        ).astype(np.uint8)

        heat = cv2.resize(
            heat,
            (IMG_SIZE, IMG_SIZE)
        )

        heat = cv2.GaussianBlur(
            heat,
            (0, 0),
            5
        )

        color_heatmap = cv2.applyColorMap(
            heat,
            cv2.COLORMAP_JET
        )

        color_heatmap = cv2.cvtColor(
            color_heatmap,
            cv2.COLOR_BGR2RGB
        )

        original = (
            image_array[0] * 255
        ).astype(np.uint8)

        alpha = (
            heat.astype(np.float32) /
            255.0
        )

        alpha = (
            alpha[..., None] *
            0.65
        )

        result = (
            original * (1 - alpha)
            +
            color_heatmap * alpha
        )

        result = np.clip(
            result,
            0,
            255
        ).astype(np.uint8)

        return result

    except Exception:

        return None


# ============================================================
# FALLBACK ATTENTION MAP
# ============================================================

def create_visual_attention_map(image):

    img = np.array(
        image.convert("RGB")
    )

    resized = cv2.resize(
        img,
        (IMG_SIZE, IMG_SIZE)
    )

    hsv = cv2.cvtColor(
        resized,
        cv2.COLOR_RGB2HSV
    )

    gray = cv2.cvtColor(
        resized,
        cv2.COLOR_RGB2GRAY
    )

    lower_problem = np.array(
        [5, 35, 20],
        dtype=np.uint8
    )

    upper_problem = np.array(
        [45, 255, 230],
        dtype=np.uint8
    )

    color_mask = cv2.inRange(
        hsv,
        lower_problem,
        upper_problem
    )

    dark_mask = cv2.inRange(
        gray,
        0,
        100
    )

    mask = cv2.bitwise_or(
        color_mask,
        dark_mask
    )

    kernel = np.ones(
        (5, 5),
        np.uint8
    )

    mask = cv2.morphologyEx(
        mask,
        cv2.MORPH_OPEN,
        kernel
    )

    mask = cv2.GaussianBlur(
        mask,
        (0, 0),
        8
    )

    heatmap = cv2.applyColorMap(
        mask,
        cv2.COLORMAP_JET
    )

    heatmap = cv2.cvtColor(
        heatmap,
        cv2.COLOR_BGR2RGB
    )

    alpha = (
        mask.astype(np.float32)
        / 255.0
    )

    alpha = (
        alpha[..., None] * 0.55
    )

    result = (
        resized.astype(np.float32)
        * (1 - alpha)
        +
        heatmap.astype(np.float32)
        * alpha
    )

    result = np.clip(
        result,
        0,
        255
    ).astype(np.uint8)

    return result


# ============================================================
# UPLOAD SECTION
# ============================================================

st.markdown(
    '<div class="section-title">🔬 Analyze Your Plant Leaf</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="section-subtitle">'
    'Upload a clear leaf image and let PlantDoc AI identify the most likely plant condition and explain the visual regions that influenced the prediction.'
    '</div>',
    unsafe_allow_html=True
)

uploaded_file = st.file_uploader(
    "📤 Upload Leaf Image",
    type=[
        "jpg",
        "jpeg",
        "png"
    ],
    help="Upload a clear JPG, JPEG or PNG image of a plant leaf."
)


# ============================================================
# NO IMAGE
# ============================================================

if uploaded_file is None:

    with st.container(border=True):

        st.info(
            "👆 Upload a leaf image above to start AI analysis."
        )

        st.markdown("### 💡 For better results")

        tips_col1, tips_col2, tips_col3 = st.columns(3)

        with tips_col1:
            st.write("🌿 **Clear leaf**")
            st.caption("Use a sharp and visible leaf image.")

        with tips_col2:
            st.write("💡 **Good lighting**")
            st.caption("Avoid extremely dark photographs.")

        with tips_col3:
            st.write("📷 **Good framing**")
            st.caption("Keep the leaf clearly visible.")

    st.stop()


# ============================================================
# LOAD IMAGE
# ============================================================

try:

    original_image = Image.open(
        uploaded_file
    ).convert("RGB")

except Exception:

    st.error(
        "❌ Could not read this image."
    )

    st.stop()


# ============================================================
# PREPROCESS
# ============================================================

image_array = preprocess_image(
    original_image
)


# ============================================================
# PREDICTION
# ============================================================

with st.spinner(
    "🧠 PlantDoc AI is analyzing the leaf..."
):

    predictions, top_indices = get_predictions(
        image_array
    )


predicted_index = int(
    top_indices[0]
)

predicted_name = clean_class_name(
    class_names[predicted_index]
)

confidence = (
    float(
        predictions[predicted_index]
    ) * 100
)


# ============================================================
# IMAGE INFORMATION
# ============================================================

st.write("")

info_col1, info_col2 = st.columns(
    [1.05, 0.95]
)


with info_col1:

    with st.container(border=True):

        st.markdown(
            "### 🌿 Uploaded Leaf"
        )

        st.image(
            original_image,
            width="stretch"
        )


with info_col2:

    with st.container(border=True):

        st.markdown(
            "### 📋 Image Information"
        )

        width, height = original_image.size

        info_data = {
            "File Name": uploaded_file.name,
            "Original Size": f"{width} × {height} px",
            "Model Input Size": "224 × 224 px",
            "Image Type": "RGB Leaf Image",
            "Analysis": "Plant Disease Detection"
        }

        for key, value in info_data.items():

            left, right = st.columns(
                [1, 1.35]
            )

            with left:
                st.caption(key)

            with right:
                st.write(value)


# ============================================================
# DIAGNOSIS + TOP 3
# ============================================================

st.write("")

diagnosis_col, prediction_col = st.columns(
    [1, 1.15]
)


# ============================================================
# AI DIAGNOSIS
# ============================================================

with diagnosis_col:

    with st.container(border=True):

        st.markdown(
            "### 🧠 AI Diagnosis"
        )

        st.caption(
            "MOST LIKELY CONDITION"
        )

        st.markdown(
            f"## 🌱 {predicted_name}"
        )

        st.markdown(
            f"# {confidence:.2f}%"
        )

        st.caption(
            "Model Confidence Score"
        )

        st.progress(
            min(
                max(confidence / 100, 0.0),
                1.0
            )
        )


# ============================================================
# TOP 3
# ============================================================

with prediction_col:

    with st.container(border=True):

        st.markdown(
            "### 🏆 Top 3 Predictions"
        )

        for rank, index in enumerate(
            top_indices,
            start=1
        ):

            index = int(index)

            name = clean_class_name(
                class_names[index]
            )

            score = (
                float(
                    predictions[index]
                ) * 100
            )

            rank_col, name_col, score_col = st.columns(
                [0.5, 3.5, 1]
            )

            with rank_col:

                st.markdown(
                    f"### {rank}"
                )

            with name_col:

                st.write(
                    f"**{name}**"
                )

                st.progress(
                    min(
                        max(score / 100, 0.0),
                        1.0
                    )
                )

            with score_col:

                st.write(
                    f"**{score:.2f}%**"
                )


# ============================================================
# EXPLAINABLE AI
# ============================================================

st.write("")

st.markdown(
    '<div class="section-title">🔎 Explainable AI — Why did the model predict this?</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="section-subtitle">'
    'SHAP highlights the image regions that contributed most strongly to the model prediction.'
    '</div>',
    unsafe_allow_html=True
)


with st.spinner(
    "🔎 Generating AI explanation..."
):

    shap_image = generate_shap_heatmap(
        image_array,
        predicted_index
    )


if shap_image is None:

    explanation_image = create_visual_attention_map(
        original_image
    )

    explanation_type = "Visual attention map"

else:

    explanation_image = shap_image

    explanation_type = "SHAP-based explanation"


# ============================================================
# SHAP IMAGE CARDS
# ============================================================

map_col1, map_col2 = st.columns(
    2
)


with map_col1:

    with st.container(border=True):

        st.markdown(
            "### 🔥 AI Attention Map"
        )

        st.caption(
            "Red/yellow regions indicate stronger model influence."
        )

        st.image(
            explanation_image,
            use_container_width=True
        )


with map_col2:

    with st.container(border=True):

        st.markdown(
            "### 🎯 Important / Suspected Regions"
        )

        st.caption(
            "Highlighted areas represent visually important regions."
        )

        original_np = np.array(
            original_image.resize(
                (IMG_SIZE, IMG_SIZE)
            )
        )

        # Create highlighted-region visualization
        gray = cv2.cvtColor(
            original_np,
            cv2.COLOR_RGB2GRAY
        )

        edges = cv2.Canny(
            gray,
            60,
            140
        )

        edges = cv2.dilate(
            edges,
            np.ones((3, 3), np.uint8),
            iterations=1
        )

        highlighted = original_np.copy()

        highlighted[
            edges > 0
        ] = [255, 40, 40]

        st.image(
            highlighted,
            use_container_width=True
        )


st.caption(
    f"{explanation_type} — red/yellow regions represent areas receiving stronger visual importance."
)


st.warning(
    "⚠️ Highlighted areas are an AI explanation, not an exact biological measurement of infected area."
)


# ============================================================
# AI EXPLANATION + MAP GUIDE
# ============================================================

st.write("")

explain_col, guide_col = st.columns(
    [1.35, 0.9]
)


with explain_col:

    with st.container(border=True):

        st.markdown(
            "### 💡 AI Explanation"
        )

        explanation_points = [

            (
                "Prediction",
                f"The model identified **{predicted_name}** as the most likely class."
            ),

            (
                "Model confidence",
                f"The model assigned approximately **{confidence:.2f}%** confidence to this prediction."
            ),

            (
                "Important regions",
                "The red/yellow regions indicate areas that had stronger visual influence on the model prediction."
            ),

            (
                "Leaf colour",
                "Colour differences such as yellow, brown or unusually dark regions can contribute to plant disease classification."
            ),

            (
                "Leaf texture",
                "Spots, patches, surface patterns and texture changes may provide useful visual information to the model."
            ),

            (
                "Spatial pattern",
                "The model also considers where visual patterns appear across different regions of the leaf."
            ),

            (
                "Interpretation",
                "The highlighted regions should be treated as model-important areas rather than an exact biological disease boundary."
            )

        ]

        for number, (
            title,
            explanation
        ) in enumerate(
            explanation_points,
            start=1
        ):

            st.markdown(
                f"**🟢 {number}. {title}**"
            )

            st.write(
                explanation
            )


with guide_col:

    with st.container(border=True):

        st.markdown(
            "### 🎨 How to Read the AI Map"
        )

        st.markdown(
            "🔴 **Red**"
        )

        st.caption(
            "Strong model attention / highly influential region."
        )

        st.divider()

        st.markdown(
            "🟡 **Yellow**"
        )

        st.caption(
            "Medium-to-high model attention."
        )

        st.divider()

        st.markdown(
            "🔵 **Blue**"
        )

        st.caption(
            "Lower contribution to the selected prediction."
        )


    with st.container(border=True):

        st.markdown(
            "### ⚠️ Important"
        )

        st.info(
            "The highlighted region represents areas that influenced the AI model's prediction. "
            "It should not be considered a clinically or biologically verified disease boundary."
        )


# ============================================================
# HEALTH STATUS
# ============================================================

st.write("")

if "healthy" in predicted_name.lower():

    st.success(
        "🌿 The model's top prediction indicates a healthy leaf."
    )

else:

    st.warning(
        "⚠️ The model detected a disease-related visual pattern."
    )


# ============================================================
# DISCLAIMER
# ============================================================

with st.expander(
    "ℹ️ Important Information"
):

    st.write(
        """
        PlantDoc AI provides an AI-based visual classification
        of plant leaf images.

        The highlighted regions show areas that influenced
        the model's visual decision.

        They should NOT be considered an exact measurement
        of disease severity or the exact infected area.

        For real agricultural treatment decisions,
        consult an agriculture expert.
        """
    )


# ============================================================
# FOOTER
# ============================================================

st.markdown(
    """
    <div class="footer">
        🌿 <strong>PlantDoc AI</strong><br>
        AI-Based Plant Disease Detection • Deep Learning • SHAP Explainable AI<br>
        Major Project • CSE / AI & ML 💚
    </div>
    """,
    unsafe_allow_html=True
)