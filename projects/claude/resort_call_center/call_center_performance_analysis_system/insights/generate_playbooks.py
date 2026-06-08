"""
Generates coaching playbooks from top-performer patterns.
"""

import os
import csv
from tabulate import tabulate

BASE_DIR = os.path.join(os.path.dirname(__file__), "..", "data")


def load_csv(filename):
    path = os.path.join(BASE_DIR, filename)
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def avg(rows, key):
    vals = [float(r[key]) for r in rows if r.get(key) not in ("", None)]
    return round(sum(vals) / len(vals), 1) if vals else 0.0


TECHNIQUE_ADVICE = {
    "knowledge_score": {
        "what": "Know your product cold.",
        "how": [
            "Memorize all suite names, prices, and what's included.",
            "Practice answering the 10 most common customer questions without hesitation.",
            "Lead with specific details — 'private balcony' beats 'nice view'.",
        ],
        "example": "Instead of: 'We have different rooms.' → Say: 'Our Marina Suite at $380 includes a direct marina view, upgraded bath amenities, and private lounge access.'",
    },
    "niceness_score": {
        "what": "Be warm, human, and personal.",
        "how": [
            "Use the customer's name at least twice during the call.",
            "Acknowledge emotional context: anniversaries, family trips, special occasions.",
            "Say 'I completely understand' before handling any objection.",
            "Close with genuine excitement — 'I'm so excited for you!'",
        ],
        "example": "Instead of: 'Ok, what dates.' → Say: 'Wonderful! And what dates are you thinking, [Name]? I'd love to help you find the perfect fit.'",
    },
    "upselling": {
        "what": "Always offer an upgrade or add-on.",
        "how": [
            "After the customer shows interest in a room, always mention one add-on.",
            "Frame add-ons as 'it pairs really well with' — not as a pitch.",
            "Use the phrase 'it's only $X more' to make the value clear.",
        ],
        "example": "After booking Marina Suite: 'A lot of our guests add the water sports package — kayaking, paddleboarding, snorkeling — for just $120 for the whole stay. It pairs really well with the marina view.'",
    },
    "objection_handling": {
        "what": "Turn 'no' into a conversation, not a dead end.",
        "how": [
            "Acknowledge the concern first — never argue.",
            "Offer a concrete alternative: midweek rate, waived fee, smaller package.",
            "End with 'Does that work better for you?' to re-engage.",
        ],
        "example": "Customer: 'That's a bit over budget.' → Agent: 'I completely understand. Let me see what I can do — we have a midweek special that brings it down to $380, and I can waive the resort fee as a courtesy. Does that work better?'",
    },
    "closing": {
        "what": "Ask for the sale — don't wait for the customer to volunteer.",
        "how": [
            "When the customer says 'that sounds good', immediately say 'Let me get that booked for you right now.'",
            "Use assumptive language: 'Shall I include that?' instead of 'Would you like that?'",
            "Never end with 'think about it' — always schedule a next step.",
        ],
        "example": "Customer: 'Yes, let's do it!' → Agent: 'Fantastic! Let me get that booked right now. Can I get your name and best contact email?'",
    },
    "value_framing": {
        "what": "Sell the experience, not just the price.",
        "how": [
            "Always say what's included before saying the price.",
            "Use social proof: 'Our guests consistently say it's the highlight of their stay.'",
            "Connect features to the customer's stated reason for the trip.",
        ],
        "example": "Instead of: 'The suite is $450.' → Say: 'The Ocean Bliss Suite starts at $450 and includes champagne on arrival, a private balcony, and a couples' spa credit — it's our most popular anniversary package.'",
    },
}


def generate(output_to_console=True):
    patterns = load_csv("conversation_patterns.csv")
    metrics = load_csv("agent_metrics.csv")

    for m in metrics:
        m["conversion_rate"] = float(m["conversion_rate"])
        m["avg_order_value"] = float(m["avg_order_value"])
        m["composite"] = m["conversion_rate"] * m["avg_order_value"]

    metrics.sort(key=lambda x: x["composite"], reverse=True)
    n = len(metrics)
    top_ids    = {m["agent_id"] for m in metrics[:max(1, n // 5)]}
    bottom_ids = {m["agent_id"] for m in metrics[n - max(1, n // 5):]}

    top_calls    = [p for p in patterns if p["agent_id"] in top_ids]
    bottom_calls = [p for p in patterns if p["agent_id"] in bottom_ids]

    score_keys = [
        "knowledge_score", "niceness_score", "technique_score",
        "upselling", "objection_handling", "closing", "value_framing",
    ]

    gaps = {}
    for key in score_keys:
        gaps[key] = round(avg(top_calls, key) - avg(bottom_calls, key), 1)

    # Focus playbook on the three biggest gaps
    priority = sorted(gaps.items(), key=lambda x: x[1], reverse=True)[:3]

    if output_to_console:
        print("\n" + "=" * 60)
        print("  COACHING PLAYBOOK — CLOSE THE GAP")
        print("=" * 60)

        print("\nWhere bottom agents fall furthest behind top agents:\n")
        gap_rows = [[k.replace("_", " ").title(), avg(bottom_calls, k), avg(top_calls, k), f"+{v}"]
                    for k, v in priority]
        print(tabulate(gap_rows, headers=["Dimension", "Bottom Avg", "Top Avg", "Gap"],
                       tablefmt="simple"))

        for rank, (key, gap) in enumerate(priority, 1):
            advice = TECHNIQUE_ADVICE.get(key)
            if not advice:
                continue
            print(f"\n--- #{rank} Priority: {key.replace('_', ' ').title()} (Gap: +{gap}) ---")
            print(f"Focus: {advice['what']}")
            print("Action steps:")
            for step in advice["how"]:
                print(f"  • {step}")
            print(f"Script example:")
            print(f"  {advice['example']}")

        print("\n" + "=" * 60)
        print("  GOLDEN RULES (from top agents, every call)")
        print("=" * 60)
        print("  1. Open warm and by name")
        print("  2. Discover WHY they're calling (occasion, group size, dates)")
        print("  3. Present the right suite with specifics — not just prices")
        print("  4. Add an upsell or package before asking for the sale")
        print("  5. Handle every objection with an alternative, not silence")
        print("  6. Close assumptively — 'Let me get that booked right now'")
        print("  7. End with genuine excitement")


if __name__ == "__main__":
    generate()
