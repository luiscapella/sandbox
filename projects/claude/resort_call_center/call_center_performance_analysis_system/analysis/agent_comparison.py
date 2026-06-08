"""
Side-by-side comparison of top vs bottom agents across all scored dimensions.
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


def compare():
    patterns = load_csv("conversation_patterns.csv")
    metrics = load_csv("agent_metrics.csv")

    # Build agent-level aggregates from patterns
    by_agent = {}
    for p in patterns:
        aid = p["agent_id"]
        by_agent.setdefault(aid, []).append(p)

    agent_scores = {}
    for aid, calls in by_agent.items():
        agent_scores[aid] = {
            "knowledge_score":    avg(calls, "knowledge_score"),
            "niceness_score":     avg(calls, "niceness_score"),
            "technique_score":    avg(calls, "technique_score"),
            "upselling":          avg(calls, "upselling"),
            "objection_handling": avg(calls, "objection_handling"),
            "closing":            avg(calls, "closing"),
            "value_framing":      avg(calls, "value_framing"),
            "rapport_building":   avg(calls, "rapport_building"),
        }

    # Merge with business metrics
    for m in metrics:
        m.update(agent_scores.get(m["agent_id"], {}))
        m["conversion_rate"] = float(m["conversion_rate"])
        m["avg_order_value"] = float(m["avg_order_value"])
        m["composite"] = round(m["conversion_rate"] * m["avg_order_value"], 2)

    metrics.sort(key=lambda x: x["composite"], reverse=True)
    n = len(metrics)
    top    = metrics[:max(1, n // 5)]
    bottom = metrics[n - max(1, n // 5):]

    def seg_avg(seg, key):
        return avg(seg, key)

    print("\n=== TOP vs BOTTOM AGENT COMPARISON ===\n")

    comparison_keys = [
        ("conversion_rate",    "Conversion Rate"),
        ("avg_order_value",    "Avg Order Value ($)"),
        ("avg_satisfaction",   "Customer Satisfaction"),
        ("knowledge_score",    "Knowledge Score"),
        ("niceness_score",     "Niceness Score"),
        ("technique_score",    "Overall Technique Score"),
        ("upselling",          "  Upselling"),
        ("objection_handling", "  Objection Handling"),
        ("closing",            "  Closing Techniques"),
        ("value_framing",      "  Value Framing"),
        ("rapport_building",   "  Rapport Building"),
    ]

    rows = []
    for key, label in comparison_keys:
        top_val = seg_avg(top, key)
        bot_val = seg_avg(bottom, key)
        diff = round(top_val - bot_val, 1)
        indicator = "▲" if diff > 0 else ("▼" if diff < 0 else "=")
        rows.append([label, top_val, bot_val, f"{indicator} {abs(diff)}"])

    print(tabulate(rows,
                   headers=["Metric", "Top Agents", "Bottom Agents", "Difference"],
                   tablefmt="rounded_outline"))

    print("\nKey Differentiators (where top outperforms bottom the most):")
    diff_rows = sorted(
        [(label, seg_avg(top, key) - seg_avg(bottom, key))
         for key, label in comparison_keys],
        key=lambda x: x[1], reverse=True
    )[:5]
    for label, diff in diff_rows:
        print(f"  {label}: +{round(diff, 1)}")


if __name__ == "__main__":
    compare()
