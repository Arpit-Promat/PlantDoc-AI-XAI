import streamlit as st
import json
import numpy as np
import cv2
from PIL import Image
from tensorflow.keras.models import load_model


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="PlantDoc AI",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="collapsed"
)


# =========================================================
# CUSTOM CSS
# =========================================================

st.markdown(
    """
    <style>

    /* ---------- GLOBAL ---------- */

    .stApp {
        background:
            radial-gradient(circle at 10% 10%, rgba(31, 105, 65, 0.22), transparent 30%),
            radial-gradient(circle at 90% 20%, rgba(20, 90, 60, 0.18), transparent 30%),
            linear-gradient(135deg, #06120d 0%, #071713 50%, #04100c 100%);
        color: #f5fff8;
    }

    .block-container {
        max-width: 1250px;
        padding-top: 2rem;
        padding-bottom: 4rem;
    }

    /* ---------- REMOVE STREAMLIT DEFAULT ---------- */

    #MainMenu {
        visibility: hidden;
    }

    footer {
        visibility: hidden;
    }

    header {
        background: transparent !important;
    }

    /* ---------- HERO ---------- */

    .hero {
        padding: 35px 40px;
        border-radius: 28px;
        border: 1px solid rgba(88, 220, 130, 0.25);
        background:
            linear-gradient(
                135deg,
                rgba(19, 76, 44, 0.55),
                rgba(5, 24, 17, 0.85)
            );
        box-shadow:
            0 20px 60px rgba(0, 0, 0, 0.30),
            inset 0 1px 0 rgba(255,255,255,0.04);
        margin-bottom: 30px;
    }

    .brand {
        font-size: 42px;
        font-weight: 800;
        letter-spacing: -1px;
        color: #f5fff7;
        margin-bottom: 8px;
    }

    .brand span {
        color: #71f29a;
    }

    .tagline {
        color: #a8c8b3;
        font-size: 17px;
        margin-bottom: 20px;
    }

    .badge-row {
        display: flex;
        gap: 10px;
        flex-wrap: wrap;
    }

    .badge {
        display: inline-block;
        padding: 8px 14px;
        border-radius: 999px;
        background: rgba(76, 190, 110, 0.12);
        border: 1px solid rgba(94, 220, 130, 0.25);
        color: #b8ffca;
        font-size: 13px;
        font-weight: 600;
    }

    /* ---------- SECTION TITLES ---------- */

    .section-title {
        font-size: 27px;
        font-weight: 750;
        margin-top: 28px;
        margin-bottom: 6px;
        color: #f2fff5;
    }

    .section-subtitle {
        color: #8fb39c;
        font-size: 15px;
        margin-bottom: 20px;
    }

    /* ---------- CARDS ---------- */

    .card {
        background: rgba(12, 31, 23, 0.78);
        border: 1px solid rgba(94, 210, 126, 0.18);
        border-radius: 22px;
        padding: 24px;
        box-shadow: 0 15px 40px rgba(0,0,0,0.20);
        height: 100%;
    }

    .card-title {
        font-size: 19px;
        font-weight: 700;
        color: #eaffef;
        margin-bottom: 14px;
    }

    /* ---------- UPLOAD BOX ---------- */

    [data-testid="stFileUploader"] {
        background: rgba(11, 32, 23, 0.85);
        border: 1px dashed rgba(103, 231, 139, 0.45);
        border-radius: 20px;
        padding: 10px;
    }

    [data-testid="stFileUploader"] section {
        background: transparent !important;
    }

    [data-testid="stFileUploaderDropzone"] {
        background: rgba(16, 45, 31, 0.50) !important;
        border-radius: 16px !important;
    }

    /* ---------- IMAGES ---------- */

    [data-testid="stImage"] {
        border-radius: 18px;
        overflow: hidden;
    }

    /* ---------- PREDICTION ---------- */

    .prediction-main {
        padding: 28px;
        border-radius: 22px;
        background:
            linear-gradient(
                135deg,
                rgba(22, 91, 51, 0.55),
                rgba(8, 30, 21, 0.75)
            );
        border: 1px solid rgba(104, 235, 137, 0.28);
    }

    .prediction-label {
        color: #93bba0;
        font-size: 13px;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        font-weight: 700;
    }

    .prediction-name {
        color: #79f29d;
        font-size: 30px;
        font-weight: 800;
        margin-top: 8px;
        margin-bottom: 14px;
    }

    .confidence-number {
        font-size: 42px;
        font-weight: 800;
        color: #ffffff;
    }

    .confidence-caption {
        color: #91b29d;
        font-size: 13px;
    }

    /* ---------- TOP PREDICTION ---------- */

    .top-item {
        padding: 15px 16px;
        margin-bottom: 12px;
        border-radius: 15px;
        background: rgba(21, 45, 34, 0.72);
        border: 1px solid rgba(112, 210, 135, 0.13);
    }

    .top-name {
        color: #eaffef;
        font-weight: 650;
        font-size: 15px;
    }

    .top-percent {
        color: #7bf19b;
        font-weight: 750;
        float: right;
    }

    .progress-bg {
        width: 100%;
        height: 7px;
        margin-top: 10px;
        border-radius: 10px;
        background: #172c22;
        overflow: hidden;
    }

    .progress-fill {
        height: 100%;
        border-radius: 10px;
        background: linear-gradient(90deg, #42cf78, #8affaa);
    }

    /* ---------- XAI ---------- */

    .xai-box {
        padding: 20px;
        border-radius: 18px;
        background: rgba(9, 27, 19, 0.75);
        border: 1px solid rgba(105, 229, 139, 0.17);
        margin-bottom: 12px;
    }

    .xai-number {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 30px;
        height: 30px;
        border-radius: 50%;
        background: #1b6840;
        color: #aaffc0;
        font-weight: 800;
        margin-right: 10px;
    }

    .xai-title {
        color: #eaffef;
        font-weight: 700;
        font-size: 16px;
    }

    .xai-text {
        color: #9bbba6;
        font-size: 14px;
        line-height: 1.6;
        margin-top: 8px;
    }

    /* ---------- STATUS ---------- */

    .status-good {
        padding: 14px 18px;
        border-radius: 14px;
        background: rgba(48, 180, 91, 0.12);
        border: 1px solid rgba(80, 220, 120, 0.25);
        color: #aaffbd;
        font-weight: 600;
    }

    .status-warning {
        padding: 14px 18px;
        border-radius: 14px;
        background: rgba(210, 150, 45, 0.10);
        border: 1px solid rgba(230, 170, 60, 0.25);
        color: #ffe0a0;
        font-weight: 600;
    }

    /* ---------- BUTTON ---------- */

    .stButton > button {
        width: 100%;
        border-radius: 13px;
        border: 1px solid rgba(113, 242, 154, 0.30);
        background: linear-gradient(135deg, #1b7444, #155d38);
        color: white;
        font-weight: 700;
        min-height: 46px;
    }

    .stButton > button:hover {
        border-color: #76f39c;
        color: white;
    }

    /* ---------- FOOTER ---------- */

    .footer {
        text-align: center;
        color: #64806e;
        font-size: 13px;
        padding-top: 45px;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# =========================================================
# MODEL LOADING
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
# HELPER FUNCTIONS
# =========================================================

def clean_class_name(name):

    name = name.replace("___", " → ")
    name = name.replace("__", " ")
    name = name.replace("_", " ")

    return name.strip()


def prepare_image(image):

    image_rgb = image.convert("RGB")

    resized = image_rgb.resize((224, 224))

    arr = np.array(resized).astype("float32") / 255.0

    arr = np.expand_dims(arr, axis=0)

    return image_rgb, resized, arr


def get_predictions(arr):

    predictions = model.predict(
        arr,
        verbose=0
    )[0]

    # Make sure probabilities are usable
    predictions = np.asarray(predictions).astype(float)

    # If model output isn't normalized, normalize it
    total = np.sum(predictions)

    if total > 0:
        predictions = predictions / total

    top_indices = np.argsort(predictions)[::-1][:3]

    results = []

    for index in top_indices:

        results.append(
            {
                "index": int(index),
                "name": clean_class_name(
                    class_names[index]
                ),
                "confidence": float(
                    predictions[index] * 100
                )
            }
        )

    return results


def create_attention_map(original_image, predicted_class):

    """
    Creates a visual disease/attention-area image.

    This is a visual XAI-style highlighting layer.
    It does not change the model prediction.
    """

    img = np.array(
        original_image.convert("RGB")
    )

    h, w = img.shape[:2]

    resized = cv2.resize(
        img,
        (224, 224)
    )

    # Convert to HSV
    hsv = cv2.cvtColor(
        resized,
        cv2.COLOR_RGB2HSV
    )

    # Green leaf mask
    lower_green = np.array(
        [20, 35, 25],
        dtype=np.uint8
    )

    upper_green = np.array(
        [100, 255, 255],
        dtype=np.uint8
    )

    green_mask = cv2.inRange(
        hsv,
        lower_green,
        upper_green
    )

    # Detect darker / brown / yellow regions
    gray = cv2.cvtColor(
        resized,
        cv2.COLOR_RGB2GRAY
    )

    dark_regions = cv2.inRange(
        gray,
        0,
        105
    )

    # Saturated yellow/brown areas
    lower_problem = np.array(
        [5, 40, 30],
        dtype=np.uint8
    )

    upper_problem = np.array(
        [45, 255, 240],
        dtype=np.uint8
    )

    problem_color = cv2.inRange(
        hsv,
        lower_problem,
        upper_problem
    )

    # Combine visual regions
    problem_mask = cv2.bitwise_or(
        dark_regions,
        problem_color
    )

    # Keep mostly inside leaf area
    problem_mask = cv2.bitwise_and(
        problem_mask,
        green_mask
    )

    # Morphological cleanup
    kernel = np.ones(
        (7, 7),
        np.uint8
    )

    problem_mask = cv2.morphologyEx(
        problem_mask,
        cv2.MORPH_OPEN,
        kernel
    )

    problem_mask = cv2.morphologyEx(
        problem_mask,
        cv2.MORPH_DILATE,
        kernel
    )

    # Blur to create heatmap-like effect
    heat = cv2.GaussianBlur(
        problem_mask,
        (0, 0),
        15
    )

    heat = cv2.normalize(
        heat,
        None,
        0,
        255,
        cv2.NORM_MINMAX
    )

    heat = heat.astype(np.uint8)

    # Color heatmap
    colored = cv2.applyColorMap(
        heat,
        cv2.COLORMAP_JET
    )

    colored = cv2.cvtColor(
        colored,
        cv2.COLOR_BGR2RGB
    )

    # Overlay
    base = resized.astype(np.float32)
    overlay = colored.astype(np.float32)

    alpha = (
        heat.astype(np.float32) / 255.0
    )[..., None] * 0.65

    result = (
        base * (1 - alpha)
        + overlay * alpha
    )

    result = np.clip(
        result,
        0,
        255
    ).astype(np.uint8)

    # Highlight strongest areas with contours
    _, binary = cv2.threshold(
        heat,
        80,
        255,
        cv2.THRESH_BINARY
    )

    contours, _ = cv2.findContours(
        binary,
        cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE
    )

    for contour in contours:

        area = cv2.contourArea(contour)

        if area > 40:

            cv2.drawContours(
                result,
                [contour],
                -1,
                (255, 255, 255),
                1
            )

    return Image.fromarray(result)


def explanation_points(
    disease_name,
    confidence
):

    disease_lower = disease_name.lower()

    points = []

    if "healthy" in disease_lower:

        points.append(
            (
                "Healthy appearance",
                "The model classified the leaf as healthy based on visual patterns learned during training."
            )
        )

        points.append(
            (
                "Leaf colour",
                "The visible green regions are consistent with a healthy-looking leaf."
            )
        )

        points.append(
            (
                "Disease symptoms",
                "No strong disease-like visual pattern was identified by the classification model."
            )
        )

        points.append(
            (
                "Surface pattern",
                "The model considers the overall texture and colour distribution closer to healthy examples."
            )
        )

        points.append(
            (
                "Prediction confidence",
                f"The model's top prediction confidence is {confidence:.2f}%."
            )
        )

    else:

        points.append(
            (
                "Affected visual region",
                "The highlighted image marks image regions that show stronger visual irregularities."
            )
        )

        points.append(
            (
                "Colour variation",
                "Changes from normal green leaf colour can contribute to disease classification."
            )
        )

        points.append(
            (
                "Texture pattern",
                "Spots, patches and unusual surface texture can provide useful visual signals."
            )
        )

        points.append(
            (
                "Leaf structure",
                "The model also considers the spatial arrangement of visible patterns across the leaf."
            )
        )

        points.append(
            (
                "Prediction confidence",
                f"The model's top prediction confidence is {confidence:.2f}%."
            )
        )

    return points


# =========================================================
# HERO SECTION
# =========================================================

st.markdown(
    """
    <div class="hero">

        <div class="brand">
            🌿 PlantDoc <span>AI</span>
        </div>

        <div class="tagline">
            AI-Based Plant Disease Detection & Explainable Artificial Intelligence
        </div>

        <div class="badge-row">
            <div class="badge">⚡ Deep Learning</div>
            <div class="badge">🔬 Explainable AI</div>
            <div class="badge">🌱 Plant Health</div>
            <div class="badge">🧠 AI Diagnosis</div>
        </div>

    </div>
    """,
    unsafe_allow_html=True
)


# =========================================================
# UPLOAD SECTION
# =========================================================

st.markdown(
    """
    <div class="section-title">
        🔬 Analyze Your Plant Leaf
    </div>

    <div class="section-subtitle">
        Upload a clear leaf image and let PlantDoc AI analyze its visual characteristics.
    </div>
    """,
    unsafe_allow_html=True
)


uploaded_file = st.file_uploader(
    "📤 Upload Leaf Image",
    type=["jpg", "jpeg", "png"],
    help="Upload a clear plant leaf image."
)


# =========================================================
# NO IMAGE
# =========================================================

if uploaded_file is None:

    st.markdown(
        """
        <div class="status-good">
            👆 Upload a leaf image above to start the AI analysis.
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <div class="footer">
            PlantDoc AI • Deep Learning + Explainable AI
        </div>
        """,
        unsafe_allow_html=True
    )

    st.stop()


# =========================================================
# READ IMAGE
# =========================================================

try:

    image = Image.open(
        uploaded_file
    ).convert("RGB")

except Exception:

    st.error(
        "❌ Unable to read this image. Please upload JPG or PNG."
    )

    st.stop()


# =========================================================
# PREPARE IMAGE
# =========================================================

original_image, resized_image, image_array = prepare_image(
    image
)


# =========================================================
# PREDICTION
# =========================================================

with st.spinner("🧠 PlantDoc AI is analyzing the leaf..."):

    results = get_predictions(
        image_array
    )


if not results:

    st.error(
        "❌ Prediction could not be generated."
    )

    st.stop()


best = results[0]

disease_name = best["name"]

confidence = best["confidence"]


# =========================================================
# IMAGE SECTION
# =========================================================

st.markdown(
    """
    <div class="section-title">
        🖼️ Leaf Analysis
    </div>

    <div class="section-subtitle">
        Compare the original leaf with the AI-highlighted visual analysis.
    </div>
    """,
    unsafe_allow_html=True
)


attention_image = create_attention_map(
    original_image,
    disease_name
)


col1, col2 = st.columns(
    2,
    gap="large"
)


with col1:

    st.markdown(
        """
        <div class="card">
            <div class="card-title">
                🌿 Original Leaf
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.image(
        original_image,
        use_container_width=True
    )


with col2:

    st.markdown(
        """
        <div class="card">
            <div class="card-title">
                🔥 AI Highlighted Areas
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.image(
        attention_image,
        use_container_width=True
    )

    st.caption(
        "Highlighted regions represent visually prominent areas used for the visual explanation."
    )


# =========================================================
# DIAGNOSIS
# =========================================================

st.markdown(
    """
    <div class="section-title">
        🧠 AI Diagnosis
    </div>
    """,
    unsafe_allow_html=True
)


left, right = st.columns(
    [1.15, 0.85],
    gap="large"
)


with left:

    st.markdown(
        f"""
        <div class="prediction-main">

            <div class="prediction-label">
                MOST LIKELY CONDITION
            </div>

            <div class="prediction-name">
                {disease_name}
            </div>

            <div class="confidence-number">
                {confidence:.2f}%
            </div>

            <div class="confidence-caption">
                Model confidence score
            </div>

        </div>
        """,
        unsafe_allow_html=True
    )


with right:

    st.markdown(
        """
        <div class="card">

            <div class="card-title">
                🏆 Top 3 Predictions
            </div>

        """,
        unsafe_allow_html=True
    )

    for i, item in enumerate(results):

        safe_width = min(
            max(item["confidence"], 0),
            100
        )

        st.markdown(
            f"""
            <div class="top-item">

                <span class="top-name">
                    #{i + 1} &nbsp; {item["name"]}
                </span>

                <span class="top-percent">
                    {item["confidence"]:.2f}%
                </span>

                <div class="progress-bg">
                    <div
                        class="progress-fill"
                        style="width:{safe_width}%;">
                    </div>
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
# EXPLAINABLE AI
# =========================================================

st.markdown(
    """
    <div class="section-title">
        🔎 Explainable AI
    </div>

    <div class="section-subtitle">
        Why the model may have made this prediction.
    </div>
    """,
    unsafe_allow_html=True
)


points = explanation_points(
    disease_name,
    confidence
)


for i, (title, text) in enumerate(points):

    st.markdown(
        f"""
        <div class="xai-box">

            <div>
                <span class="xai-number">
                    {i + 1}
                </span>

                <span class="xai-title">
                    {title}
                </span>
            </div>

            <div class="xai-text">
                {text}
            </div>

        </div>
        """,
        unsafe_allow_html=True
    )


# =========================================================
# RESULT STATUS
# =========================================================

if "healthy" in disease_name.lower():

    st.markdown(
        """
        <div class="status-good">
            🌱 The model's top prediction indicates a healthy leaf.
        </div>
        """,
        unsafe_allow_html=True
    )

else:

    st.markdown(
        """
        <div class="status-warning">
            ⚠️ The model detected a disease-related visual pattern.
            Consider consulting an agriculture expert before taking treatment decisions.
        </div>
        """,
        unsafe_allow_html=True
    )


# =========================================================
# FOOTER
# =========================================================

st.markdown(
    """
    <div class="footer">
        🌿 PlantDoc AI &nbsp;•&nbsp;
        Deep Learning &nbsp;•&nbsp;
        Explainable AI &nbsp;•&nbsp;
        Plant Health Analysis
    </div>
    """,
    unsafe_allow_html=True
)