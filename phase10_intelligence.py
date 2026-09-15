"""Phase 10 agricultural intelligence and productization helpers.

The helpers are deterministic and conservative: they summarize model outputs,
identify monitoring/review priority, and provide bilingual wording. They do
not diagnose biological disease, estimate severity, prescribe pesticides, or
claim agronomic certainty.
"""

from __future__ import annotations

from collections import Counter
from typing import Any, Iterable

from decision_support import build_decision_support, clean_label

SUPPORTED_LANGUAGES = {"en", "hi"}


def normalize_language(language: str | None) -> str:
    value = str(language or "en").strip().lower()
    return value if value in SUPPORTED_LANGUAGES else "en"


def _priority_for_scan(decision: dict[str, Any]) -> str:
    if decision["reliability"] == "uncertain":
        return "high"
    if not decision["is_healthy_prediction"] and decision["reliability"] in {"low", "unknown"}:
        return "high"
    if not decision["is_healthy_prediction"]:
        return "moderate"
    return "routine"


def _translate_steps(steps: list[str], language: str) -> list[str]:
    if language != "hi":
        return steps

    translations = {
        "Continue routine crop monitoring.": "फसल की नियमित निगरानी जारी रखें।",
        "Recheck new growth or visibly changing leaves if symptoms appear.": "लक्षण दिखने पर नई वृद्धि या बदलती पत्तियों की दोबारा जाँच करें।",
        "Inspect several leaves instead of relying on one image.": "केवल एक तस्वीर पर निर्भर रहने के बजाय कई पत्तियों की जाँच करें।",
        "Upload a clearer leaf image or collect another observation.": "पत्ती की अधिक स्पष्ट तस्वीर अपलोड करें या एक और अवलोकन लें।",
        "Do not make treatment decisions from an uncertain prediction alone.": "केवल अनिश्चित AI prediction के आधार पर उपचार का निर्णय न लें।",
        "Seek crop-specific agricultural guidance before selecting a treatment.": "उपचार चुनने से पहले फसल-विशिष्ट कृषि सलाह लें।",
        "Seek crop-specific agricultural guidance before treatment decisions.": "उपचार संबंधी निर्णय से पहले फसल-विशिष्ट कृषि सलाह लें।",
        "Seek crop-specific guidance before selecting a treatment.": "उपचार चुनने से पहले फसल-विशिष्ट कृषि सलाह लें।",
    }
    return [translations.get(step, step) for step in steps]


def build_scan_intelligence(
    label: str | None,
    confidence: float | None,
    margin: float | None,
    status: str | None = None,
    language: str | None = "en",
) -> dict[str, Any]:
    lang = normalize_language(language)
    decision = build_decision_support(label, confidence, margin, status)
    priority = _priority_for_scan(decision)

    if lang == "hi":
        headline = {
            "routine": "नियमित निगरानी",
            "moderate": "निगरानी बढ़ाएँ",
            "high": "दोबारा जाँच / विशेषज्ञ समीक्षा प्राथमिक है",
        }[priority]
        rationale = {
            "routine": "AI result में पर्याप्त भरोसा है और healthy classification मिला है।",
            "moderate": "AI result disease/condition pattern दिखाता है; कई observations से पुष्टि करना बेहतर है।",
            "high": "Confidence कम/अनिश्चित है या result disease pattern दिखाता है; केवल इस prediction पर treatment निर्णय न लें।",
        }[priority]
    else:
        headline = {
            "routine": "Routine monitoring",
            "moderate": "Increase monitoring",
            "high": "Recheck / expert review is a priority",
        }[priority]
        rationale = {
            "routine": "The model produced a sufficiently reliable healthy classification.",
            "moderate": "The model indicates a disease/condition pattern; confirming with additional observations is preferable.",
            "high": "Confidence is low/uncertain or the result indicates a disease pattern; do not make treatment decisions from this prediction alone.",
        }[priority]

    return {
        **decision,
        "language": lang,
        "attention_priority": priority,
        "headline": headline,
        "rationale": rationale,
        "recommended_next_steps": _translate_steps(decision["recommended_next_steps"], lang),
        "product_note": (
            "Use this result to prioritize observation and review, not as a standalone treatment prescription."
            if lang == "en"
            else "इस result का उपयोग निगरानी और समीक्षा की प्राथमिकता तय करने के लिए करें, standalone treatment prescription के रूप में नहीं।"
        ),
    }


def build_crop_intelligence(scans: Iterable[Any], language: str | None = "en") -> dict[str, Any]:
    lang = normalize_language(language)
    ordered_scans = sorted(list(scans), key=lambda item: item.created_at or 0, reverse=True)
    completed = [scan for scan in ordered_scans if scan.prediction_status == "completed"]
    rejected = [scan for scan in ordered_scans if scan.prediction_status == "rejected"]
    disease_scans = [
        scan for scan in completed
        if scan.prediction and "healthy" not in str(scan.prediction).lower()
    ]
    predictions = [str(scan.prediction) for scan in completed if scan.prediction]
    repeated_conditions = Counter(clean_label(value) for value in predictions).most_common(5)

    recent_window = completed[:10]
    recent_disease = sum(
        1 for scan in recent_window
        if scan.prediction and "healthy" not in str(scan.prediction).lower()
    )
    recent_disease_rate = round((recent_disease / len(recent_window)) * 100, 2) if recent_window else 0.0
    rejection_rate = round((len(rejected) / len(ordered_scans)) * 100, 2) if ordered_scans else 0.0
    avg_confidence = (
        round(
            sum(float(scan.confidence) for scan in completed if scan.confidence is not None)
            / sum(1 for scan in completed if scan.confidence is not None),
            2,
        )
        if any(scan.confidence is not None for scan in completed)
        else None
    )

    if not ordered_scans:
        risk = "no_data"
    elif recent_disease_rate >= 60 or rejection_rate >= 40:
        risk = "high_attention"
    elif recent_disease_rate >= 30 or rejection_rate >= 20:
        risk = "monitor"
    else:
        risk = "routine"

    if lang == "hi":
        risk_label = {
            "no_data": "डेटा उपलब्ध नहीं",
            "high_attention": "उच्च प्राथमिकता निगरानी",
            "monitor": "निगरानी आवश्यक",
            "routine": "नियमित निगरानी",
        }[risk]
        recommendation = {
            "no_data": "इस crop के लिए अधिक scans collect करें।",
            "high_attention": "कई पौधों/पत्तियों की दोबारा जाँच करें और जरूरत होने पर crop-specific expert review लें।",
            "monitor": "अगले observations नियमित रूप से record करें और repeated pattern होने पर expert review लें।",
            "routine": "नियमित monitoring जारी रखें और बदलते symptoms होने पर नए scans लें।",
        }[risk]
    else:
        risk_label = {
            "no_data": "No data",
            "high_attention": "High-priority monitoring",
            "monitor": "Monitoring recommended",
            "routine": "Routine monitoring",
        }[risk]
        recommendation = {
            "no_data": "Collect more scans for this crop before drawing conclusions.",
            "high_attention": "Recheck multiple plants/leaves and seek crop-specific expert review when appropriate.",
            "monitor": "Record observations regularly and seek expert review when a pattern repeats.",
            "routine": "Continue routine monitoring and create new scans when visible symptoms change.",
        }[risk]

    return {
        "language": lang,
        "scan_count": len(ordered_scans),
        "completed_scans": len(completed),
        "rejected_scans": len(rejected),
        "rejection_rate": rejection_rate,
        "average_confidence": avg_confidence,
        "disease_prediction_count": len(disease_scans),
        "recent_10_disease_rate": recent_disease_rate,
        "risk_level": risk,
        "risk_label": risk_label,
        "recommendation": recommendation,
        "repeated_conditions": [
            {"prediction": name, "count": count}
            for name, count in repeated_conditions
        ],
        "limitations": [
            "A scan trend is not a confirmed field-level disease prevalence estimate.",
            "Image sampling can be biased by which leaves and plants were photographed.",
            "Weather, crop stage, cultivar, soil, pests, and field context are not inferred from image-only scans.",
        ],
    }
