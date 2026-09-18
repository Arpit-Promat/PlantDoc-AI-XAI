"""Disease occurrence and prevention guidance for ATHARVADRISHTI.

This is educational decision support. It explains common causal pathways and
preventive practices associated with model labels. It does not confirm a
biological diagnosis and does not prescribe pesticides, doses, or treatment
chemicals.
"""

from __future__ import annotations

from typing import Any


def _item(occurs: str, prevention: list[str], note: str = "") -> dict[str, Any]:
    return {
        "how_it_occurs": occurs,
        "prevention": prevention,
        "note": note,
    }


GUIDANCE: dict[str, dict[str, Any]] = {
    # Apple
    "apple scab": _item(
        "A fungal disease caused by Venturia inaequalis. The fungus survives in infected fallen leaves and produces spores that are spread during wet spring weather.",
        [
            "Remove or manage fallen infected leaves to reduce overwintering inoculum.",
            "Improve canopy airflow and avoid prolonged leaf wetness where practical.",
            "Use scab-tolerant/resistant cultivars when available for the growing area.",
        ],
    ),
    "apple black rot": _item(
        "A fungal rot disease associated with Botryosphaeria/Diplodia fungi. Inoculum can survive in dead wood, cankers and mummified fruit and spread to healthy tissue under wet conditions.",
        [
            "Remove mummified fruit, dead wood and obvious cankers where appropriate.",
            "Maintain good orchard sanitation and airflow.",
            "Avoid unnecessary plant injury and monitor fruit and branches regularly.",
        ],
    ),
    "apple cedar apple rust": _item(
        "A rust disease caused by Gymnosporangium fungi that requires apple-family hosts and compatible juniper/cedar hosts to complete its life cycle. Spores can move between hosts by wind and rain.",
        [
            "Use resistant cultivars where available.",
            "Monitor for rust symptoms during the local infection period.",
            "Where locally appropriate, manage nearby alternate-host plants based on agricultural guidance.",
        ],
    ),
    "apple healthy": _item(
        "The model's top class is healthy; no disease pattern was classified from the image.",
        [
            "Continue routine plant and leaf monitoring.",
            "Maintain good sanitation, airflow and balanced irrigation.",
            "Re-scan new or changing leaves when symptoms appear.",
        ],
    ),
    # Blueberry / cherry
    "blueberry healthy": _item(
        "The model's top class is healthy; no disease pattern was classified from the image.",
        [
            "Continue routine monitoring and remove obviously diseased plant material.",
            "Maintain airflow and avoid unnecessary prolonged leaf wetness.",
            "Re-scan changing leaves or new growth when symptoms appear.",
        ],
    ),
    "cherry (including sour) powdery mildew": _item(
        "A fungal disease that spreads by spores. Warm conditions with humid air favor infection, especially when susceptible new growth is present.",
        [
            "Choose resistant/tolerant cultivars when available.",
            "Prune for good airflow and avoid dense, shaded growth.",
            "Monitor young leaves and shoots during periods favorable for mildew.",
        ],
    ),
    "cherry (including sour) healthy": _item(
        "The model's top class is healthy; no disease pattern was classified from the image.",
        [
            "Continue routine monitoring.",
            "Maintain canopy airflow and clean up infected plant debris if symptoms later appear.",
            "Re-scan new growth when leaf changes are noticed.",
        ],
    ),
    # Corn
    "corn (maize) cercospora leaf spot gray leaf spot": _item(
        "A fungal leaf disease caused mainly by Cercospora species. The pathogen survives in corn residue and spreads under warm, humid conditions with leaf wetness.",
        [
            "Rotate crops where practical to reduce residue-borne inoculum.",
            "Use resistant/tolerant hybrids when available.",
            "Manage residue and canopy humidity according to local agronomic guidance.",
        ],
    ),
    "corn (maize) common rust": _item(
        "A rust disease caused by Puccinia sorghi. Windborne spores can reach susceptible plants; cool, wet weather and prolonged leaf wetness favor infection.",
        [
            "Use resistant hybrids when available.",
            "Monitor fields during cool, wet periods.",
            "Protect susceptible crops according to local crop-pathology guidance rather than relying on a single leaf image.",
        ],
    ),
    "corn (maize) northern leaf blight": _item(
        "A fungal disease caused by Exserohilum turcicum. The pathogen can survive on corn residue, and prolonged moisture with moderate temperatures favors infection.",
        [
            "Use resistant hybrids when available.",
            "Rotate crops and manage infected residue where appropriate.",
            "Monitor lower leaves early, especially during prolonged wet periods.",
        ],
    ),
    "corn (maize) healthy": _item(
        "The model's top class is healthy; no disease pattern was classified from the image.",
        [
            "Continue routine field scouting.",
            "Use resistant hybrids and sound crop sanitation practices where appropriate.",
            "Re-scan leaves when new lesions or color changes appear.",
        ],
    ),
    # Grape
    "grape black rot": _item(
        "A fungal disease caused by Guignardia bidwellii. The fungus overwinters in mummified fruit and infected plant tissue; spring rain can release spores that infect wet, susceptible tissue.",
        [
            "Remove mummified berries and infected plant material before new growth when practical.",
            "Keep the canopy open to improve drying and airflow.",
            "Monitor early-season growth closely when rain and leaf wetness are frequent.",
        ],
    ),
    "grape esca (black measles)": _item(
        "Esca is a grapevine trunk-disease complex involving wood-colonizing fungi. Infection is associated with infected wood and wounds, especially around pruning and other plant injuries.",
        [
            "Use healthy planting material and clean pruning practices.",
            "Avoid unnecessary large wounds and manage pruning wounds appropriately.",
            "Remove and isolate severely affected wood according to local viticulture guidance.",
        ],
    ),
    "grape leaf blight (isariopsis leaf spot)": _item(
        "A fungal leaf disease that spreads by spores and is favored by warm, humid and wet conditions.",
        [
            "Improve canopy airflow and sunlight penetration.",
            "Avoid unnecessary leaf wetness and remove heavily affected material where appropriate.",
            "Monitor neighboring leaves for spread after wet weather.",
        ],
    ),
    "grape healthy": _item(
        "The model's top class is healthy; no disease pattern was classified from the image.",
        [
            "Continue routine vineyard scouting.",
            "Maintain canopy airflow and sanitation.",
            "Re-scan leaves when spotting, discoloration or unusual growth develops.",
        ],
    ),
    # Citrus / peach / pepper
    "orange haunglongbing (citrus greening)": _item(
        "A bacterial disease associated with Candidatus Liberibacter species and mainly spread by infected citrus psyllids and grafting with infected material.",
        [
            "Use certified disease-free planting material.",
            "Monitor and manage psyllid populations using locally approved integrated pest-management guidance.",
            "Remove and replace confirmed infected plants where local disease-management programs recommend it.",
        ],
        "Image classification alone cannot confirm citrus greening; laboratory or expert confirmation may be required.",
    ),
    "peach bacterial spot": _item(
        "A bacterial disease caused by Xanthomonas species. Rain splash, wind-driven rain and wet foliage can spread bacteria, with warm wet weather increasing risk.",
        [
            "Use tolerant/resistant cultivars where available.",
            "Improve airflow and avoid unnecessary overhead irrigation.",
            "Remove severely affected material where appropriate and reduce plant-to-plant spread.",
        ],
    ),
    "peach healthy": _item(
        "The model's top class is healthy; no disease pattern was classified from the image.",
        [
            "Continue routine monitoring.",
            "Maintain balanced irrigation, sanitation and canopy airflow.",
            "Re-scan leaves when spots or discoloration appear.",
        ],
    ),
    "pepper, bell bacterial spot": _item(
        "A bacterial disease caused by Xanthomonas species. Bacteria spread through splashing water, contaminated seed or plant material, and warm humid conditions favor disease.",
        [
            "Use clean/certified seed and healthy transplants.",
            "Avoid working plants when foliage is wet and reduce splashing.",
            "Remove severely affected plants or tissue where appropriate.",
        ],
    ),
    "pepper, bell healthy": _item(
        "The model's top class is healthy; no disease pattern was classified from the image.",
        [
            "Continue routine monitoring.",
            "Keep foliage as dry as practical and maintain airflow.",
            "Use clean planting material and re-scan new symptoms.",
        ],
    ),
    # Potato
    "potato early blight": _item(
        "A fungal disease caused mainly by Alternaria solani. The pathogen survives in crop debris and soil; warm conditions, leaf wetness and plant stress can favor disease development.",
        [
            "Rotate crops where practical and remove or manage infected residue.",
            "Maintain balanced plant nutrition and irrigation to reduce stress.",
            "Avoid prolonged leaf wetness and improve airflow where possible.",
        ],
    ),
    "potato late blight": _item(
        "A destructive disease caused by Phytophthora infestans. Spores spread through wind and water, and cool, wet conditions strongly favor infection and rapid spread.",
        [
            "Use certified healthy seed tubers and resistant/tolerant varieties when available.",
            "Scout frequently during cool, wet weather.",
            "Reduce prolonged leaf wetness and follow local late-blight forecasting/guidance.",
        ],
    ),
    "potato healthy": _item(
        "The model's top class is healthy; no disease pattern was classified from the image.",
        [
            "Continue routine scouting.",
            "Use healthy planting material and good field sanitation.",
            "Re-scan leaves promptly when spots or blight-like changes appear.",
        ],
    ),
    # Other healthy classes
    "raspberry healthy": _item(
        "The model's top class is healthy; no disease pattern was classified from the image.",
        [
            "Continue routine monitoring.",
            "Maintain airflow and sanitation.",
            "Re-scan changing foliage or new growth.",
        ],
    ),
    "soybean healthy": _item(
        "The model's top class is healthy; no disease pattern was classified from the image.",
        [
            "Continue routine crop scouting.",
            "Manage crop residue and field moisture according to local practice.",
            "Re-scan leaves when symptoms change or spread.",
        ],
    ),
    "strawberry leaf scorch": _item(
        "A fungal leaf disease caused by Diplocarpon species. Spore production and spread are favored by wet foliage and humid conditions.",
        [
            "Use healthy planting material and resistant/tolerant cultivars when available.",
            "Improve airflow and avoid overhead irrigation where practical.",
            "Remove heavily infected leaves and plant debris where appropriate.",
        ],
    ),
    "strawberry healthy": _item(
        "The model's top class is healthy; no disease pattern was classified from the image.",
        [
            "Continue routine monitoring.",
            "Maintain clean beds and good airflow.",
            "Re-scan leaves when lesions or discoloration appear.",
        ],
    ),
    # Squash / tomato
    "squash powdery mildew": _item(
        "A fungal disease caused by powdery mildew fungi. Spores spread through air, and disease is favored by warm conditions, humidity and dense foliage.",
        [
            "Choose resistant/tolerant cultivars when available.",
            "Improve airflow and sunlight penetration by avoiding overly dense growth.",
            "Scout regularly and act early under favorable mildew conditions.",
        ],
    ),
    "tomato bacterial spot": _item(
        "A bacterial disease caused by Xanthomonas species. It spreads through splashing water, contaminated seed/plant material and handling, especially in warm humid weather.",
        [
            "Use clean seed and healthy transplants.",
            "Avoid overhead irrigation and handling plants when leaves are wet.",
            "Remove severely affected material and sanitize tools where appropriate.",
        ],
    ),
    "tomato early blight": _item(
        "A fungal disease caused mainly by Alternaria solani. It survives in infected crop debris and can spread by rain splash; warm wet conditions favor infection.",
        [
            "Remove or manage infected lower leaves and crop residue where appropriate.",
            "Mulch soil to reduce splash onto lower leaves.",
            "Improve airflow and water at the soil line rather than keeping foliage wet.",
        ],
    ),
    "tomato late blight": _item(
        "A disease caused by Phytophthora infestans. Airborne and water-assisted spores spread infection rapidly under cool, wet conditions.",
        [
            "Use healthy planting material and resistant/tolerant varieties when available.",
            "Scout frequently during cool, wet weather.",
            "Reduce prolonged leaf wetness and seek local late-blight guidance when risk is high.",
        ],
    ),
    "tomato leaf mold": _item(
        "A fungal disease caused by Passalora fulva. High relative humidity and prolonged leaf wetness favor infection and spore production.",
        [
            "Improve greenhouse/field ventilation and canopy airflow.",
            "Avoid prolonged leaf wetness and water at the soil line.",
            "Remove infected leaves and use resistant varieties when available.",
        ],
    ),
    "tomato septoria leaf spot": _item(
        "A fungal disease caused by Septoria lycopersici. Spores spread through water splash and survive on infected plant debris; humid wet weather increases risk.",
        [
            "Remove infected lower leaves and manage crop debris.",
            "Mulch to reduce soil splash and water at the plant base.",
            "Improve airflow and avoid working through wet foliage.",
        ],
    ),
    "tomato spider mites two-spotted spider mite": _item(
        "A two-spotted spider mite infestation rather than a fungal or bacterial disease. Hot, dry conditions often favor rapid mite multiplication and feeding damage.",
        [
            "Inspect leaf undersides regularly, especially during hot dry weather.",
            "Maintain adequate plant moisture and reduce drought stress.",
            "Use integrated pest-management guidance and preserve beneficial predators where practical.",
        ],
    ),
    "tomato target spot": _item(
        "A fungal leaf-spot disease associated with Corynespora cassiicola. Spores spread by air and water, and warm humid conditions favor disease.",
        [
            "Improve airflow and reduce prolonged leaf wetness.",
            "Remove heavily affected foliage and manage crop residue where appropriate.",
            "Avoid unnecessary splashing of water onto foliage.",
        ],
    ),
    "tomato tomato yellow leaf curl virus": _item(
        "A viral disease primarily spread by whiteflies. Infected plants and whiteflies can help move the virus between plants.",
        [
            "Use healthy/certified transplants and resistant varieties when available.",
            "Monitor and manage whiteflies using integrated pest-management guidance.",
            "Remove strongly symptomatic plants where appropriate to reduce sources of infection.",
        ],
    ),
    "tomato tomato mosaic virus": _item(
        "A virus that can spread through infected seed, plant sap and mechanical contact with hands, tools or plants.",
        [
            "Use clean/certified seed and healthy transplants.",
            "Disinfect tools and wash hands before handling plants when practical.",
            "Remove infected plants where appropriate and avoid saving seed from symptomatic plants.",
        ],
    ),
    "tomato healthy": _item(
        "The model's top class is healthy; no disease pattern was classified from the image.",
        [
            "Continue routine monitoring.",
            "Maintain sanitation, airflow and appropriate irrigation.",
            "Re-scan new or changing leaves when symptoms appear.",
        ],
    ),
    # Mango
    "mango anthracnose": _item(
        "A fungal disease caused by Colletotrichum species. Spores spread by rain and wet plant surfaces; warm, humid conditions favor infection.",
        [
            "Maintain canopy airflow and reduce prolonged wetness.",
            "Remove infected or mummified plant material where appropriate.",
            "Use healthy planting material and follow local orchard-disease guidance.",
        ],
    ),
    "mango bacterial canker": _item(
        "A bacterial disease associated with Xanthomonas species. It can spread through rain splash, wounds and infected plant material.",
        [
            "Use healthy planting material and clean pruning tools.",
            "Avoid unnecessary wounds and reduce spread through wet foliage handling.",
            "Remove severely affected material according to local orchard guidance.",
        ],
    ),
    "mango cutting weevil": _item(
        "An insect pest pattern associated with weevil feeding or damage to mango plant tissue. Infestation depends on the presence and life cycle of the pest in the orchard.",
        [
            "Inspect new growth and damaged tissues regularly.",
            "Remove and destroy visibly infested material where appropriate.",
            "Use local integrated pest-management recommendations for confirmed infestations.",
        ],
    ),
    "mango die back": _item(
        "A branch die-back condition can be associated with fungal pathogens, wounds and plant stress. Infection often enters through damaged tissue and is favored by poor sanitation or stressful conditions.",
        [
            "Prune dead or diseased branches with clean tools where appropriate.",
            "Reduce plant stress with suitable irrigation and nutrition.",
            "Maintain orchard sanitation and protect pruning/wound sites according to local guidance.",
        ],
    ),
    "mango gall midge": _item(
        "An insect-pest pattern in which gall-midge larvae feed on susceptible plant tissue after adults lay eggs. Damage is more likely when pest populations build up on new growth.",
        [
            "Inspect tender shoots and new growth regularly.",
            "Remove severely infested plant parts where appropriate.",
            "Use locally recommended integrated pest-management practices for confirmed infestations.",
        ],
    ),
    "mango healthy": _item(
        "The model's top class is healthy; no disease or pest pattern was classified from the image.",
        [
            "Continue routine orchard scouting.",
            "Maintain sanitation, canopy airflow and balanced irrigation.",
            "Re-scan new or changing leaves and shoots when symptoms appear.",
        ],
    ),
    "mango powdery mildew": _item(
        "A fungal disease caused by Oidium mangiferae. Spores spread through air and infection is favored by suitable humidity, mild temperatures and susceptible flowering/new tissue.",
        [
            "Maintain canopy airflow and avoid overly dense growth.",
            "Monitor flowering and young tissue closely during favorable periods.",
            "Use tolerant varieties and local disease-management guidance where available.",
        ],
    ),
    "mango sooty mould": _item(
        "A dark fungal coating often develops on honeydew produced by sap-sucking insects such as scales, mealybugs or aphids. The mould grows on the sticky surface rather than directly causing the original insect problem.",
        [
            "Scout for honeydew-producing sap-sucking insects and manage them through integrated pest management.",
            "Improve canopy airflow and reduce dense foliage.",
            "Address the underlying pest pressure rather than treating the mould alone.",
        ],
    ),
}


def _key(label: str | None) -> str:
    value = str(label or "").strip().lower()
    value = value.replace(" → ", "___").replace("___", " ")
    value = value.replace("_", " ")
    value = " ".join(value.split())
    return value


def get_disease_guidance(label: str | None) -> dict[str, Any]:
    cleaned = str(label or "").strip()
    key = _key(cleaned)
    for name, data in GUIDANCE.items():
        if name in key or key in name:
            return {
                "condition": cleaned or "Unknown condition",
                **data,
                "specific": True,
            }

    # Conservative fallback for labels outside the current knowledge base.
    return {
        "condition": cleaned or "Unknown condition",
        "how_it_occurs": (
            "The image classifier detected a plant-condition pattern, but the current "
            "guidance library does not have crop-specific causal information for this label."
        ),
        "prevention": [
            "Monitor several plants/leaves rather than relying on one image.",
            "Maintain good sanitation, airflow and appropriate irrigation.",
            "Confirm the condition with crop-specific agricultural or plant-pathology guidance before taking treatment action.",
        ],
        "note": "Crop-specific guidance is unavailable for this label.",
        "specific": False,
    }
