"""
Runs knowledge, niceness, and technique scoring across all transcripts
and writes results to data/conversation_patterns.csv.
"""

import os
import csv
from knowledge_scorer import score_knowledge
from niceness_scorer import score_niceness
from technique_detector import detect_techniques

BASE_DIR = os.path.join(os.path.dirname(__file__), "..", "data")


def load_csv(filename):
    path = os.path.join(BASE_DIR, filename)
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def extract_all():
    transcripts = load_csv("call_transcripts.csv")
    outcomes = {r["call_id"]: r for r in load_csv("call_outcomes.csv")}
    agents = {r["agent_id"]: r for r in load_csv("agents.csv")}

    rows = []
    for t in transcripts:
        cid = t["call_id"]
        aid = t["agent_id"]
        text = t["transcript"]

        k = score_knowledge(text)
        n = score_niceness(text)
        tech = detect_techniques(text)
        outcome = outcomes.get(cid, {})
        agent = agents.get(aid, {})

        rows.append({
            "call_id": cid,
            "agent_id": aid,
            "agent_name": agent.get("name", ""),
            "performance_tier": agent.get("performance_tier", ""),
            "sale_made": outcome.get("sale_made", ""),
            "order_value": outcome.get("order_value", ""),
            "satisfaction": outcome.get("customer_satisfaction", ""),
            # Scores
            "knowledge_score": k["knowledge_score"],
            "niceness_score": n["niceness_score"],
            "technique_score": tech["technique_score"],
            # Breakdowns
            "product_references": k["product_references"],
            "uncertainty_count": k["uncertainty_count"],
            "proactive_suggestions": k["proactive_suggestions"],
            "positive_signals": n["positive_signals_count"],
            "negative_signals": n["negative_signals_count"],
            "uses_customer_name": n["uses_customer_name"],
            "needs_discovery": tech.get("needs_discovery", {}).get("score", 0),
            "upselling": tech.get("upselling", {}).get("score", 0),
            "objection_handling": tech.get("objection_handling", {}).get("score", 0),
            "closing": tech.get("closing", {}).get("score", 0),
            "value_framing": tech.get("value_framing", {}).get("score", 0),
            "rapport_building": tech.get("rapport_building", {}).get("score", 0),
        })

    out_path = os.path.join(BASE_DIR, "conversation_patterns.csv")
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)

    print(f"Extracted patterns for {len(rows)} calls → {out_path}")
    return rows


if __name__ == "__main__":
    extract_all()
