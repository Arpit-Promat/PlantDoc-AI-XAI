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
# SIMPLE NATIVE STREAMLIT THEME
# NO HTML USED FOR UI
# ============================================================

st.markdown(
    """
    # 🌿 PlantDoc AI
    ### AI-Based Plant Disease Detection & Explainable AI

    **Deep Learning** • **Plant Health Analysis** • **SHAP XAI**
    """
)

st.divider()


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

    # --------------------------------------------------------
    # Convert output to probabilities if necessary
    # --------------------------------------------------------

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

        # ----------------------------------------------------
        # SHAP output handling
        # ----------------------------------------------------

        if values.ndim == 5:

            # [image, height, width, channels, classes]
            if predicted_index < values.shape[-1]:

                heat = values[
                    0,
                    :, :,
                    :,
                    predicted_index
                ]

            else:

                heat = values[0]

        elif values.ndim == 4:

            # [image, height, width, channels]
            heat = values[0]

        else:

            return None

        # ----------------------------------------------------
        # Convert RGB SHAP values into one heat map
        # ----------------------------------------------------

        if heat.ndim == 3:

            heat = np.mean(
                np.abs(heat),
                axis=-1
            )

        heat = np.abs(
            heat
        )

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

        # ----------------------------------------------------
        # Create colored heatmap
        # ----------------------------------------------------

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

        # ----------------------------------------------------
        # Overlay heatmap on original leaf
        # ----------------------------------------------------

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
# FALLBACK VISUAL HIGHLIGHT
# ============================================================

def create_visual_attention_map(
    image
):

    """
    Fallback visualization.

    This is NOT an exact measurement of infection.
    It simply highlights visually unusual regions.
    """

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

    # --------------------------------------------------------
    # Detect yellow/brown/dark regions
    # --------------------------------------------------------

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

st.subheader(
    "🔬 Analyze Your Plant Leaf"
)

st.write(
    "Upload a clear JPG, JPEG or PNG image of a plant leaf."
)

uploaded_file = st.file_uploader(
    "📤 Choose a leaf image",
    type=[
        "jpg",
        "jpeg",
        "png"
    ]
)


# ============================================================
# NO IMAGE
# ============================================================

if uploaded_file is None:

    st.info(
        "👆 Upload a leaf image above to start the AI analysis."
    )

    st.markdown(
        """
        ### 💡 For better results

        - Use a clear leaf image.
        - Keep the leaf visible.
        - Avoid extremely dark images.
        - Avoid very blurry photographs.
        """
    )

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

    predictions, top_indices = (
        get_predictions(
            image_array
        )
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
# IMAGE ANALYSIS
# ============================================================

st.divider()

st.subheader(
    "🖼️ Visual Analysis"
)

st.write(
    "Original image and AI-generated important-region visualization."
)


with st.spinner(
    "🔎 Generating AI explanation..."
):

    shap_image = generate_shap_heatmap(
        image_array,
        predicted_index
    )


# If SHAP fails, use fallback
if shap_image is None:

    explanation_image = (
        create_visual_attention_map(
            original_image
        )
    )

    explanation_type = (
        "Visual attention map"
    )

else:

    explanation_image = shap_image

    explanation_type = (
        "SHAP-based explanation"
    )


# ============================================================
# ORIGINAL + EXPLANATION
# ============================================================

image_col1, image_col2 = st.columns(
    2
)


with image_col1:

    st.markdown(
        "### 🌿 Original Leaf"
    )

    st.image(
        original_image,
        use_container_width=True
    )


with image_col2:

    st.markdown(
        "### 🔥 AI Important Areas"
    )

    st.image(
        explanation_image,
        use_container_width=True
    )

    st.caption(
        explanation_type
        + " — red/yellow regions represent "
        "areas receiving stronger visual importance."
    )


st.warning(
    "⚠️ Highlighted areas are an AI explanation, "
    "not an exact biological measurement of infected area."
)


# ============================================================
# AI DIAGNOSIS
# ============================================================

st.divider()

st.subheader(
    "🧠 AI Diagnosis"
)


diagnosis_col1, diagnosis_col2 = st.columns(
    [1.2, 0.8]
)


with diagnosis_col1:

    st.success(
        f"🌱 Most likely condition: **{predicted_name}**"
    )


with diagnosis_col2:

    st.metric(
        "Model Confidence",
        f"{confidence:.2f}%"
    )


# ============================================================
# TOP 3 PREDICTIONS
# ============================================================

st.subheader(
    "🏆 Top 3 Predictions"
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

    col_name, col_score = st.columns(
        [4, 1]
    )

    with col_name:

        st.write(
            f"**#{rank} {name}**"
        )

    with col_score:

        st.write(
            f"**{score:.2f}%**"
        )

    st.progress(
        min(
            max(score / 100, 0.0),
            1.0
        )
    )


# ============================================================
# XAI SECTION
# ============================================================

st.divider()

st.subheader(
    "🔍 Explainable AI"
)

st.write(
    "The following points explain what the model's "
    "visual prediction means."
)


# ============================================================
# EXPLANATION POINTS
# ============================================================

explanation_points = [

    (
        "Prediction",
        f"The model's strongest prediction is "
        f"**{predicted_name}**."
    ),

    (
        "Important regions",
        "The red/yellow regions in the explanation "
        "image indicate areas that had stronger "
        "influence on the visual prediction."
    ),

    (
        "Leaf colour",
        "Colour differences such as yellow, brown "
        "or unusually dark regions can contribute "
        "to plant disease classification."
    ),

    (
        "Leaf texture",
        "Spots, patches, surface patterns and "
        "texture changes may provide useful "
        "visual information to the model."
    ),

    (
        "Spatial pattern",
        "The model also considers where visual "
        "patterns appear across the leaf."
    ),

    (
        "Confidence",
        f"The model assigned approximately "
        f"**{confidence:.2f}%** confidence to "
        f"the top prediction."
    )

]


for number, (
    title,
    explanation
) in enumerate(
    explanation_points,
    start=1
):

    with st.container(
        border=True
    ):

        st.markdown(
            f"### {number}. {title}"
        )

        st.write(
            explanation
        )


# ============================================================
# HEALTH STATUS
# ============================================================

st.divider()

if "healthy" in predicted_name.lower():

    st.success(
        "🌿 The model's top prediction indicates "
        "a healthy leaf."
    )

else:

    st.warning(
        "⚠️ The model detected a disease-related "
        "visual pattern."
    )


# ============================================================
# DISCLAIMER
# ============================================================

with st.expander(
    "ℹ️ Important Information"
):

    st.write(
        """
        PlantDoc AI provides an AI-based visual
        classification of plant leaf images.

        The highlighted regions show areas that
        influenced the model's visual decision.
        They should NOT be considered an exact
        measurement of disease severity or the
        exact infected area.

        For real agricultural treatment decisions,
        consult an agriculture expert.
        """
    )


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "🌿 PlantDoc AI • Deep Learning • Explainable AI • SHAP"
)