"""
Scores agent product knowledge based on transcript patterns.
"""

import re

# Phrases that signal confident product knowledge
KNOWLEDGE_SIGNALS = [
    r"\$\d+",                          # mentions specific prices
    r"per night",
    r"(suite|penthouse|garden|marina)", # specific room names
    r"(balcon|ocean.view|pool.view|marina.view)",
    r"(champagne|spa|butler|lounge|plunge pool)",
    r"(breakfast|dinner|water.sport|kayak|paddleboard|snorkel)",
    r"(resort fee|midweek|special|package)",
    r"(king bed|bath|amenities|private)",
]

# Phrases that signal uncertainty / low knowledge
UNCERTAINTY_SIGNALS = [
    r"i('d| would) have to check",
    r"i('m| am) not sure",
    r"i think (it'?s?|around)",
    r"you could ask",
    r"i don't (think|know)",
    r"maybe around",
    r"(stuff|things) like that",
    r"i'd have to look that up",
]

# Phrases indicating proactive product suggestions
PROACTIVE_SIGNALS = [
    r"(designed|perfect|great) for (couples|families|anniversary)",
    r"a lot of our guests",
    r"(pairs|goes) (really )?well with",
    r"i('d| would) (highly )?recommend",
    r"(most popular|highlight of|consistently say)",
    r"shall i include",
    r"let me walk you through",
]


def _count_matches(text, patterns):
    text = text.lower()
    return sum(1 for p in patterns if re.search(p, text))


def score_knowledge(transcript: str) -> dict:
    """
    Returns a knowledge_score (0-100) plus a breakdown.
    """
    knowledge_hits = _count_matches(transcript, KNOWLEDGE_SIGNALS)
    uncertainty_hits = _count_matches(transcript, UNCERTAINTY_SIGNALS)
    proactive_hits = _count_matches(transcript, PROACTIVE_SIGNALS)

    max_knowledge = len(KNOWLEDGE_SIGNALS)
    max_proactive = len(PROACTIVE_SIGNALS)

    raw = (
        (knowledge_hits / max_knowledge) * 50 +
        (proactive_hits / max_proactive) * 30 +
        max(0, 1 - (uncertainty_hits / 3)) * 20
    )
    score = round(min(100, raw * 100), 1)

    return {
        "knowledge_score": score,
        "product_references": knowledge_hits,
        "uncertainty_count": uncertainty_hits,
        "proactive_suggestions": proactive_hits,
    }
