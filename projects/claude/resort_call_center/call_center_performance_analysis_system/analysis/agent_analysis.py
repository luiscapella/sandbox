"""
Loads agent metrics and segments them into performance tiers.
"""

import os
import csv
from tabulate import tabulate

BASE_DIR = os.path.join(os.path.dirname(__file__), "..", "data")


def load_csv(filename):
    path = os.path.join(BASE_DIR, filename)
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def segment_agents(metrics):
    """Sort agents by composite score (conversion * aov) and label tiers."""
    for m in metrics:
        m["conversion_rate"] = float(m["conversion_rate"])
        m["avg_order_value"] = float(m["avg_order_value"])
        m["avg_satisfaction"] = float(m["avg_satisfaction"])
        m["composite"] = round(m["conversion_rate"] * m["avg_order_value"], 2)

    metrics.sort(key=lambda x: x["composite"], reverse=True)
    n = len(metrics)
    for i, m in enumerate(metrics):
        if i < n * 0.2:
            m["segment"] = "top"
        elif i >= n * 0.8:
            m["segment"] = "bottom"
        else:
            m["segment"] = "middle"
    return metrics


def print_summary(metrics):
    top    = [m for m in metrics if m["segment"] == "top"]
    middle = [m for m in metrics if m["segment"] == "middle"]
    bottom = [m for m in metrics if m["segment"] == "bottom"]

    def avg(lst, key):
        return round(sum(x[key] for x in lst) / len(lst), 2) if lst else 0

    print("\n=== AGENT PERFORMANCE SUMMARY ===\n")
    rows = [
        ["Top agents",    len(top),    avg(top, "conversion_rate"),
         avg(top, "avg_order_value"),    avg(top, "avg_satisfaction")],
        ["Middle agents", len(middle), avg(middle, "conversion_rate"),
         avg(middle, "avg_order_value"), avg(middle, "avg_satisfaction")],
        ["Bottom agents", len(bottom), avg(bottom, "conversion_rate"),
         avg(bottom, "avg_order_value"), avg(bottom, "avg_satisfaction")],
    ]
    print(tabulate(rows,
                   headers=["Segment", "Count", "Conv. Rate", "Avg AOV", "Avg Satisfaction"],
                   tablefmt="rounded_outline"))

    print("\nTop Agents:")
    top_rows = [[m["name"], m["conversion_rate"], f"${m['avg_order_value']}", m["avg_satisfaction"]]
                for m in top]
    print(tabulate(top_rows, headers=["Name", "Conversion", "AOV", "Satisfaction"],
                   tablefmt="simple"))

    print("\nBottom Agents:")
    bot_rows = [[m["name"], m["conversion_rate"], f"${m['avg_order_value']}", m["avg_satisfaction"]]
                for m in bottom]
    print(tabulate(bot_rows, headers=["Name", "Conversion", "AOV", "Satisfaction"],
                   tablefmt="simple"))

    return top, middle, bottom


def run():
    metrics = load_csv("agent_metrics.csv")
    metrics = segment_agents(metrics)
    return print_summary(metrics)


if __name__ == "__main__":
    run()
