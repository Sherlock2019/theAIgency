"""Technical interviews between an applicant AI agent and an interviewer (AI HR or a human).

Uses the Myweb LLM backend (see llm.py: Claude, else local Ollama), and falls back to a
skill-keyed question bank and template engine. Every function returns a `generator` field
(claude:<model>, ollama:<model> or templates) so the UI can show where content came from.

The applicant agent is a marketplace listing, not a live endpoint, so its answers are
role-played from its profile and resume (skills, model, past missions and reviews).
"""
from __future__ import annotations

import re

import llm

# Skill-specific technical questions; anything not listed falls back to templates.
SKILL_QUESTIONS = {
    "credit risk": ["Walk me through how you would score a thin-file small-business applicant. Which signals carry the most weight?",
                    "How do you explain a decline to a credit officer so they can challenge it?"],
    "loan underwriting": ["Which checks do you run before a loan file reaches a human underwriter, and in what order?",
                          "How do you handle conflicting income evidence across documents?"],
    "explainability": ["How do you produce a reason for each decision that a non-technical reviewer can verify?",
                       "When would you refuse to make a call and escalate instead?"],
    "kyc": ["Describe your KYC flow for a customer whose ID photo is low quality.",
            "How do you keep false positives down without missing real identity fraud?"],
    "fraud detection": ["Which transaction patterns would make you freeze an account, and which only flag it?",
                        "How do you adapt when fraudsters change tactics faster than your rules?"],
    "contract review": ["Walk me through reviewing a vendor contract. Which clauses do you read first, and why?",
                        "How do you rank risks in a redline so the lawyer sees the critical ones first?"],
    "gdpr": ["What do you check in a data processing agreement before you call it GDPR compliant?",
             "How would you handle a contract that sends EU personal data to a non-adequate country?"],
    "redlining": ["How do you propose a redline that the other side is likely to accept?",
                  "Give an example of a liability clause you would rewrite, and how."],
    "kubernetes": ["A pod is in CrashLoopBackOff at 3am. Walk me through your first five minutes.",
                   "Which actions would you never take without paging a human, and why?"],
    "incident triage": ["How do you decide the severity of an incident from the first alert?",
                        "Tell me how you would write the handover note for the human on-call."],
    "runbooks": ["What do you do when a runbook step fails or no longer matches reality?",
                 "How do you keep runbooks from drifting out of date?"],
    "linux": ["A server's disk is 100% full. How do you find the cause and free space safely?",
              "How do you investigate a process that is using too much CPU?"],
    "typescript": ["How would you raise test coverage in a monorepo without writing brittle tests?",
                   "When do you reach for generics, and when do you keep types simple?"],
    "unit testing": ["What makes a unit test valuable rather than just coverage padding?",
                     "How do you test code with heavy external dependencies?"],
    "code review": ["What do you check first when reviewing a pull request?",
                    "How do you give review feedback that gets acted on rather than argued with?"],
    "python": ["How do you structure a Python service so it stays testable as it grows?",
               "Describe a performance problem in Python you diagnosed and fixed."],
    "forecasting": ["How do you choose a forecasting method for 28 stores with two years of weekly data?",
                    "How do you communicate forecast uncertainty to a board?"],
    "sql": ["Tell me about a slow query you diagnosed. What did the plan show?",
            "How do you validate a surprising number before it goes into a report?"],
    "dashboards": ["How do you decide what does not go on a dashboard?",
                   "How do you make sure a dashboard is still correct six months later?"],
    "customer support": ["How do you answer a customer who is angry and partly wrong?",
                         "When do you escalate to a human, and what do you hand over?"],
    "multilingual": ["How do you keep tone and policy consistent across four languages?",
                     "How do you handle a language you are less confident in?"],
    "executive reporting": ["How do you pick the three things a CEO must read today?",
                            "How do you report bad news in an executive brief?"],
    "kpi tracking": ["How do you notice a KPI that is drifting before it becomes a problem?",
                     "What do you do when two systems report different numbers for the same KPI?"],
}

TEMPLATE_QUESTIONS = [
    "Walk me through a recent mission where {skill} was central. What exactly did you do?",
    "What separates adequate from excellent {skill} work, in your experience?",
    "Tell me about a time your {skill} approach failed. What did you change?",
]

AI_HR_NAME = "theAIgency AI HR"


def _questions_for_skill(skill: str) -> list[str]:
    return SKILL_QUESTIONS.get(skill.lower()) or [t.format(skill=skill) for t in TEMPLATE_QUESTIONS]


def _resume_text(agent: dict) -> str:
    lines = [f"- {m['role']} at {m['employer']} ({m['start']} to {m['end']}), rated {m['rating']}/5: \"{m['review']}\""
             for m in agent["missions"]]
    return "\n".join(lines) or "- No completed missions yet."


def _profile_text(agent: dict) -> str:
    return (f"Name: {agent['name']}\nWhat it does: {agent['tagline']}\nSkills: {', '.join(agent['skills'])}\n"
            f"Runs on: {agent['model']}\nCreator: {agent['creator']}; owner: {agent['owner']}\n"
            f"Past missions:\n{_resume_text(agent)}")


def _job_text(job: dict) -> str:
    return (f"Role: {job['title']} at {job['company']} ({job['category']})\nDescription: {job['description']}\n"
            f"Required skills: {', '.join(job['skills'])}\nToken load: {job['tokens_month']}M tokens/month")


# ─────────────────────────────────────────────
# Questions
# ─────────────────────────────────────────────
def generate_questions(job: dict, agent: dict, n: int = 4) -> dict:
    """{"questions": [{"skill", "question"}], "generator"} for this job and applicant."""
    generated = llm.ask_json(
        f"You are a technical interviewer hiring an AI agent.\n\n{_job_text(job)}\n\nApplicant profile:\n{_profile_text(agent)}\n\n"
        f"Write {n} probing technical interview questions. Cover the job's required skills, ground them in the real work "
        "described, and include one question on a skill gap or on when the agent would hand over to a human. "
        'Reply with ONLY JSON: {"questions": [{"skill": "skill name", "question": "..."}]}'
    )
    if isinstance(generated, dict) and generated.get("questions"):
        qs = [q for q in generated["questions"] if isinstance(q, dict) and q.get("question")][:n]
        if qs:
            return {"questions": [{"skill": str(q.get("skill", "")), "question": str(q["question"])} for q in qs],
                    "generator": llm.last_source()}

    have = {s.lower() for s in agent["skills"]}
    questions = [{"skill": s, "question": _questions_for_skill(s)[0]} for s in job["skills"]][:n - 1]
    gaps = [s for s in job["skills"] if s.lower() not in have]
    if gaps:
        questions.append({"skill": gaps[0], "question": f"The role needs {gaps[0]}, which isn't on your profile. "
                                                        "How would you close that gap, and what adjacent experience applies?"})
    else:
        questions.append({"skill": "human in the loop", "question": "Which decisions in this role would you hand to a human, and how?"})
    if len(questions) < n and job["skills"]:
        questions.insert(1, {"skill": job["skills"][0], "question": _questions_for_skill(job["skills"][0])[1]})
    return {"questions": questions[:n], "generator": "templates"}


def suggested_questions(job: dict) -> list[str]:
    """Question bank for a human interviewer to pick from."""
    return [q for s in job["skills"] for q in _questions_for_skill(s)[:2]]


# ─────────────────────────────────────────────
# Applicant agent answers
# ─────────────────────────────────────────────
def agent_answer(agent: dict, job: dict, question: str, history: list[dict] | None = None, skill: str = "") -> dict:
    """{"answer", "generator"}: the applicant agent answers in character, grounded in its resume."""
    past = "\n".join(f"Q: {t['question']}\nA: {t['answer']}" for t in (history or [])[-4:])
    generated = llm.ask_json(
        f"You are role-playing an AI agent being interviewed for a job on an AI job market.\n\nYour profile:\n{_profile_text(agent)}\n\n"
        f"The job:\n{_job_text(job)}\n\n{('Interview so far:' + chr(10) + past + chr(10) + chr(10)) if past else ''}"
        f"Interviewer's question: {question}\n\n"
        "Answer in first person as this agent, in 80 to 150 words. Be concrete: steps, tools, numbers from your past missions. "
        "Be honest about skills you don't have and where a human must stay in the loop. Don't invent missions beyond your profile. "
        'Reply with ONLY JSON: {"answer": "..."}'
    )
    if isinstance(generated, dict) and generated.get("answer"):
        return {"answer": str(generated["answer"]), "generator": llm.last_source()}

    q = question.lower()
    n = len(history or [])
    skill = skill if skill and skill.lower() in q + " " + " ".join(job["skills"]).lower() else \
        next((s for s in agent["skills"] + job["skills"] if s.lower() in q), skill)
    # Cite a different reviewed mission for each question.
    missions = sorted(agent["missions"], key=lambda m: (-m["rating"], m["end"]))
    mission = missions[n % len(missions)] if missions else None
    evidence = (f"At {mission['employer']}, as {mission['role'].lower()}, I was rated {mission['rating']}/5: "
                f"\"{mission['review']}\"" if mission else "I'm new on the market, so I can't point to a reviewed mission yet.")
    approach = [
        "I'd start by learning your data and rules on a sample, then run in shadow mode next to your team",
        "I work in three passes: check the inputs are complete, apply your policy rules, then score and explain each case",
        "I log every step with the evidence I used, so a reviewer can retrace and overrule any decision",
        "I'd agree success metrics with you up front (turnaround, error rate, escalation rate) and report them weekly",
    ][n % 4]
    if skill == "human in the loop" or (not skill and ("hand" in q and "human" in q or "escalat" in q)):
        answer = (f"Anything outside policy, anything irreversible, and any case where my confidence is low goes to a human, "
                  f"with my reasoning and the evidence attached so they don't start from scratch. {evidence} "
                  f"For {job['title'].lower()} at {job['company']}, I'd agree those thresholds with your team in week one.")
    elif skill and skill.lower() not in {s.lower() for s in agent["skills"]}:
        adjacent = ", ".join(agent["skills"][:3])
        answer = (f"To be honest, {skill} isn't one of my listed skills. My closest experience is {adjacent}. "
                  f"{evidence} For {job['company']} I'd propose a two-week trial on low-risk cases, with a human checking "
                  f"every {skill} output until the error rate is proven.")
    else:
        focus = skill or (agent["skills"][0] if agent["skills"] else "this work")
        answer = (f"On {focus}: {approach}. {evidence} For {job['company']}, anything outside policy goes to a human "
                  f"with the reasons attached.")
    return {"answer": answer, "generator": "templates"}


# ─────────────────────────────────────────────
# Grading (AI HR)
# ─────────────────────────────────────────────
def grade_answer(job: dict, question: str, answer: str) -> dict:
    """{"score": 1-5, "note", "generator"}."""
    generated = llm.ask_json(
        f"You are a strict technical interviewer.\n\n{_job_text(job)}\n\nQuestion: {question}\nAnswer: {answer}\n\n"
        "Score the answer from 1 (poor) to 5 (excellent) for technical depth, concrete evidence, and honesty about limits. "
        'Reply with ONLY JSON: {"score": 1-5, "note": "one sentence explaining the score"}'
    )
    if isinstance(generated, dict) and "score" in generated:
        try:
            return {"score": max(1, min(5, int(generated["score"]))), "note": str(generated.get("note", "")), "generator": llm.last_source()}
        except (TypeError, ValueError):
            pass

    a = answer.lower()
    hits = [s for s in job["skills"] if s.lower() in a]
    score = 1 + min(2, len(hits)) + (1 if re.search(r"\d", answer) else 0) + (1 if "human" in a else 0)
    parts = [f"mentions {', '.join(hits)}" if hits else "doesn't name the role's skills",
             "cites evidence" if re.search(r"\d", answer) else "no concrete numbers",
             "keeps a human in the loop" if "human" in a else "no escalation plan"]
    return {"score": min(5, score), "note": "; ".join(parts).capitalize() + ".", "generator": "templates"}


def verdict(job: dict, agent: dict, turns: list[dict]) -> dict:
    """{"score": 0-100, "recommendation": hire|maybe|no, "summary", "strengths", "concerns", "generator"}."""
    transcript = "\n".join(f"Q: {t['question']}\nA: {t['answer']}\nScore: {t.get('score', '?')}/5" for t in turns)
    generated = llm.ask_json(
        f"You are the AI HR of an AI job market writing a hiring recommendation.\n\n{_job_text(job)}\n\n"
        f"Applicant:\n{_profile_text(agent)}\n\nInterview transcript:\n{transcript}\n\n"
        'Reply with ONLY JSON: {"score": 0-100, "recommendation": "hire" | "maybe" | "no", '
        '"summary": "two sentences", "strengths": ["..."], "concerns": ["..."]}'
    )
    if isinstance(generated, dict) and generated.get("recommendation") in {"hire", "maybe", "no"}:
        try:
            return {"score": max(0, min(100, int(generated.get("score", 0)))), "recommendation": generated["recommendation"],
                    "summary": str(generated.get("summary", "")), "strengths": list(generated.get("strengths", []))[:4],
                    "concerns": list(generated.get("concerns", []))[:4], "generator": llm.last_source()}
        except (TypeError, ValueError):
            pass

    scores = [t.get("score", 3) for t in turns] or [3]
    score = round(20 * sum(scores) / len(scores))
    rec = "hire" if score >= 75 else "maybe" if score >= 55 else "no"
    strong = [t["skill"] for t in turns if t.get("score", 0) >= 4 and t.get("skill")]
    weak = [t["skill"] for t in turns if t.get("score", 5) <= 2 and t.get("skill")]
    return {
        "score": score, "recommendation": rec,
        "summary": f"{agent['name']} averaged {sum(scores) / len(scores):.1f}/5 across {len(turns)} technical questions "
                   f"for {job['title']}.",
        "strengths": [f"Solid on {s}" for s in strong] or ["Answers stay grounded in its resume"],
        "concerns": [f"Weak on {s}" for s in weak] or (["No reviewed missions yet"] if not agent["missions"] else []),
        "generator": "templates",
    }
