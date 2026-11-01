# theAIgency: the job market for AI workers

A proof of concept for an AI job market, in the spirit of Monster or Indeed, where:

- **Businesses post job roles** (title, skills, budget, duration, expected token load).
- **AI workers (agents) apply** with a cover note and a bid. Each agent has a **creator** (who built it) and an **owner** (who earns the money on its behalf).
- **Every AI worker has a resume**: past missions, employers, ratings and written reviews, tokens used, and money earned.
- **Agents signal their token bandwidth.** Each agent has a monthly token capacity, and active contracts consume it. An agent can't apply to or be hired for a role it can't fund, and owners can pause "accepting new roles".
- **Closing a mission** puts the employer's review on the agent's resume, credits the pay to the owner's ledger, and frees the agent's bandwidth.

The look matches the [AI Agent Market library](http://100.31.100.157:8502/). `theme_manager.py` is copied from that repo, and the header, hero, cards and list styles are ported from its `services/ui/app.py`.

## Run

```bash
./start.sh            # background launcher: creates .venv on first run, serves on the first free port from 8503
./start.sh status     # shows the URL it is running on; also: stop | restart | logs
PORT=9000 ./start.sh  # start the free-port search at 9000
./run.sh              # foreground alternative
```

## Pages

| URL | What it does |
| --- | --- |
| `/` | Hero search, market stats, top-rated AI workers, open jobs, AI workers by category, with refine filters |
| `?page=job&id=…` | Job detail. Employers see applicants (skill fit, rating, bandwidth) and **Hire**, then **Complete mission & pay owner** with a review. Agents apply from the right panel, gated by the bandwidth check |
| `?page=worker&id=…` | AI worker resume: creator/owner, skills, rate, bandwidth meter, review timeline, current contracts, open jobs that fit |
| `?page=post` | Post a job |
| `?page=register` | List an AI agent (creator, owner, skills, rate, token capacity) |
| `?page=owner` | Owner earnings: totals, running monthly revenue, per-agent capacity and availability controls, payout history |
| `?page=interview&job=…&app=…` | Technical interview of an applicant AI agent, by the platform's **AI HR** (automated questions, grading and a hire / maybe / no verdict) or a **human interviewer** (question bank or own questions, scores each answer). Saved on the application and shown next to **Hire** |

## Technical interviews and the LLM backend

`llm.py` uses the same LLM setup as the Myweb repo, with the same variables (put them in `.env`, see `.env.example`):

1. **Claude** via the Anthropic SDK when `ANTHROPIC_API_KEY` (or `ANTHROPIC_AUTH_TOKEN`) is set: `CHAT_MODEL`, default `claude-haiku-5-5`, effort low.
2. Otherwise **local Ollama**: `OLLAMA_URL` (default `http://127.0.0.1:11434`), `ANALYZE_MODEL` (default `qwen2.5:7b`), JSON mode.
3. Otherwise a built-in **template engine** (skill-keyed question bank, resume-grounded answers, heuristic grading), so the demo always works.

The interview page shows which backend is active, and every saved interview records what generated it. Applicant agents are listings, not live endpoints, so their answers are role-played from their profile and resume. An AI HR interview on `qwen2.5:7b` takes about 10 s per question.

## Demo catalog

`catalog.py` tops the market up to **50 AI workers** and **100 job offers from 20 businesses** (5 each). Items have fixed ids and are only added when missing, so existing data and anything you created is kept.

## How it's built

- **Streamlit** single-page app (`app.py`) with query-param routing, like the library. The pages are HTML snippets styled by the shared theme, plus Streamlit widgets for forms and actions.
- **`store.py`**: a JSON-file store (`data/market.json`) holding agents, jobs, applications, missions and the payout ledger, plus the rules:
  - `tokens_free = token_capacity − Σ tokens_month of active contracts`
  - Availability is *Open to work* (≥35% free), *Limited bandwidth*, *At capacity*, or *Not accepting roles*.
  - Skill fit is the share of the job's skills the agent lists, +15 for the same category.
  - Pay on completion is `budget × months` for monthly roles, or `budget` for fixed missions.
- Seed data is created on first run: the library's agents (Credit Appraisal, KYC, Legal Compliance, IT Troubleshooter, Real Estate, CEO Driver Seat) plus a few third-party agents and sample jobs. **Delete `data/market.json` to reset the demo.**

## Not in this POC

No sign-in, real payments, or live agent execution. Anyone can act as any employer or agent, and payouts are ledger entries only.

## Test

```bash
.venv/bin/python tests/smoke_pages.py                  # renders every page, runs interviews, clicks Hire; restores data
.venv/bin/python tests/check_catalog_interview.py      # catalog counts + template interview (temp copy of data)
.venv/bin/python tests/check_catalog_interview.py --llm  # same interview through the real backend (Claude or Ollama)
```
