"""
Detects sales techniques used in call transcripts.
"""

import re

TECHNIQUES = {
    "needs_discovery": [
        r"(romantic|anniversary|family|traveling with)",
        r"(what are you looking for|tell me (more )?about)",
        r"(how (many|long)|what dates)",
        r"(preference|what kind of)",
    ],
    "upselling": [
        r"(one step up|step above|upgrade)",
        r"(add(ing)?|include|shall i include)",
        r"(pairs|goes) (really )?well with",
        r"(only \$\d+|just \$\d+) more",
        r"(package|bundle)",
    ],
    "objection_handling": [
        r"i (completely |fully )?understand",
        r"let me see what i can do",
        r"(bring|comes?) (that |it )down to",
        r"(special|waive|courtesy|discount)",
        r"(does that work|would that help)",
    ],
    "closing": [
        r"(shall i|let me) (get|book|set) (that|everything)",
        r"(get that booked|i'll get that set up)",
        r"(fantastic|wonderful|perfect)!? i('ll| will)",
        r"can i get your (name|contact|info)",
    ],
    "value_framing": [
        r"(most popular|highlight of|best value)",
        r"(guests consistently|a lot of our guests)",
        r"(designed for|perfect for|made for)",
        r"(includes|included|all the amenities)",
        r"(only|just) \$\d+ (more|per)",
    ],
    "rapport_building": [
        r"(how special|congratulations|how lovely)",
        r"(excited for you|so happy|wonderful)",
        r"(anniversary|special occasion)",
        r"(makes sense|completely understand)",
    ],
}


def detect_techniques(transcript: str) -> dict:
    """
    Returns a techniques dict with individual scores and an overall
    technique_score (0-100).
    """
    text = transcript.lower()
    results = {}
    total_score = 0

    for technique, patterns in TECHNIQUES.items():
        hits = sum(1 for p in patterns if re.search(p, text))
        pct = round(hits / len(patterns), 3)
        results[technique] = {
            "hits": hits,
            "max": len(patterns),
            "score": round(pct * 100, 1),
        }
        total_score += pct

    technique_score = round((total_score / len(TECHNIQUES)) * 100, 1)
    results["technique_score"] = technique_score

    # Flags for coaching
    missing = [k for k, v in results.items()
               if k != "technique_score" and v["score"] < 25]
    results["missing_techniques"] = missing

    return results
