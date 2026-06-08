# Call Center Performance Analysis System

A data-driven system to analyze call center calls, identify what top-performing
sales agents do differently, and turn those insights into coaching playbooks for
the rest of the team.

---

## 🎯 The Goal

Figure out **what makes the best agents the best** — then mimic it.

We do this by comparing the highest-performing agents (highest **Average Order
Value** and **conversion rate**) against the lowest performers, and extracting
the concrete behaviors that drive the difference.

The big questions we want to answer:

- Are top agents simply **more knowledgeable** about the product?
- Are they **nicer** — warmer, more empathetic, more personable?
- Do they use specific **sales techniques** (objection handling, upselling, closing)?
- Which combination of these traits actually drives revenue?

---

## 📊 What We Measure

Every agent gets scored on three dimensions, then correlated against their
business results (AOV + conversion).

### 1. Knowledge Score (0–100)
How well does the agent know the product?

| Signal | Example |
|--------|---------|
| Answers technical questions confidently | "Yes, the suite sleeps 6 and includes ocean-view balconies." |
| References specific features/specs | Mentions exact amenities, policies, pricing tiers |
| No hesitation / "let me check" loops | Handles questions directly |
| Proactive suggestions based on needs | "Since you're traveling with kids, the resort pool package is perfect." |

### 2. Niceness Score (0–100)
How warm, polite, and personable is the agent?

**Positive signals (raise the score):**
- Uses the customer's name
- Empathetic phrases — "I understand," "That makes sense"
- Gratitude — "Thank you for your patience"
- Personalized greetings and closings
- Warm, positive tone

**Negative signals (lower the score / raise flags):**
- Abrupt interruptions
- Dismissive language
- Cold, robotic phrasing
- Failure to acknowledge the customer

> Example — high niceness: *"Thank you so much for your patience, Sarah. I
> completely understand, and I'm happy to walk you through the options."*
>
> Example — low niceness: *"Just hold on."*

### 3. Sales Technique Score (0–100)
How effective is the agent's selling approach?

- **Objection handling** — response to "too expensive" / "I need to think about it"
- **Upselling & cross-selling** — moving customers to higher-value packages
- **Question types** — open-ended (discover needs) vs. qualifying (budget/timeline)
  vs. closing (move to sale)
- **Rapport building** — establishing trust and connection
- **Urgency & value framing** — communicating why now, why this

---

## 🏗️ How It Works

```
Sample Data  ─►  Analysis Engine  ─►  Insights & Playbooks  ─►  Reports
 (generated)     (scoring + NLP)      (what top agents do)       (CLI output)
```

### Phase 1 — Data Foundation
Generate realistic sample data with a believable spread of high / medium / low
performers so the whole pipeline can be built and tested before real call data
is plugged in.

| File | Contents |
|------|----------|
| `agents.csv` | Agent profiles (ID, name, experience, region) |
| `calls.csv` | Call records (call ID, agent, customer, duration, timestamp) |
| `call_transcripts.csv` | Full call text |
| `call_outcomes.csv` | Sale made?, order value, satisfaction |
| `agent_metrics.csv` | Aggregated performance (AOV, conversion, etc.) |

### Phase 2 — Analysis Engine
- **Agent profiling** — segment agents into quartiles by AOV & conversion
- **Knowledge scorer** — assess product knowledge
- **Niceness scorer** — assess tone & politeness
- **Technique detector** — identify sales techniques in use
- **Comparison engine** — side-by-side high vs. low performers, with statistical
  testing so differences are real, not noise

### Phase 3 — Insights & Playbooks
- **Playbook generator** — extract repeatable best practices from top agents and
  turn them into coaching guides for everyone else
- **Performance predictor** — model that scores a call/agent and predicts success

### Phase 4 — Reporting (expand later)
- **Report generator** — agent comparison reports & performance summaries
- **CLI tool** (`main.py`) — run analyses and generate reports on demand
- Web dashboard is a future expansion, not part of the first build

---

## 📁 Project Structure

```
call_center_performance_analysis_system/
├── data/
│   ├── agents.csv
│   ├── calls.csv
│   ├── call_transcripts.csv
│   ├── call_outcomes.csv
│   ├── agent_metrics.csv
│   ├── conversation_patterns.csv      # extracted patterns
│   └── generate_sample_data.py
├── analysis/
│   ├── agent_analysis.py
│   ├── pattern_extraction.py          # knowledge, niceness, techniques
│   ├── knowledge_scorer.py
│   ├── niceness_scorer.py
│   ├── technique_detector.py
│   └── agent_comparison.py
├── insights/
│   ├── generate_playbooks.py
│   └── performance_predictor.py
├── reports/
│   └── generate_reports.py
├── main.py
├── requirements.txt
└── README.md
```

---

## 🧰 Tech Stack

| Tool | Purpose |
|------|---------|
| **pandas** | Data manipulation |
| **scikit-learn** | Predictive modeling |
| **nltk / spaCy** | NLP for pattern extraction |
| **matplotlib / seaborn** | Visualization |
| **jinja2** | Report templating |

---

## 🗺️ Build Order

1. Data schema & sample data generator *(foundation)*
2. Agent analysis module *(basic profiling)*
3. Knowledge + niceness scorers
4. Technique detector & pattern extraction
5. Comparison engine *(high vs. low, with significance testing)*
6. Playbook generation *(actionable insights)*
7. Predictive scoring model *(optional / phase 2)*
8. CLI tool *(user interface)*
9. Dashboards *(future expansion)*

---

## ✅ The Payoff

Three clear scores per agent — **Knowledge**, **Niceness**, **Sales Technique** —
mapped against **AOV** and **conversion rate**. That lets you say things like:

> *"Top agents score 85+ on knowledge, 90+ on niceness, and consistently use
> value-framing when closing. Bottom agents are knowledgeable but cold, and rarely
> ask qualifying questions."*

From there, the playbooks write themselves.
