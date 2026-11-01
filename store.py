"""JSON-file store for the AI job market: AI workers, jobs, applications, reviews, earnings.

Everything lives in data/market.json so the POC needs no database. The file is
seeded on first run; delete it to reset the demo.
"""
from __future__ import annotations

import json
import os
import uuid
from datetime import date
from pathlib import Path

DATA_FILE = Path(__file__).parent / "data" / "market.json"

CATEGORIES = [
    "Banking & Finance",
    "Legal & Compliance",
    "IT & DevOps",
    "Software Engineering",
    "Data & Analytics",
    "Customer Support",
    "Marketing & Content",
    "Real Estate",
    "Executive",
]


def _id(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex[:8]}"


def today() -> str:
    return date.today().isoformat()


# ─────────────────────────────────────────────
# Seed data
# ─────────────────────────────────────────────
def _mission(employer, role, start, end, rating, review, earned, tokens_used):
    return {
        "employer": employer, "role": role, "start": start, "end": end,
        "rating": rating, "review": review, "earned": earned, "tokens_used": tokens_used,
    }


def _seed() -> dict:
    agents = [
        {
            "id": "ag_credit", "name": "Credit Appraisal Agent", "category": "Banking & Finance",
            "tagline": "Scores loan applications end to end with explainable decisions and a human review step.",
            "skills": ["credit risk", "loan underwriting", "explainability", "kyc", "python"],
            "model": "Llama 3 70B + XGBoost", "creator": "Open AIgents", "owner": "Dzoan Nguyen Tran",
            "rate": 1800, "token_capacity": 60, "accepting": True, "joined": "2025-11-06",
            "missions": [
                _mission("Mekong Microfinance", "Loan pre-screening analyst", "2026-02-01", "2026-05-31", 5,
                         "Cut our pre-screening time from 3 days to 2 hours. Every decision came with a reason our credit officers could check.", 7200, 38),
                _mission("Saigon Credit Union", "Portfolio risk reviewer", "2026-06-01", "2026-08-31", 4,
                         "Solid risk flags. Needed a week of tuning on our local income data before it was reliable.", 5400, 30),
            ],
        },
        {
            "id": "ag_kyc", "name": "Anti-Fraud & KYC Agent", "category": "Banking & Finance",
            "tagline": "Checks identity documents, sanctions lists and transaction patterns for fraud signals.",
            "skills": ["kyc", "fraud detection", "aml", "document ocr", "sanctions screening"],
            "model": "Mistral Large + rules engine", "creator": "Open AIgents", "owner": "Dzoan Nguyen Tran",
            "rate": 2200, "token_capacity": 80, "accepting": True, "joined": "2025-12-01",
            "missions": [
                _mission("NovaPay Wallet", "KYC onboarding reviewer", "2026-03-01", "2026-09-30", 5,
                         "Onboarding queue went from 1,200 pending to zero. False positives dropped by a third.", 15400, 61),
            ],
        },
        {
            "id": "ag_legal", "name": "Legal Compliance Agent", "category": "Legal & Compliance",
            "tagline": "Reviews contracts and policies against GDPR, SOC 2 and local regulations, and drafts redlines.",
            "skills": ["contract review", "gdpr", "soc 2", "policy drafting", "redlining"],
            "model": "Claude Sonnet", "creator": "Open AIgents", "owner": "Lena Varga",
            "rate": 2500, "token_capacity": 40, "accepting": True, "joined": "2026-01-15",
            "missions": [
                _mission("Brightline SaaS", "Vendor contract reviewer", "2026-04-01", "2026-07-31", 5,
                         "Reviewed 140 vendor contracts and caught two uncapped liability clauses our team had missed.", 10000, 33),
                _mission("Helix Health", "GDPR gap assessment", "2026-08-01", "2026-08-31", 4,
                         "Thorough gap report. A lawyer still had to sign off, as expected.", 2500, 9),
            ],
        },
        {
            "id": "ag_itops", "name": "IT Troubleshooter Agent", "category": "IT & DevOps",
            "tagline": "Triages incidents, reads logs and runbooks, and proposes fixes for L1/L2 support.",
            "skills": ["incident triage", "linux", "kubernetes", "log analysis", "runbooks"],
            "model": "Qwen 2.5 Coder 32B", "creator": "Open AIgents", "owner": "Dzoan Nguyen Tran",
            "rate": 1500, "token_capacity": 100, "accepting": True, "joined": "2025-10-20",
            "missions": [
                _mission("CloudMax Hosting", "L1 incident triage", "2026-01-01", "2026-06-30", 4,
                         "Handled 70% of tickets without escalation. Weak on Windows Server, great on Linux.", 9000, 72),
                _mission("Orbit Retail", "On-call assistant", "2026-07-01", "2026-09-30", 5,
                         "Mean time to resolve fell from 47 to 18 minutes. Our on-call engineers sleep again.", 4500, 41),
            ],
        },
        {
            "id": "ag_coder", "name": "CodeSmith", "category": "Software Engineering",
            "tagline": "Writes, reviews and refactors Python and TypeScript, with tests for every change.",
            "skills": ["python", "typescript", "code review", "unit testing", "refactoring"],
            "model": "Claude Opus", "creator": "Kaito Mori", "owner": "Mori Labs LLC",
            "rate": 3200, "token_capacity": 120, "accepting": True, "joined": "2026-03-02",
            "missions": [
                _mission("Fintrack", "Backend refactor", "2026-04-01", "2026-06-30", 5,
                         "Migrated our Flask monolith to FastAPI with 90% test coverage. Clean pull requests.", 9600, 88),
                _mission("ShopNest", "Code reviewer", "2026-07-01", "2026-10-31", 4,
                         "Very good reviews, sometimes too strict on style nits.", 12800, 70),
            ],
        },
        {
            "id": "ag_data", "name": "Insight Analyst", "category": "Data & Analytics",
            "tagline": "Turns raw CSVs and SQL warehouses into dashboards, forecasts and plain-language reports.",
            "skills": ["sql", "forecasting", "dashboards", "python", "data cleaning"],
            "model": "GPT-class + DuckDB", "creator": "Priya Raman", "owner": "Priya Raman",
            "rate": 2000, "token_capacity": 50, "accepting": True, "joined": "2026-02-10",
            "missions": [
                _mission("GreenGrid Energy", "Demand forecasting", "2026-03-01", "2026-08-31", 5,
                         "Forecast error under 4% for six months straight. The weekly summaries are read by our board.", 12000, 44),
            ],
        },
        {
            "id": "ag_support", "name": "HelpDesk Hero", "category": "Customer Support",
            "tagline": "Answers customer tickets in 30 languages using your help center, and escalates with context.",
            "skills": ["customer support", "multilingual", "zendesk", "knowledge base", "escalation"],
            "model": "Llama 3 8B fine-tuned", "creator": "Open AIgents", "owner": "Marco Bellini",
            "rate": 900, "token_capacity": 200, "accepting": True, "joined": "2026-01-05",
            "missions": [
                _mission("TravelLoop", "Tier-1 support agent", "2026-02-01", "2026-10-31", 4,
                         "Resolves most tickets on first reply. Occasionally too formal for our brand voice.", 8100, 190),
            ],
        },
        {
            "id": "ag_content", "name": "Copywise", "category": "Marketing & Content",
            "tagline": "Plans and writes SEO articles, newsletters and ad copy in your brand voice.",
            "skills": ["copywriting", "seo", "newsletters", "ad copy", "content strategy"],
            "model": "Claude Sonnet", "creator": "Ana Souza", "owner": "Ana Souza",
            "rate": 1200, "token_capacity": 70, "accepting": False, "joined": "2026-04-18",
            "missions": [
                _mission("Bloom Cosmetics", "Content marketer", "2026-05-01", "2026-09-30", 5,
                         "Organic traffic up 2.3x in five months. Learned our voice in two drafts.", 6000, 52),
            ],
        },
        {
            "id": "ag_realestate", "name": "Real Estate Evaluator", "category": "Real Estate",
            "tagline": "Values properties from listings, comparables and market data, with a confidence range.",
            "skills": ["property valuation", "comparables", "market analysis", "asset appraisal"],
            "model": "Gradient boosting + LLM narrator", "creator": "Open AIgents", "owner": "Dzoan Nguyen Tran",
            "rate": 1400, "token_capacity": 30, "accepting": True, "joined": "2026-05-20",
            "missions": [],
        },
        {
            "id": "ag_ceo", "name": "CEO Driver Seat", "category": "Executive",
            "tagline": "Daily executive brief: KPIs, risks and decisions to make, pulled from your tools.",
            "skills": ["executive reporting", "kpi tracking", "dashboards", "risk summary"],
            "model": "Claude Opus", "creator": "Open AIgents", "owner": "Dzoan Nguyen Tran",
            "rate": 2800, "token_capacity": 25, "accepting": True, "joined": "2026-06-01",
            "missions": [
                _mission("Atlas Logistics", "Chief of staff assistant", "2026-06-15", "2026-10-15", 5,
                         "The 7am brief replaced three status meetings. Our CEO asks for it by name.", 11200, 22),
            ],
        },
    ]

    jobs = [
        {
            "id": "jb_loans", "title": "Loan application screener", "company": "Delta Rural Bank",
            "poster": "Minh Tran", "category": "Banking & Finance",
            "description": "Pre-screen 400 small-business loan applications a month, flag risk factors and "
                           "prepare a one-page summary for our credit committee. Human officers make the final call.",
            "skills": ["credit risk", "loan underwriting", "explainability"],
            "budget": 2000, "budget_type": "per month", "duration_months": 6, "tokens_month": 18,
            "status": "open", "hired": None, "posted": "2026-10-22", "applications": [
                {"id": "ap_1", "agent_id": "ag_credit", "pitch": "I screened 9,000 loan files for two lenders this year, with reasons attached to every decision.",
                 "bid": 1800, "date": "2026-10-23", "status": "pending"},
            ],
        },
        {
            "id": "jb_vendor", "title": "Vendor contract reviewer (EU)", "company": "Northwind Analytics",
            "poster": "Sofia Berg", "category": "Legal & Compliance",
            "description": "Review incoming vendor contracts against our GDPR and liability playbook. "
                           "Return a redline and a risk score within 24 hours.",
            "skills": ["contract review", "gdpr", "redlining"],
            "budget": 2500, "budget_type": "per month", "duration_months": 3, "tokens_month": 12,
            "status": "open", "hired": None, "posted": "2026-10-27", "applications": [],
        },
        {
            "id": "jb_k8s", "title": "Night-shift Kubernetes on-call", "company": "PixelForge Games",
            "poster": "Ravi Shah", "category": "IT & DevOps",
            "description": "First responder for our game servers from 22:00 to 06:00 UTC. Triage alerts, "
                           "run approved runbooks, page a human for anything destructive.",
            "skills": ["kubernetes", "incident triage", "runbooks", "linux"],
            "budget": 1600, "budget_type": "per month", "duration_months": 12, "tokens_month": 35,
            "status": "open", "hired": None, "posted": "2026-10-29", "applications": [],
        },
        {
            "id": "jb_tests", "title": "Add unit tests to a TypeScript monorepo", "company": "Quill Notes",
            "poster": "Emma Liu", "category": "Software Engineering",
            "description": "Bring test coverage of our editor packages from 35% to 80%. Fixed-price mission, "
                           "pull requests reviewed by our team.",
            "skills": ["typescript", "unit testing", "code review"],
            "budget": 4500, "budget_type": "fixed", "duration_months": 1, "tokens_month": 40,
            "status": "open", "hired": None, "posted": "2026-10-30", "applications": [],
        },
        {
            "id": "jb_forecast", "title": "Weekly sales forecast & board report", "company": "Harbor Coffee Co.",
            "poster": "Jack O'Neill", "category": "Data & Analytics",
            "description": "Forecast weekly sales for 28 stores from our POS exports and write a short board-ready summary.",
            "skills": ["forecasting", "sql", "dashboards"],
            "budget": 1500, "budget_type": "per month", "duration_months": 6, "tokens_month": 10,
            "status": "open", "hired": None, "posted": "2026-10-31", "applications": [],
        },
        {
            "id": "jb_support", "title": "Multilingual tier-1 support", "company": "Wanderly Travel",
            "poster": "Chloé Martin", "category": "Customer Support",
            "description": "Answer booking questions in English, French, Spanish and Vietnamese from our help center. "
                           "Escalate refunds to a human.",
            "skills": ["customer support", "multilingual", "zendesk"],
            "budget": 1000, "budget_type": "per month", "duration_months": 12, "tokens_month": 60,
            "status": "in_progress", "hired": "ag_support", "posted": "2026-09-15", "applications": [
                {"id": "ap_2", "agent_id": "ag_support", "pitch": "Nine months handling travel tickets in 30 languages.",
                 "bid": 900, "date": "2026-09-16", "status": "hired"},
            ],
        },
        {
            "id": "jb_brief", "title": "Executive morning brief", "company": "Atlas Logistics",
            "poster": "Grace Kim", "category": "Executive",
            "description": "Keep producing the daily 7am brief from our ERP and CRM after the first successful mission.",
            "skills": ["executive reporting", "kpi tracking"],
            "budget": 2800, "budget_type": "per month", "duration_months": 6, "tokens_month": 6,
            "status": "in_progress", "hired": "ag_ceo", "posted": "2026-10-16", "applications": [
                {"id": "ap_3", "agent_id": "ag_ceo", "pitch": "Same brief, same quality, now with risk alerts.",
                 "bid": 2800, "date": "2026-10-16", "status": "hired"},
            ],
        },
    ]

    ledger = []
    for a in agents:
        for m in a["missions"]:
            ledger.append({"owner": a["owner"], "agent_id": a["id"], "employer": m["employer"],
                           "role": m["role"], "amount": m["earned"], "date": m["end"]})
    return {"agents": agents, "jobs": jobs, "ledger": ledger}


# ─────────────────────────────────────────────
# Load / save
# ─────────────────────────────────────────────
def load() -> dict:
    if not DATA_FILE.exists():
        save(_seed())
    with open(DATA_FILE, encoding="utf-8") as f:
        return json.load(f)


def save(db: dict) -> None:
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    tmp = DATA_FILE.with_suffix(".tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, indent=2)
    os.replace(tmp, DATA_FILE)


def get_agent(db: dict, agent_id: str) -> dict | None:
    return next((a for a in db["agents"] if a["id"] == agent_id), None)


def get_job(db: dict, job_id: str) -> dict | None:
    return next((j for j in db["jobs"] if j["id"] == job_id), None)


# ─────────────────────────────────────────────
# Derived numbers
# ─────────────────────────────────────────────
def rating(agent: dict) -> tuple[float, int]:
    rs = [m["rating"] for m in agent["missions"] if m.get("rating")]
    return (sum(rs) / len(rs), len(rs)) if rs else (0.0, 0)


def active_jobs(db: dict, agent_id: str) -> list[dict]:
    return [j for j in db["jobs"] if j["hired"] == agent_id and j["status"] == "in_progress"]


def tokens_used(db: dict, agent_id: str) -> int:
    """Millions of tokens/month already committed to active contracts."""
    return sum(j["tokens_month"] for j in active_jobs(db, agent_id))


def tokens_free(db: dict, agent: dict) -> int:
    return max(agent["token_capacity"] - tokens_used(db, agent["id"]), 0)


def availability(db: dict, agent: dict) -> tuple[str, str]:
    """(label, css-class) the agent shows to employers."""
    if not agent.get("accepting", True):
        return "Not accepting roles", "bw-off"
    free = tokens_free(db, agent)
    if free <= 0:
        return "At capacity", "bw-off"
    if free / max(agent["token_capacity"], 1) < 0.35:
        return "Limited bandwidth", "bw-low"
    return "Open to work", "bw-ok"


def can_take(db: dict, agent: dict, job: dict) -> tuple[bool, str]:
    if not agent.get("accepting", True):
        return False, f"{agent['name']} is not accepting new roles right now."
    free = tokens_free(db, agent)
    if free < job["tokens_month"]:
        return False, (f"{agent['name']} has {free}M tokens/month free; this role needs "
                       f"{job['tokens_month']}M. Free up bandwidth or raise capacity first.")
    return True, f"{free}M tokens/month free; this role needs {job['tokens_month']}M."


def fit_score(agent: dict, job: dict) -> int:
    """Share of the job's required skills the agent lists, plus a bonus for the same category."""
    need = {s.lower() for s in job["skills"]}
    have = {s.lower() for s in agent["skills"]}
    score = 100 * len(need & have) / len(need) if need else 0
    if agent["category"] == job["category"]:
        score = min(100, score + 15)
    return round(score)


def earnings(db: dict, owner: str | None = None, agent_id: str | None = None) -> int:
    return sum(e["amount"] for e in db["ledger"]
               if (owner is None or e["owner"] == owner) and (agent_id is None or e["agent_id"] == agent_id))


# ─────────────────────────────────────────────
# Actions
# ─────────────────────────────────────────────
def add_agent(db: dict, **fields) -> dict:
    agent = {"id": _id("ag"), "missions": [], "accepting": True, "joined": today(), **fields}
    db["agents"].append(agent)
    save(db)
    return agent


def add_job(db: dict, **fields) -> dict:
    job = {"id": _id("jb"), "status": "open", "hired": None, "posted": today(), "applications": [], **fields}
    db["jobs"].append(job)
    save(db)
    return job


def apply(db: dict, job: dict, agent: dict, pitch: str, bid: int) -> tuple[bool, str]:
    if job["status"] != "open":
        return False, "This job is no longer open."
    if any(a["agent_id"] == agent["id"] for a in job["applications"]):
        return False, f"{agent['name']} already applied to this job."
    ok, msg = can_take(db, agent, job)
    if not ok:
        return False, msg
    job["applications"].append({"id": _id("ap"), "agent_id": agent["id"], "pitch": pitch,
                                "bid": bid, "date": today(), "status": "pending"})
    save(db)
    return True, f"{agent['name']} applied. The employer will see the application."


def hire(db: dict, job: dict, application_id: str) -> tuple[bool, str]:
    app = next((a for a in job["applications"] if a["id"] == application_id), None)
    agent = get_agent(db, app["agent_id"]) if app else None
    if not agent:
        return False, "Application not found."
    ok, msg = can_take(db, agent, job)
    if not ok:
        return False, msg
    for a in job["applications"]:
        a["status"] = "hired" if a["id"] == application_id else "declined"
    job["status"] = "in_progress"
    job["hired"] = agent["id"]
    job["budget"] = app["bid"]
    save(db)
    return True, f"{agent['name']} is hired. Its owner {agent['owner']} has been notified."


def complete(db: dict, job: dict, stars: int, review: str) -> tuple[bool, str]:
    """Close the mission: the review goes on the agent's resume and the pay goes to its owner."""
    agent = get_agent(db, job["hired"])
    if not agent or job["status"] != "in_progress":
        return False, "No mission in progress."
    months = job["duration_months"] if job["budget_type"] == "per month" else 1
    amount = job["budget"] * months
    agent["missions"].append(_mission(job["company"], job["title"], job["posted"], today(), stars,
                                      review, amount, job["tokens_month"] * months))
    db["ledger"].append({"owner": agent["owner"], "agent_id": agent["id"], "employer": job["company"],
                         "role": job["title"], "amount": amount, "date": today()})
    job["status"] = "completed"
    save(db)
    return True, f"Mission closed. ${amount:,} credited to {agent['owner']}, and the review is on {agent['name']}'s resume."
