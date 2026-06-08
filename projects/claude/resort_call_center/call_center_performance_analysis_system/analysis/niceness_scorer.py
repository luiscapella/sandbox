"""
Scores agent warmth, politeness, and empathy based on transcript patterns.
"""

import re

# Warmth & politeness signals
POSITIVE_SIGNALS = [
    (r"\bthank(s| you)\b", 2),
    (r"\bi('m| am) (so |very )?happy to\b", 2),
    (r"\bwonderful\b", 2),
    (r"\bfantastic\b", 2),
    (r"\bspecial\b", 1),
    (r"\bcongratulations\b", 3),
    (r"\bi (completely |fully )?understand\b", 2),
    (r"\bthat makes sense\b", 2),
    (r"\bour (most )?popular\b", 1),
    (r"\bi'(m|ll) (get|take care|help)\b", 1),
    (r"\bperfect\b", 1),
    (r"\bexcited for you\b", 3),
    (r"\bhow (special|lovely|wonderful)\b", 3),
    (r"\blet me see what i can do\b", 2),
    (r"\bcourtesy\b", 2),
    (r"\bamazing\b", 1),
    (r"\blovely\b", 1),
    (r"\bof course\b", 1),
    (r"\babsolutely\b", 1),
    (r"\bhappy to help\b", 2),
]

# Cold, dismissive, or rude signals
NEGATIVE_SIGNALS = [
    (r"\byeah,? hi\b", 3),
    (r"\bwhat do you need\b", 3),
    (r"\bjust hold\b", 3),
    (r"\bok bye\b", 3),
    (r"\bi'll think about it\b", 1),      # customer phrase, not agent
    (r"\bhold please\b", 2),
    (r"\byeah there'?s?\b", 2),
    (r"\byou could ask\b", 2),
    (r"^Agent: Ok\.$", 3),                 # single-word acknowledgment
    (r"\bstuff like that\b", 2),
    (r"\bi don't think so\b", 2),
    (r"\bcall back\b", 2),
]

# Personalization: using the customer's name mid-call
PERSONALIZATION_RE = re.compile(
    r"Agent:.*?,\s+[A-Z][a-z]+[.!?]",   # "..., Sarah!" pattern
)


def _weighted_matches(text, patterns):
    text_lower = text.lower()
    total = 0
    hits = []
    for pattern, weight in patterns:
        if re.search(pattern, text_lower):
            total += weight
            hits.append(pattern)
    return total, hits


def score_niceness(transcript: str) -> dict:
    """
    Returns a niceness_score (0-100) plus a breakdown.
    """
    pos_score, pos_hits = _weighted_matches(transcript, POSITIVE_SIGNALS)
    neg_score, neg_hits = _weighted_matches(transcript, NEGATIVE_SIGNALS)
    personalized = bool(PERSONALIZATION_RE.search(transcript))

    max_positive = sum(w for _, w in POSITIVE_SIGNALS)
    raw = (
        (pos_score / max_positive) * 70 +
        (personalized * 10) +
        max(0, 1 - neg_score / 10) * 20
    )
    score = round(min(100, raw * 100), 1)

    return {
        "niceness_score": score,
        "positive_signals_count": len(pos_hits),
        "negative_signals_count": len(neg_hits),
        "uses_customer_name": personalized,
        "negative_flags": neg_hits[:3],   # top 3 flags for coaching
    }
