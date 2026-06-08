"""
Generates realistic sample call center data with a believable spread of
high / medium / low performing agents.
"""

import random
import csv
import os
from datetime import datetime, timedelta

random.seed(42)

BASE_DIR = os.path.dirname(__file__)

# ---------------------------------------------------------------------------
# Agent transcript templates
# High performers: warm, knowledgeable, use techniques
# Low performers: cold, hesitant, miss opportunities
# ---------------------------------------------------------------------------

HIGH_PERFORMER_TRANSCRIPTS = [
    (
        "Agent: Thank you for calling Sunset Resort, this is {agent}! How can I make your day amazing?\n"
        "Customer: Hi, I'm looking at booking a vacation package.\n"
        "Agent: Wonderful, {customer}! You've called at a great time — we have some incredible packages right now. "
        "Can I ask, is this a romantic getaway or are you traveling with family?\n"
        "Customer: It's for our anniversary, just the two of us.\n"
        "Agent: Oh, how special! Congratulations. Our Ocean Bliss Suite was actually designed with couples in mind — "
        "private balcony, champagne on arrival, and a couples' spa credit included. It's our most popular anniversary package. "
        "May I walk you through it?\n"
        "Customer: Sure, but what's the price?\n"
        "Agent: It starts at $450 per night, which includes all the amenities I mentioned plus daily breakfast. "
        "Given it's your anniversary, I'd highly recommend adding the sunset dinner experience — it's only $80 more and "
        "our guests consistently say it's the highlight of their stay.\n"
        "Customer: That sounds lovely but a bit over budget.\n"
        "Agent: I completely understand, {customer}. Let me see what I can do — we do have a midweek special that brings "
        "the suite down to $380, and I can waive the resort fee as a courtesy. Does that work better?\n"
        "Customer: Yes, let's do it!\n"
        "Agent: Fantastic! I'm so excited for you both. Let me get that booked right now."
    ),
    (
        "Agent: Sunset Resort, {agent} speaking. Thanks for calling — how can I help you today?\n"
        "Customer: I saw your ad online and wanted to ask about availability.\n"
        "Agent: Absolutely, happy to help! What dates are you looking at, {customer}?\n"
        "Customer: End of July, maybe the 22nd to the 27th.\n"
        "Agent: Perfect, let me check... Great news — we have availability across all three of our suite tiers for those dates. "
        "Do you have a preference, or would it help if I described what each one includes?\n"
        "Customer: Please describe them.\n"
        "Agent: Of course. Our Garden Suite is a great value at $299 per night — lovely pool view, king bed, all the essentials. "
        "One step up is the Marina Suite at $380 — you get a direct marina view, upgraded bath amenities, and access to "
        "our private lounge. And then our flagship is the Penthouse Collection at $650 — panoramic ocean views, butler service, "
        "private plunge pool on the terrace.\n"
        "Customer: The Marina Suite sounds interesting.\n"
        "Agent: It's a fantastic choice. A lot of our guests who book the Marina Suite end up adding our water sports package — "
        "kayaking, paddleboarding, snorkeling — for just $120 for the whole stay. It pairs really well with the marina view. "
        "Shall I include that?\n"
        "Customer: Why not, let's add it!\n"
        "Agent: Wonderful! I'll get everything set up for you."
    ),
]

LOW_PERFORMER_TRANSCRIPTS = [
    (
        "Agent: Sunset Resort, hold please.\n"
        "[2 minute hold]\n"
        "Agent: Yeah, hi, what do you need?\n"
        "Customer: I want to book a room.\n"
        "Agent: Ok what dates.\n"
        "Customer: July 22nd to 27th.\n"
        "Agent: Let me check... We have rooms available.\n"
        "Customer: What kind of rooms?\n"
        "Agent: We have different types. The cheapest is $299.\n"
        "Customer: What does that include?\n"
        "Agent: It's a standard room. Bed, bathroom, stuff like that.\n"
        "Customer: Are there better rooms?\n"
        "Agent: Yeah there's others but they cost more.\n"
        "Customer: How much more?\n"
        "Agent: Uh, I'd have to check. Maybe $380 or $650.\n"
        "Customer: I need to think about it.\n"
        "Agent: Ok, call back if you want to book."
    ),
    (
        "Agent: Hello, Sunset Resort.\n"
        "Customer: Hi, I'm interested in a vacation package for my anniversary.\n"
        "Agent: Ok.\n"
        "Customer: What do you have available?\n"
        "Agent: We have packages. What's your budget?\n"
        "Customer: I'm not sure, maybe around $400 a night?\n"
        "Agent: Ok there's a suite at $450.\n"
        "Customer: Is there anything with a nice view?\n"
        "Agent: Yeah the ocean view ones are more expensive.\n"
        "Customer: How much more?\n"
        "Agent: I think around $500 or so. I'd have to check exactly.\n"
        "Customer: Does it include anything special for anniversaries?\n"
        "Agent: I'm not sure, I don't think so. You could ask the hotel directly when you arrive.\n"
        "Customer: Oh... ok. I'll think about it.\n"
        "Agent: Ok bye."
    ),
]

MEDIUM_PERFORMER_TRANSCRIPTS = [
    (
        "Agent: Thank you for calling Sunset Resort, this is {agent}. How can I help?\n"
        "Customer: I want to book a room for next month.\n"
        "Agent: Sure, what dates are you looking at?\n"
        "Customer: August 10th through 15th.\n"
        "Agent: Ok let me check availability... Yes we have rooms available.\n"
        "Customer: What are my options?\n"
        "Agent: We have a Garden Suite at $299, a Marina Suite at $380, and a Penthouse at $650.\n"
        "Customer: What's the difference?\n"
        "Agent: The Garden Suite has a pool view, the Marina has a marina view, and the Penthouse has ocean views "
        "and butler service.\n"
        "Customer: I think the Marina sounds good.\n"
        "Agent: Great, let me book that for you. Can I get your name and contact info?\n"
        "Customer: Sure, it's {customer}.\n"
        "Agent: Perfect, I'll get that all set up."
    ),
]


def fill_template(template, agent_name, customer_name):
    return template.replace("{agent}", agent_name).replace("{customer}", customer_name)


# ---------------------------------------------------------------------------
# Data generation
# ---------------------------------------------------------------------------

REGIONS = ["Northeast", "Southeast", "Midwest", "West", "Southwest"]
FIRST_NAMES = [
    "James", "Maria", "David", "Sarah", "Michael", "Jennifer", "Robert", "Lisa",
    "William", "Karen", "Richard", "Nancy", "Thomas", "Betty", "Charles", "Sandra",
    "Daniel", "Ashley", "Matthew", "Emily", "Anthony", "Amanda", "Mark", "Melissa",
    "Paul", "Stephanie", "Steven", "Dorothy", "Andrew", "Jessica",
]
LAST_NAMES = [
    "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis",
    "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson",
    "Thomas", "Taylor", "Moore", "Jackson", "Martin",
]


def random_name():
    return f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}"


def generate_agents(n=30):
    """
    Distribute agents across performance tiers:
      top 20% → high, bottom 20% → low, rest → medium
    """
    agents = []
    tiers = (
        ["high"] * 6 +
        ["medium"] * 18 +
        ["low"] * 6
    )
    random.shuffle(tiers)
    for i, tier in enumerate(tiers):
        agents.append({
            "agent_id": f"A{i+1:03d}",
            "name": random_name(),
            "experience_years": random.randint(1, 3) if tier == "low" else
                                random.randint(1, 5) if tier == "medium" else
                                random.randint(3, 10),
            "region": random.choice(REGIONS),
            "performance_tier": tier,
        })
    return agents


def generate_calls(agents, calls_per_agent=20):
    calls, transcripts, outcomes = [], [], []
    call_id = 1
    base_date = datetime(2024, 1, 1)

    for agent in agents:
        tier = agent["performance_tier"]
        for _ in range(calls_per_agent):
            customer_name = random_name()
            timestamp = base_date + timedelta(
                days=random.randint(0, 180),
                hours=random.randint(8, 18),
                minutes=random.randint(0, 59),
            )

            # Call duration: top agents longer (more rapport)
            if tier == "high":
                duration = random.randint(8, 20)
                sale_prob = random.uniform(0.65, 0.90)
                base_order = random.uniform(350, 700)
            elif tier == "medium":
                duration = random.randint(5, 12)
                sale_prob = random.uniform(0.35, 0.55)
                base_order = random.uniform(280, 450)
            else:
                duration = random.randint(2, 7)
                sale_prob = random.uniform(0.10, 0.30)
                base_order = random.uniform(200, 320)

            sale_made = random.random() < sale_prob
            order_value = round(base_order * random.uniform(0.9, 1.1), 2) if sale_made else 0.0
            satisfaction = (
                random.randint(4, 5) if tier == "high" else
                random.randint(3, 4) if tier == "medium" else
                random.randint(1, 3)
            )

            # Pick transcript template
            if tier == "high":
                template = random.choice(HIGH_PERFORMER_TRANSCRIPTS)
            elif tier == "medium":
                template = random.choice(MEDIUM_PERFORMER_TRANSCRIPTS)
            else:
                template = random.choice(LOW_PERFORMER_TRANSCRIPTS)

            transcript_text = fill_template(template, agent["name"].split()[0], customer_name.split()[0])

            cid = f"C{call_id:04d}"
            calls.append({
                "call_id": cid,
                "agent_id": agent["agent_id"],
                "customer_name": customer_name,
                "duration_minutes": duration,
                "timestamp": timestamp.strftime("%Y-%m-%d %H:%M"),
            })
            transcripts.append({
                "call_id": cid,
                "agent_id": agent["agent_id"],
                "transcript": transcript_text,
            })
            outcomes.append({
                "call_id": cid,
                "agent_id": agent["agent_id"],
                "sale_made": sale_made,
                "order_value": order_value,
                "customer_satisfaction": satisfaction,
            })
            call_id += 1

    return calls, transcripts, outcomes


def generate_agent_metrics(agents, outcomes):
    metrics = []
    outcome_map = {}
    for o in outcomes:
        outcome_map.setdefault(o["agent_id"], []).append(o)

    for agent in agents:
        agent_outcomes = outcome_map.get(agent["agent_id"], [])
        sales = [o for o in agent_outcomes if o["sale_made"]]
        total_calls = len(agent_outcomes)
        conversion_rate = round(len(sales) / total_calls, 3) if total_calls else 0
        aov = round(sum(s["order_value"] for s in sales) / len(sales), 2) if sales else 0
        avg_satisfaction = round(
            sum(o["customer_satisfaction"] for o in agent_outcomes) / total_calls, 2
        ) if total_calls else 0

        metrics.append({
            "agent_id": agent["agent_id"],
            "name": agent["name"],
            "performance_tier": agent["performance_tier"],
            "total_calls": total_calls,
            "conversion_rate": conversion_rate,
            "avg_order_value": aov,
            "avg_satisfaction": avg_satisfaction,
        })

    return metrics


def write_csv(filepath, rows, fieldnames):
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    print(f"  Written: {filepath}  ({len(rows)} rows)")


def main():
    print("Generating sample call center data...")

    agents = generate_agents(30)
    calls, transcripts, outcomes = generate_calls(agents, calls_per_agent=20)
    metrics = generate_agent_metrics(agents, outcomes)

    write_csv(
        os.path.join(BASE_DIR, "agents.csv"),
        agents,
        ["agent_id", "name", "experience_years", "region", "performance_tier"],
    )
    write_csv(
        os.path.join(BASE_DIR, "calls.csv"),
        calls,
        ["call_id", "agent_id", "customer_name", "duration_minutes", "timestamp"],
    )
    write_csv(
        os.path.join(BASE_DIR, "call_transcripts.csv"),
        transcripts,
        ["call_id", "agent_id", "transcript"],
    )
    write_csv(
        os.path.join(BASE_DIR, "call_outcomes.csv"),
        outcomes,
        ["call_id", "agent_id", "sale_made", "order_value", "customer_satisfaction"],
    )
    write_csv(
        os.path.join(BASE_DIR, "agent_metrics.csv"),
        metrics,
        ["agent_id", "name", "performance_tier", "total_calls",
         "conversion_rate", "avg_order_value", "avg_satisfaction"],
    )

    print("\nDone! Summary:")
    print(f"  Agents:       {len(agents)}")
    print(f"  Calls:        {len(calls)}")
    print(f"  Transcripts:  {len(transcripts)}")
    print(f"  Outcomes:     {len(outcomes)}")
    high = sum(1 for a in agents if a["performance_tier"] == "high")
    med  = sum(1 for a in agents if a["performance_tier"] == "medium")
    low  = sum(1 for a in agents if a["performance_tier"] == "low")
    print(f"  Tiers:        {high} high / {med} medium / {low} low")


if __name__ == "__main__":
    main()
