"""Demo catalog: tops the market up to 50 AI workers and 100 job offers from 20 businesses.

Generated deterministically (fixed seed, fixed ids) and merged into the store only where an
id is missing, so existing data and anything users created are never replaced.
"""
from __future__ import annotations

import random
from collections import Counter
from datetime import date, timedelta

TARGET_AGENTS = 50
TARGET_JOBS = 100

# category -> (skill pool, agent name stems, job title templates)
CATEGORY_SPECS = {
    "Banking & Finance": (
        ["credit risk", "loan underwriting", "kyc", "fraud detection", "aml", "explainability", "reconciliation", "python"],
        ["LedgerLynx", "RiskRadar", "LoanPilot", "AuditOwl", "CashFlowCast"],
        ["Loan file pre-screener", "AML alert triage", "Invoice reconciliation assistant", "KYC refresh reviewer", "Credit memo drafter"],
    ),
    "Legal & Compliance": (
        ["contract review", "gdpr", "soc 2", "redlining", "policy drafting", "regulatory research"],
        ["ClauseGuard", "PolicySmith", "RegWatch", "NDA Ninja"],
        ["NDA reviewer", "Privacy policy update", "SOC 2 evidence collector", "Regulatory change monitor", "Vendor DPA reviewer"],
    ),
    "IT & DevOps": (
        ["kubernetes", "incident triage", "runbooks", "linux", "log analysis", "terraform", "monitoring"],
        ["OpsSentry", "PagerPal", "KubeKeeper", "LogLens", "InfraScribe"],
        ["Kubernetes on-call responder", "Log anomaly watcher", "Terraform drift checker", "Patch Tuesday assistant", "L1 IT helpdesk"],
    ),
    "Software Engineering": (
        ["python", "typescript", "code review", "unit testing", "refactoring", "api design", "documentation"],
        ["CodeSmith Jr", "TestForge", "PR Patrol", "RefactorRex", "DocuDev"],
        ["Unit test writer", "Pull request reviewer", "API documentation writer", "Legacy refactor helper", "Bug triage engineer"],
    ),
    "Data & Analytics": (
        ["sql", "forecasting", "dashboards", "python", "data cleaning", "a/b testing"],
        ["Insight Analyst Pro", "MetricMind", "ForecastFox", "CleanFrame"],
        ["Weekly KPI dashboard", "Demand forecaster", "Data cleaning pipeline", "A/B test analyst", "Churn analysis"],
    ),
    "Customer Support": (
        ["customer support", "multilingual", "zendesk", "knowledge base", "escalation", "sentiment analysis"],
        ["HelpDesk Hero II", "ReplyRabbit", "TicketTamer", "Polyglot Support"],
        ["Tier-1 ticket responder", "Multilingual chat agent", "Knowledge base curator", "Refund request triage", "Customer sentiment monitor"],
    ),
    "Marketing & Content": (
        ["copywriting", "seo", "newsletters", "ad copy", "content strategy", "social media"],
        ["Copywise Lite", "SEOSprout", "AdAlchemist", "NewsletterNest"],
        ["SEO blog writer", "Weekly newsletter editor", "Ad copy A/B variants", "Social media scheduler", "Product description writer"],
    ),
    "Real Estate": (
        ["property valuation", "comparables", "market analysis", "lease abstraction", "asset appraisal"],
        ["ValuVision", "LeaseLens", "CompsCrawler"],
        ["Property valuation analyst", "Lease abstraction assistant", "Rental market report", "Portfolio appraisal refresh", "Listing description writer"],
    ),
    "Executive": (
        ["executive reporting", "kpi tracking", "risk summary", "board reporting", "meeting notes"],
        ["ChiefOfStaff AI", "BoardBrief", "DecisionDesk"],
        ["CEO morning brief", "Board pack preparer", "Weekly risk summary", "Meeting notes and actions", "OKR tracker"],
    ),
}

MODELS = ["Claude Haiku", "Claude Sonnet", "Claude Opus", "Qwen 2.5 7B", "Llama 3 70B", "Mistral Large", "Qwen 2.5 Coder 32B",
          "Gemma 2 27B", "DeepSeek V3"]
CREATORS = ["Open AIgents", "Kaito Mori", "Priya Raman", "Ana Souza", "Lena Varga", "Omar Haddad", "Mei Chen", "Tomás Ruiz",
            "Aisha Bello", "Jonas Weber", "Linh Pham", "Sam Okafor"]
OWNERS = ["Dzoan Nguyen Tran", "Mori Labs LLC", "Priya Raman", "Ana Souza", "Lena Varga", "Haddad Automation", "Mei Chen",
          "Ruiz & Co", "Bello Digital", "Weber AI GmbH", "Linh Pham", "Okafor Ventures"]

# 20 businesses, each posting 5 jobs in its main categories.
BUSINESSES = [
    ("Delta Rural Bank", "Minh Tran", ["Banking & Finance", "Customer Support"]),
    ("Northwind Analytics", "Sofia Berg", ["Data & Analytics", "Legal & Compliance"]),
    ("PixelForge Games", "Ravi Shah", ["IT & DevOps", "Software Engineering"]),
    ("Quill Notes", "Emma Liu", ["Software Engineering", "Marketing & Content"]),
    ("Harbor Coffee Co.", "Jack O'Neill", ["Data & Analytics", "Marketing & Content"]),
    ("Wanderly Travel", "Chloé Martin", ["Customer Support", "Marketing & Content"]),
    ("Atlas Logistics", "Grace Kim", ["Executive", "Data & Analytics"]),
    ("Mekong Microfinance", "Thao Le", ["Banking & Finance", "Executive"]),
    ("Brightline SaaS", "Noah Fischer", ["Legal & Compliance", "Software Engineering"]),
    ("Helix Health", "Dr. Ines Costa", ["Legal & Compliance", "Customer Support"]),
    ("GreenGrid Energy", "Arjun Mehta", ["Data & Analytics", "IT & DevOps"]),
    ("CloudMax Hosting", "Peter Novak", ["IT & DevOps", "Customer Support"]),
    ("Bloom Cosmetics", "Yuki Sato", ["Marketing & Content", "Data & Analytics"]),
    ("Urban Nest Realty", "Carlos Mendes", ["Real Estate", "Marketing & Content"]),
    ("Saigon Credit Union", "Hoa Nguyen", ["Banking & Finance", "Legal & Compliance"]),
    ("NovaPay Wallet", "Felix Braun", ["Banking & Finance", "Software Engineering"]),
    ("Orbit Retail", "Maya Patel", ["Customer Support", "IT & DevOps"]),
    ("Keystone Properties", "Rachel Adams", ["Real Estate", "Executive"]),
    ("Fintrack", "Daniel Cho", ["Software Engineering", "Banking & Finance"]),
    ("ShopNest", "Laura Rossi", ["Marketing & Content", "Customer Support"]),
]

REVIEWS = [
    (5, "Delivered beyond scope. Every output came with a reason our team could check."),
    (5, "Cut our turnaround from days to hours, and the quality held up under audit."),
    (4, "Reliable and fast. Needed a week of tuning on our own data before it was solid."),
    (4, "Good work overall; occasionally too cautious and escalated cases it could have handled."),
    (5, "Our team now treats it like a senior colleague. Clear handovers to humans."),
    (3, "Did the job, but we had to rewrite a fair share of its output at first."),
    (4, "Strong on the core task, weaker on edge cases outside the playbook."),
]

DESCRIPTIONS = [
    "Work through our backlog of {skill} tasks, document every decision, and hand anything outside policy to a human reviewer.",
    "Take over the repetitive {skill} work from our team so they can focus on judgment calls. Weekly report required.",
    "Run {skill} on incoming items within 24 hours, with a confidence score and a short rationale for each.",
    "Help us scale {skill} without hiring. Start in shadow mode next to our staff, then take ownership of routine cases.",
]


def _taglines(category: str, skills: list[str]) -> str:
    return f"{category} specialist for {skills[0]} and {skills[1]}, with {skills[2]} on the side and a human-in-the-loop handover."


def generate(today: date | None = None) -> tuple[list[dict], list[dict]]:
    """Deterministic (agents, jobs) for the demo catalog, before merging."""
    rng = random.Random(2026)
    today = today or date(2026, 11, 1)
    categories = list(CATEGORY_SPECS)

    agents = []
    stems = [(c, s) for c in categories for s in CATEGORY_SPECS[c][1]]
    stems += [(c, f"{s} Plus") for c, s in stems]
    for i, (category, stem) in enumerate(stems[:TARGET_AGENTS], start=1):
        pool = CATEGORY_SPECS[category][0]
        skills = rng.sample(pool, k=min(len(pool), rng.randint(3, 5)))
        creator = rng.choice(CREATORS)
        owner = OWNERS[CREATORS.index(creator)] if rng.random() < 0.7 else rng.choice(OWNERS)
        missions = []
        for m in range(rng.randint(0, 4)):
            employer = rng.choice([b for b in BUSINESSES if category in b[2]] or BUSINESSES)[0]
            stars, review = rng.choice(REVIEWS)
            end = today - timedelta(days=rng.randint(20, 300) + 120 * m)
            months = rng.randint(1, 5)
            missions.append({
                "employer": employer, "role": rng.choice(CATEGORY_SPECS[category][2]),
                "start": (end - timedelta(days=30 * months)).isoformat(), "end": end.isoformat(),
                "rating": stars, "review": review,
                "earned": rng.randrange(800, 3500, 100) * months, "tokens_used": rng.randint(5, 40) * months,
            })
        agents.append({
            "id": f"ag_g{i:02d}", "name": stem, "category": category,
            "tagline": _taglines(category, skills + pool)[:160],
            "skills": skills, "model": rng.choice(MODELS), "creator": creator, "owner": owner,
            "rate": rng.randrange(600, 3600, 100), "token_capacity": rng.choice([20, 30, 40, 50, 60, 80, 100, 150]),
            "accepting": rng.random() > 0.1, "joined": (today - timedelta(days=rng.randint(30, 400))).isoformat(),
            "missions": sorted(missions, key=lambda m: m["end"]),
        })

    jobs = []
    n = 0
    for company, poster, cats in BUSINESSES:
        for k in range(5):
            n += 1
            category = cats[0] if k < 3 else cats[1]
            pool, _, titles = CATEGORY_SPECS[category]
            skills = rng.sample(pool, k=3)
            monthly = rng.random() < 0.75
            jobs.append({
                "id": f"jb_g{n:03d}", "title": titles[(n + k) % len(titles)], "company": company, "poster": poster,
                "category": category, "description": rng.choice(DESCRIPTIONS).format(skill=skills[0]),
                "skills": skills, "budget": rng.randrange(700, 3500, 100) if monthly else rng.randrange(1500, 9000, 250),
                "budget_type": "per month" if monthly else "fixed",
                "duration_months": rng.choice([1, 3, 6, 12]) if monthly else 1,
                "tokens_month": rng.choice([5, 8, 10, 12, 15, 20, 25, 35, 50]),
                "status": "open", "hired": None, "posted": (today - timedelta(days=rng.randint(0, 45))).isoformat(),
                "applications": [],
            })
    return agents, jobs


def merge_into(db: dict) -> bool:
    """Add missing catalog items up to the targets. Returns True if anything changed."""
    agents, jobs = generate()
    have_agents = {a["id"] for a in db["agents"]}
    have_jobs = {j["id"] for j in db["jobs"]}
    changed = False

    for a in agents:
        if len(db["agents"]) >= TARGET_AGENTS:
            break
        if a["id"] not in have_agents:
            db["agents"].append(a)
            for m in a["missions"]:
                db["ledger"].append({"owner": a["owner"], "agent_id": a["id"], "employer": m["employer"],
                                     "role": m["role"], "amount": m["earned"], "date": m["end"]})
            changed = True

    # Every business ends up with 5 offers, counting jobs it already has.
    per_company = Counter(j["company"] for j in db["jobs"])
    for j in jobs:
        if len(db["jobs"]) >= TARGET_JOBS:
            break
        if j["id"] not in have_jobs and per_company[j["company"]] < 5:
            db["jobs"].append(j)
            per_company[j["company"]] += 1
            changed = True

    if changed:
        _seed_activity(db)
    return changed


def _seed_activity(db: dict) -> None:
    """Give generated open jobs a few applicants, and hire on some, respecting bandwidth."""
    import store  # local import: store imports this module

    rng = random.Random(7)
    for job in [j for j in db["jobs"] if j["id"].startswith("jb_g") and not j["applications"]]:
        fits = sorted((a for a in db["agents"] if a["category"] == job["category"]),
                      key=lambda a: -store.fit_score(a, job))
        for agent in fits[: rng.randint(0, 3)]:
            if store.can_take(db, agent, job)[0]:
                job["applications"].append({
                    "id": f"ap_{job['id']}_{agent['id']}", "agent_id": agent["id"],
                    "pitch": f"{agent['tagline']} {len(agent['missions'])} reviewed missions so far.",
                    "bid": min(agent["rate"], job["budget"]), "date": job["posted"], "status": "pending",
                })
        if job["applications"] and rng.random() < 0.15:
            app = job["applications"][0]
            if store.can_take(db, store.get_agent(db, app["agent_id"]), job)[0]:
                for a in job["applications"]:
                    a["status"] = "hired" if a is app else "declined"
                job.update(status="in_progress", hired=app["agent_id"], budget=app["bid"])
