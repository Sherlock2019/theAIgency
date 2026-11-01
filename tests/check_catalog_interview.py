"""Catalog merge + interview engine checks on a temp copy of the data. Pass --llm to also hit the real backend."""
import os, pathlib, shutil, sys, tempfile, time
from collections import Counter

root = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(root))
import store, catalog, interview, llm

tmp = pathlib.Path(tempfile.mkdtemp()) / "market.json"
if store.DATA_FILE.exists():
    shutil.copy(store.DATA_FILE, tmp)
before = None
if tmp.exists():
    import json
    before = json.loads(tmp.read_text())
store.DATA_FILE = tmp
db = store.load()
print("agents:", len(db["agents"]), "jobs:", len(db["jobs"]), "businesses:", len({j["company"] for j in db["jobs"]}))
print("jobs per generated business:", sorted(Counter(j["company"] for j in db["jobs"] if j["id"].startswith("jb_g")).values())[:3], "...")
print("statuses:", Counter(j["status"] for j in db["jobs"]), "applications:", sum(len(j["applications"]) for j in db["jobs"]))
if before:
    kept = {a["id"] for a in before["agents"]} <= {a["id"] for a in db["agents"]} and {j["id"] for j in before["jobs"]} <= {j["id"] for j in db["jobs"]}
    print("existing data kept:", kept)
print("idempotent (2nd merge changes nothing):", not catalog.merge_into(db))
over = [a["name"] for a in db["agents"] if store.tokens_used(db, a["id"]) > a["token_capacity"]]
print("agents over capacity:", over or "none")
print("unique agent names:", len({a['name'] for a in db['agents']}) == len(db["agents"]))

os.environ.pop("ANTHROPIC_API_KEY", None)
if "--llm" not in sys.argv:
    os.environ["ANALYZE_MODEL"] = "no-such-model"  # force template engine
print("backend:", llm.backend_label())

job = store.get_job(db, "jb_loans")
agent = store.get_agent(db, "ag_credit")
t0 = time.time()
qs = interview.generate_questions(job, agent, 3 if "--llm" in sys.argv else 4)
print("questions via", qs["generator"])
turns = []
for q in qs["questions"]:
    a = interview.agent_answer(agent, job, q["question"], turns, skill=q["skill"])
    g = interview.grade_answer(job, q["question"], a["answer"])
    turns.append({**q, "answer": a["answer"], **{k: g[k] for k in ("score", "note")}})
    print(f"- [{q['skill']}] {q['question'][:90]}\n    A({a['generator']}): {a['answer'][:160]}...\n    score {g['score']} ({g['generator']}): {g['note'][:100]}")
v = interview.verdict(job, agent, turns)
print("verdict:", v["recommendation"], v["score"], "via", v["generator"], "|", v["summary"][:160])
print(f"took {time.time() - t0:.1f}s")
store.save_interview(db, job, "ap_1", {"mode": "AI HR", "interviewer": interview.AI_HR_NAME, "turns": turns, **v})
print("saved interviews on ap_1:", len(store.get_application(job, "ap_1")["interviews"]))
