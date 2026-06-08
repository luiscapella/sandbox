"""
Generates a self-contained HTML report with:
  - Executive summary (top vs bottom stats)
  - All agents ranked with their 3 scores
  - Per-agent scorecards with best & worst call excerpts
  - Coaching playbook
  - Embedded charts (no external dependencies at render time)
"""

import os
import csv
import base64
import io
from datetime import datetime

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns

BASE_DIR    = os.path.join(os.path.dirname(__file__), "..", "data")
REPORTS_DIR = os.path.dirname(__file__)

# ---------------------------------------------------------------------------
# Data helpers
# ---------------------------------------------------------------------------

def load_csv(filename):
    path = os.path.join(BASE_DIR, filename)
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def avg(rows, key):
    vals = [float(r[key]) for r in rows if r.get(key) not in ("", None)]
    return round(sum(vals) / len(vals), 1) if vals else 0.0


def fig_to_b64(fig):
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=130, bbox_inches="tight")
    plt.close(fig)
    buf.seek(0)
    return base64.b64encode(buf.read()).decode()


# ---------------------------------------------------------------------------
# Chart generators
# ---------------------------------------------------------------------------

TIER_COLORS = {"top": "#22c55e", "middle": "#f59e0b", "bottom": "#ef4444"}

def chart_agent_scores(agents_data):
    """Bar chart: knowledge / niceness / technique per agent (sorted by composite)."""
    names  = [a["name"].split()[0] + " " + a["name"].split()[1][0] + "." for a in agents_data]
    ks     = [a["knowledge_score"] for a in agents_data]
    ns     = [a["niceness_score"]  for a in agents_data]
    ts     = [a["technique_score"] for a in agents_data]
    colors = [TIER_COLORS[a["segment"]] for a in agents_data]

    x = range(len(names))
    fig, ax = plt.subplots(figsize=(14, 5))
    w = 0.28
    bars_k = ax.bar([i - w for i in x], ks, w, label="Knowledge",  color="#3b82f6", alpha=0.85)
    bars_n = ax.bar([i     for i in x], ns, w, label="Niceness",   color="#a855f7", alpha=0.85)
    bars_t = ax.bar([i + w for i in x], ts, w, label="Technique",  color="#f97316", alpha=0.85)

    ax.set_xticks(list(x))
    ax.set_xticklabels(names, rotation=45, ha="right", fontsize=8)
    ax.set_ylim(0, 115)
    ax.set_ylabel("Score (0–100)")
    ax.set_title("Agent Scores: Knowledge · Niceness · Technique  (green=top · yellow=mid · red=bottom)")
    ax.legend(loc="upper right")

    # Tier color dot on x-axis labels
    for tick, color in zip(ax.get_xticklabels(), colors):
        tick.set_color(color)

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    fig.tight_layout()
    return fig_to_b64(fig)


def chart_conversion_vs_niceness(agents_data):
    fig, ax = plt.subplots(figsize=(7, 5))
    for a in agents_data:
        color = TIER_COLORS[a["segment"]]
        ax.scatter(a["niceness_score"], float(a["conversion_rate"]) * 100,
                   color=color, s=80, alpha=0.85)
        ax.annotate(a["name"].split()[0], (a["niceness_score"], float(a["conversion_rate"]) * 100),
                    fontsize=7, alpha=0.7, xytext=(3, 3), textcoords="offset points")

    ax.set_xlabel("Niceness Score")
    ax.set_ylabel("Conversion Rate (%)")
    ax.set_title("Niceness Score vs Conversion Rate")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    patches = [mpatches.Patch(color=c, label=t.capitalize()) for t, c in TIER_COLORS.items()]
    ax.legend(handles=patches)
    fig.tight_layout()
    return fig_to_b64(fig)


def chart_aov_distribution(agents_data):
    top_aov = [float(a["avg_order_value"]) for a in agents_data if a["segment"] == "top"]
    mid_aov = [float(a["avg_order_value"]) for a in agents_data if a["segment"] == "middle"]
    bot_aov = [float(a["avg_order_value"]) for a in agents_data if a["segment"] == "bottom"]

    fig, ax = plt.subplots(figsize=(7, 5))
    data    = [bot_aov, mid_aov, top_aov]
    labels  = ["Bottom", "Middle", "Top"]
    colors  = [TIER_COLORS["bottom"], TIER_COLORS["middle"], TIER_COLORS["top"]]

    bp = ax.boxplot(data, patch_artist=True, labels=labels)
    for patch, color in zip(bp["boxes"], colors):
        patch.set_facecolor(color)
        patch.set_alpha(0.7)

    ax.set_ylabel("Avg Order Value ($)")
    ax.set_title("AOV Distribution by Performance Tier")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    fig.tight_layout()
    return fig_to_b64(fig)


def chart_technique_radar(top_avg, bot_avg):
    """Spider chart comparing top vs bottom agents on technique sub-scores."""
    labels   = ["Upselling", "Objection\nHandling", "Closing", "Value\nFraming", "Rapport\nBuilding", "Needs\nDiscovery"]
    top_vals = [top_avg.get(k, 0) for k in ["upselling","objection_handling","closing","value_framing","rapport_building","needs_discovery"]]
    bot_vals = [bot_avg.get(k, 0) for k in ["upselling","objection_handling","closing","value_framing","rapport_building","needs_discovery"]]

    n = len(labels)
    angles = [i * 2 * 3.14159 / n for i in range(n)] + [0]
    top_vals += [top_vals[0]]
    bot_vals += [bot_vals[0]]

    fig, ax = plt.subplots(figsize=(6, 5), subplot_kw=dict(polar=True))
    ax.plot(angles, top_vals, "o-", color="#22c55e", linewidth=2, label="Top Agents")
    ax.fill(angles, top_vals, alpha=0.15, color="#22c55e")
    ax.plot(angles, bot_vals, "o-", color="#ef4444", linewidth=2, label="Bottom Agents")
    ax.fill(angles, bot_vals, alpha=0.15, color="#ef4444")

    ax.set_thetagrids([a * 180 / 3.14159 for a in angles[:-1]], labels, fontsize=9)
    ax.set_ylim(0, 100)
    ax.set_title("Sales Technique Breakdown\nTop vs Bottom Agents", pad=20)
    ax.legend(loc="upper right", bbox_to_anchor=(1.3, 1.1))
    fig.tight_layout()
    return fig_to_b64(fig)


# ---------------------------------------------------------------------------
# Per-agent call excerpts
# ---------------------------------------------------------------------------

def get_call_excerpts(agent_id, patterns, transcripts_map):
    agent_calls = [p for p in patterns if p["agent_id"] == agent_id]
    if not agent_calls:
        return None, None

    def composite(p):
        return (float(p["knowledge_score"]) +
                float(p["niceness_score"]) +
                float(p["technique_score"])) / 3

    best  = max(agent_calls, key=composite)
    worst = min(agent_calls, key=composite)

    def excerpt(call, max_lines=12):
        text = transcripts_map.get(call["call_id"], "")
        lines = text.strip().split("\n")
        snip  = "\n".join(lines[:max_lines])
        if len(lines) > max_lines:
            snip += f"\n... ({len(lines) - max_lines} more lines)"
        return snip

    return excerpt(best), excerpt(worst)


# ---------------------------------------------------------------------------
# Score bar (inline HTML)
# ---------------------------------------------------------------------------

def score_bar(score, color):
    s = float(score)
    return (
        f'<div style="display:flex;align-items:center;gap:8px">'
        f'<div style="width:120px;background:#e5e7eb;border-radius:4px;height:10px">'
        f'<div style="width:{s}%;background:{color};height:10px;border-radius:4px"></div></div>'
        f'<span style="font-weight:600">{s}</span></div>'
    )


def tier_badge(segment):
    colors = {"top": "#dcfce7", "middle": "#fef9c3", "bottom": "#fee2e2"}
    text   = {"top": "TOP",     "middle": "MIDDLE",  "bottom": "BOTTOM"}
    border = {"top": "#22c55e", "middle": "#f59e0b", "bottom": "#ef4444"}
    return (f'<span style="background:{colors[segment]};border:1px solid {border[segment]};'
            f'color:{border[segment]};padding:2px 8px;border-radius:12px;font-size:0.75rem;'
            f'font-weight:700">{text[segment]}</span>')


# ---------------------------------------------------------------------------
# HTML template
# ---------------------------------------------------------------------------

HTML_TEMPLATE = """\
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Call Center Performance Report</title>
<style>
  *, *::before, *::after {{ box-sizing: border-box; }}
  body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
         margin: 0; background: #f8fafc; color: #1e293b; }}
  .header {{ background: linear-gradient(135deg, #1e40af 0%, #7c3aed 100%);
             color: white; padding: 2rem 2.5rem; }}
  .header h1 {{ margin: 0 0 .25rem; font-size: 1.8rem; }}
  .header p  {{ margin: 0; opacity: .8; font-size: .9rem; }}
  .container {{ max-width: 1200px; margin: 0 auto; padding: 2rem; }}
  h2 {{ font-size: 1.3rem; color: #1e40af; border-bottom: 2px solid #e2e8f0;
        padding-bottom: .5rem; margin-top: 2.5rem; }}
  h3 {{ font-size: 1rem; color: #374151; margin: .75rem 0 .4rem; }}
  .stat-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(180px,1fr));
                gap: 1rem; margin: 1rem 0; }}
  .stat-card {{ background: white; border-radius: 10px; padding: 1.2rem;
                box-shadow: 0 1px 4px rgba(0,0,0,.08); text-align: center; }}
  .stat-card .value {{ font-size: 1.8rem; font-weight: 700; }}
  .stat-card .label {{ font-size: .8rem; color: #64748b; margin-top: .2rem; }}
  .top    .value {{ color: #16a34a; }}
  .middle .value {{ color: #d97706; }}
  .bottom .value {{ color: #dc2626; }}
  .charts {{ display: grid; grid-template-columns: 1fr 1fr; gap: 1.5rem; margin: 1rem 0; }}
  .charts img, .chart-full img {{ width: 100%; border-radius: 8px; background: white;
                                   padding: .5rem; box-shadow: 0 1px 4px rgba(0,0,0,.08); }}
  .chart-full {{ margin: 1rem 0; }}
  table {{ width: 100%; border-collapse: collapse; background: white;
           border-radius: 10px; overflow: hidden;
           box-shadow: 0 1px 4px rgba(0,0,0,.08); font-size: .88rem; }}
  th {{ background: #1e40af; color: white; padding: .7rem 1rem; text-align: left; font-weight: 600; }}
  td {{ padding: .65rem 1rem; border-bottom: 1px solid #f1f5f9; }}
  tr:last-child td {{ border-bottom: none; }}
  tr:hover td {{ background: #f8fafc; }}
  .agent-card {{ background: white; border-radius: 10px; padding: 1.5rem;
                 box-shadow: 0 1px 4px rgba(0,0,0,.08); margin-bottom: 1.5rem; }}
  .agent-card-header {{ display: flex; justify-content: space-between;
                         align-items: center; margin-bottom: 1rem; }}
  .agent-card-header h3 {{ margin: 0; font-size: 1.1rem; }}
  .scores-row {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 1rem; margin-bottom: 1rem; }}
  .score-box {{ background: #f8fafc; border-radius: 8px; padding: .75rem; }}
  .score-box .name {{ font-size: .75rem; color: #64748b; margin-bottom: .3rem; }}
  .excerpts {{ display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin-top: 1rem; }}
  .excerpt {{ border-radius: 8px; padding: 1rem; font-size: .82rem; }}
  .excerpt.best  {{ background: #f0fdf4; border-left: 4px solid #22c55e; }}
  .excerpt.worst {{ background: #fff7ed; border-left: 4px solid #f97316; }}
  .excerpt h4 {{ margin: 0 0 .5rem; font-size: .85rem; }}
  .excerpt pre {{ margin: 0; white-space: pre-wrap; word-break: break-word;
                  font-family: inherit; font-size: .8rem; color: #374151; }}
  .playbook {{ background: white; border-radius: 10px; padding: 1.5rem;
               box-shadow: 0 1px 4px rgba(0,0,0,.08); }}
  .rule {{ background: #eff6ff; border-left: 4px solid #3b82f6;
           padding: .6rem 1rem; margin: .5rem 0; border-radius: 0 6px 6px 0;
           font-size: .9rem; }}
  .gap-item {{ background: #faf5ff; border: 1px solid #e9d5ff; border-radius: 8px;
               padding: 1rem; margin-bottom: 1rem; }}
  .gap-item .title {{ font-weight: 700; color: #7c3aed; margin-bottom: .3rem; }}
  .gap-item .example {{ background: white; border-radius: 6px; padding: .6rem;
                         font-size: .82rem; margin-top: .5rem; color: #374151;
                         border: 1px solid #e9d5ff; }}
  .gap-item ul {{ margin: .3rem 0 0; padding-left: 1.2rem; font-size: .88rem; }}
  footer {{ text-align: center; padding: 1.5rem; font-size: .8rem; color: #94a3b8; }}
</style>
</head>
<body>

<div class="header">
  <h1>Call Center Performance Report</h1>
  <p>Resort Call Center Analysis · Generated {date}</p>
</div>

<div class="container">

  <!-- ===== EXECUTIVE SUMMARY ===== -->
  <h2>Executive Summary</h2>
  <div class="stat-grid">
    <div class="stat-card top">
      <div class="value">{top_conv}%</div>
      <div class="label">Top Agent Conversion Rate</div>
    </div>
    <div class="stat-card bottom">
      <div class="value">{bot_conv}%</div>
      <div class="label">Bottom Agent Conversion Rate</div>
    </div>
    <div class="stat-card top">
      <div class="value">${top_aov}</div>
      <div class="label">Top Agent Avg Order Value</div>
    </div>
    <div class="stat-card bottom">
      <div class="value">${bot_aov}</div>
      <div class="label">Bottom Agent Avg Order Value</div>
    </div>
    <div class="stat-card top">
      <div class="value">{top_sat}</div>
      <div class="label">Top Agent Avg Satisfaction</div>
    </div>
    <div class="stat-card bottom">
      <div class="value">{bot_sat}</div>
      <div class="label">Bottom Agent Avg Satisfaction</div>
    </div>
  </div>

  <!-- ===== CHARTS ===== -->
  <h2>Performance Charts</h2>
  <div class="chart-full"><img src="data:image/png;base64,{chart_scores}" alt="Agent Scores"></div>
  <div class="charts">
    <img src="data:image/png;base64,{chart_scatter}" alt="Niceness vs Conversion">
    <img src="data:image/png;base64,{chart_aov}" alt="AOV Distribution">
  </div>
  <div class="charts">
    <img src="data:image/png;base64,{chart_radar}" alt="Technique Radar">
    <div style="display:flex;align-items:center;justify-content:center;background:white;
                border-radius:8px;padding:1rem;box-shadow:0 1px 4px rgba(0,0,0,.08)">
      <div>
        <h3 style="margin-bottom:1rem">Top 5 Differentiators</h3>
        {top_diffs_html}
      </div>
    </div>
  </div>

  <!-- ===== AGENT LEADERBOARD ===== -->
  <h2>Agent Leaderboard</h2>
  <table>
    <thead>
      <tr>
        <th>#</th><th>Agent</th><th>Tier</th><th>Conversion</th>
        <th>AOV</th><th>Satisfaction</th><th>Knowledge</th><th>Niceness</th><th>Technique</th>
      </tr>
    </thead>
    <tbody>
      {leaderboard_rows}
    </tbody>
  </table>

  <!-- ===== PER-AGENT SCORECARDS ===== -->
  <h2>Agent Scorecards &amp; Call Excerpts</h2>
  {agent_cards}

  <!-- ===== COACHING PLAYBOOK ===== -->
  <h2>Coaching Playbook</h2>
  <div class="playbook">
    <h3>Golden Rules (what top agents do on every call)</h3>
    {golden_rules_html}
    <h3 style="margin-top:1.5rem">Priority Gaps to Close</h3>
    {gap_items_html}
  </div>

</div>
<footer>Call Center Performance Analysis System · {date}</footer>
</body>
</html>
"""

TECHNIQUE_ADVICE = {
    "value_framing": {
        "label": "Value Framing",
        "what": "Sell the experience before quoting the price.",
        "how": [
            "Always describe what's included before mentioning the price.",
            "Use social proof: 'Our guests consistently say it's the highlight of their stay.'",
            "Connect features directly to the customer's reason for calling.",
        ],
        "example": "Instead of: 'The suite is $450.' → 'The Ocean Bliss Suite starts at $450 and includes champagne on arrival, a private balcony, and a couples' spa credit — it's our most popular anniversary package.'",
    },
    "niceness_score": {
        "label": "Warmth & Niceness",
        "what": "Be warm, human, and personal on every call.",
        "how": [
            "Use the customer's name at least twice.",
            "Acknowledge emotional context: anniversaries, family trips, special occasions.",
            "Open with energy: 'How can I make your day amazing?'",
            "Close with genuine excitement: 'I'm so excited for you!'",
        ],
        "example": "Instead of: 'Ok, what dates.' → 'Wonderful! What dates are you thinking, [Name]? I'd love to help you find the perfect fit.'",
    },
    "upselling": {
        "label": "Upselling",
        "what": "Always offer one upgrade or add-on before closing.",
        "how": [
            "After the customer shows interest, mention one natural add-on.",
            "Frame it as 'it pairs really well with' — not as a sales pitch.",
            "Use 'it's only $X more' to anchor the value.",
        ],
        "example": "'A lot of our guests add the water sports package — kayaking, paddleboarding, snorkeling — for just $120 for the whole stay. It pairs really well with the marina view.'",
    },
    "objection_handling": {
        "label": "Objection Handling",
        "what": "Turn 'no' into a conversation, not a dead end.",
        "how": [
            "Acknowledge the concern first — never argue.",
            "Offer a concrete alternative: midweek rate, waived fee, smaller package.",
            "End with 'Does that work better for you?' to re-engage.",
        ],
        "example": "Customer: 'That's over budget.' → 'I completely understand. Let me see what I can do — we have a midweek special at $380, and I can waive the resort fee. Does that work better?'",
    },
    "closing": {
        "label": "Closing Techniques",
        "what": "Ask for the sale — don't wait for the customer.",
        "how": [
            "When the customer says 'that sounds good', say 'Let me get that booked right now.'",
            "Use assumptive language: 'Shall I include that?' not 'Would you like that?'",
            "Never end with 'think about it' — always offer a next step.",
        ],
        "example": "Customer: 'Yes, let's do it!' → 'Fantastic! Let me get that booked right now. Can I get your name and best email?'",
    },
    "rapport_building": {
        "label": "Rapport Building",
        "what": "Establish a human connection before selling anything.",
        "how": [
            "Ask about the occasion or purpose of the trip early.",
            "React emotionally to what customers share ('How special!').",
            "Mirror the customer's tone and energy.",
        ],
        "example": "Customer: 'It's our anniversary.' → 'Oh, how special! Congratulations — let me make sure we get you something truly memorable.'",
    },
}

GOLDEN_RULES = [
    "Open warm and by name — set the tone in the first 10 seconds.",
    "Discover WHY they're calling (occasion, group size, dates) before pitching anything.",
    "Present the right suite with specifics — not just prices.",
    "Add one upsell or package before asking for the sale.",
    "Handle every objection with a concrete alternative, not silence.",
    "Close assumptively — 'Let me get that booked right now.'",
    "End with genuine excitement — customers remember how you made them feel.",
]


# ---------------------------------------------------------------------------
# Main builder
# ---------------------------------------------------------------------------

def build_report():
    agents   = load_csv("agents.csv")
    metrics  = load_csv("agent_metrics.csv")
    patterns = load_csv("conversation_patterns.csv")
    trans_raw = load_csv("call_transcripts.csv")
    transcripts_map = {r["call_id"]: r["transcript"] for r in trans_raw}

    # Merge and sort
    metrics_by_id = {m["agent_id"]: m for m in metrics}
    for a in agents:
        a.update(metrics_by_id.get(a["agent_id"], {}))
        a["conversion_rate"] = float(a.get("conversion_rate", 0))
        a["avg_order_value"] = float(a.get("avg_order_value", 0))
        a["avg_satisfaction"] = float(a.get("avg_satisfaction", 0))
        a["composite"] = round(a["conversion_rate"] * a["avg_order_value"], 2)

    agents.sort(key=lambda x: x["composite"], reverse=True)
    n = len(agents)
    for i, a in enumerate(agents):
        a["segment"] = "top" if i < n // 5 else ("bottom" if i >= n * 4 // 5 else "middle")

    # Per-agent pattern scores
    pattern_by_agent = {}
    for p in patterns:
        pattern_by_agent.setdefault(p["agent_id"], []).append(p)

    for a in agents:
        calls = pattern_by_agent.get(a["agent_id"], [])
        a["knowledge_score"]    = avg(calls, "knowledge_score")
        a["niceness_score"]     = avg(calls, "niceness_score")
        a["technique_score"]    = avg(calls, "technique_score")
        a["upselling"]          = avg(calls, "upselling")
        a["objection_handling"] = avg(calls, "objection_handling")
        a["closing"]            = avg(calls, "closing")
        a["value_framing"]      = avg(calls, "value_framing")
        a["rapport_building"]   = avg(calls, "rapport_building")
        a["needs_discovery"]    = avg(calls, "needs_discovery")

    top    = [a for a in agents if a["segment"] == "top"]
    bottom = [a for a in agents if a["segment"] == "bottom"]

    def seg_avg(seg, key):
        vals = [float(a.get(key, 0)) for a in seg]
        return round(sum(vals) / len(vals), 1) if vals else 0.0

    # ---- Charts ----
    chart_scores  = chart_agent_scores(agents)
    chart_scatter = chart_conversion_vs_niceness(agents)
    chart_aov_b64 = chart_aov_distribution(agents)

    top_tech = {k: seg_avg(top, k)    for k in ["upselling","objection_handling","closing","value_framing","rapport_building","needs_discovery"]}
    bot_tech = {k: seg_avg(bottom, k) for k in top_tech}
    chart_radar_b64 = chart_technique_radar(top_tech, bot_tech)

    # ---- Top differentiators ----
    diff_keys = [
        ("avg_order_value", "Avg Order Value ($)"),
        ("value_framing",   "Value Framing"),
        ("rapport_building","Rapport Building"),
        ("niceness_score",  "Niceness Score"),
        ("upselling",       "Upselling"),
        ("closing",         "Closing Techniques"),
    ]
    diffs = sorted(
        [(label, seg_avg(top, k) - seg_avg(bottom, k)) for k, label in diff_keys],
        key=lambda x: x[1], reverse=True
    )[:5]
    top_diffs_html = "".join(
        f'<div style="display:flex;justify-content:space-between;padding:.4rem .6rem;'
        f'background:#f0fdf4;border-radius:6px;margin:.3rem 0;font-size:.88rem">'
        f'<span>{label}</span><strong style="color:#16a34a">+{round(d,1)}</strong></div>'
        for label, d in diffs
    )

    # ---- Leaderboard ----
    lb_rows = ""
    for rank, a in enumerate(agents, 1):
        badge = tier_badge(a["segment"])
        lb_rows += (
            f'<tr>'
            f'<td>{rank}</td>'
            f'<td><strong>{a["name"]}</strong></td>'
            f'<td>{badge}</td>'
            f'<td>{round(a["conversion_rate"]*100,1)}%</td>'
            f'<td>${a["avg_order_value"]}</td>'
            f'<td>{a["avg_satisfaction"]}</td>'
            f'<td>{score_bar(a["knowledge_score"], "#3b82f6")}</td>'
            f'<td>{score_bar(a["niceness_score"],  "#a855f7")}</td>'
            f'<td>{score_bar(a["technique_score"], "#f97316")}</td>'
            f'</tr>'
        )

    # ---- Per-agent cards ----
    agent_cards = ""
    for a in agents:
        best_excerpt, worst_excerpt = get_call_excerpts(a["agent_id"], patterns, transcripts_map)
        excerpts_html = ""
        if best_excerpt and worst_excerpt:
            excerpts_html = (
                f'<div class="excerpts">'
                f'<div class="excerpt best">'
                f'<h4>✅ Best Call (highest composite score)</h4>'
                f'<pre>{best_excerpt}</pre></div>'
                f'<div class="excerpt worst">'
                f'<h4>⚠️ Worst Call (lowest composite score)</h4>'
                f'<pre>{worst_excerpt}</pre></div>'
                f'</div>'
            )

        agent_cards += (
            f'<div class="agent-card">'
            f'<div class="agent-card-header">'
            f'<h3>{a["name"]}</h3>'
            f'{tier_badge(a["segment"])}'
            f'</div>'
            f'<div style="font-size:.85rem;color:#64748b;margin-bottom:.75rem">'
            f'Conversion: <strong>{round(a["conversion_rate"]*100,1)}%</strong> &nbsp;|&nbsp; '
            f'AOV: <strong>${a["avg_order_value"]}</strong> &nbsp;|&nbsp; '
            f'Satisfaction: <strong>{a["avg_satisfaction"]}</strong> &nbsp;|&nbsp; '
            f'Experience: <strong>{a.get("experience_years","?")} yrs</strong>'
            f'</div>'
            f'<div class="scores-row">'
            f'<div class="score-box"><div class="name">Knowledge</div>'
            f'{score_bar(a["knowledge_score"], "#3b82f6")}</div>'
            f'<div class="score-box"><div class="name">Niceness</div>'
            f'{score_bar(a["niceness_score"], "#a855f7")}</div>'
            f'<div class="score-box"><div class="name">Technique</div>'
            f'{score_bar(a["technique_score"], "#f97316")}</div>'
            f'</div>'
            f'{excerpts_html}'
            f'</div>'
        )

    # ---- Playbook ----
    golden_rules_html = "".join(f'<div class="rule">{i+1}. {r}</div>' for i, r in enumerate(GOLDEN_RULES))

    # Gap priorities — top 3 technique gaps
    gap_keys = ["value_framing","niceness_score","upselling","objection_handling","closing","rapport_building"]
    gaps = sorted(
        [(k, seg_avg(top, k) - seg_avg(bottom, k)) for k in gap_keys],
        key=lambda x: x[1], reverse=True
    )[:3]

    gap_items_html = ""
    for key, gap in gaps:
        advice = TECHNIQUE_ADVICE.get(key)
        if not advice:
            continue
        steps = "".join(f"<li>{s}</li>" for s in advice["how"])
        gap_items_html += (
            f'<div class="gap-item">'
            f'<div class="title">{advice["label"]} — Gap: +{round(gap,1)}</div>'
            f'<div>{advice["what"]}</div>'
            f'<ul>{steps}</ul>'
            f'<div class="example"><strong>Script example:</strong><br>{advice["example"]}</div>'
            f'</div>'
        )

    # ---- Render ----
    html = HTML_TEMPLATE.format(
        date          = datetime.now().strftime("%B %d, %Y"),
        top_conv      = round(seg_avg(top,    "conversion_rate") * 100, 1),
        bot_conv      = round(seg_avg(bottom, "conversion_rate") * 100, 1),
        top_aov       = seg_avg(top,    "avg_order_value"),
        bot_aov       = seg_avg(bottom, "avg_order_value"),
        top_sat       = seg_avg(top,    "avg_satisfaction"),
        bot_sat       = seg_avg(bottom, "avg_satisfaction"),
        chart_scores  = chart_scores,
        chart_scatter = chart_scatter,
        chart_aov     = chart_aov_b64,
        chart_radar   = chart_radar_b64,
        top_diffs_html    = top_diffs_html,
        leaderboard_rows  = lb_rows,
        agent_cards       = agent_cards,
        golden_rules_html = golden_rules_html,
        gap_items_html    = gap_items_html,
    )

    out_path = os.path.join(REPORTS_DIR, "performance_report.html")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"Report generated: {out_path}")
    return out_path


if __name__ == "__main__":
    build_report()
