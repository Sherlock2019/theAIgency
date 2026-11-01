import os, pathlib, sys
from streamlit.testing.v1 import AppTest

root = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(root))
os.environ["ANALYZE_MODEL"] = "no-such-model"  # template engine: fast and offline
os.environ.pop("ANTHROPIC_API_KEY", None)
os.chdir(root)
data = root / "data" / "market.json"
backup = data.read_bytes() if data.exists() else None

routes = [{}, {"page": "worker", "id": "ag_credit"}, {"page": "worker", "id": "ag_realestate"},
          {"page": "job", "id": "jb_loans"}, {"page": "job", "id": "jb_support"},
          {"page": "post"}, {"page": "register"}, {"page": "owner"}, {"page": "job", "id": "nope"},
          {"page": "interview", "job": "jb_loans", "app": "ap_1"}, {"page": "worker", "id": "ag_g17"},
          {"page": "job", "id": "jb_g050"}]
try:
    for qp in routes:
        at = AppTest.from_file(str(root / "app.py"), default_timeout=30)
        for k, v in qp.items():
            at.query_params[k] = v
        at.run()
        print(qp or "home", "OK" if not at.exception else f"EXC {[x.value for x in at.exception]}",
              "| md blocks:", len(at.markdown), "buttons:", len(at.button))

    # search on home
    at = AppTest.from_file(str(root / "app.py"), default_timeout=30); at.run()
    at.text_input(key="mk_search").input("kyc").run()
    print("search kyc:", "OK" if not at.exception else at.exception, "| has KYC:", any("Anti-Fraud" in m.value for m in at.markdown))

    # AI HR interview via UI
    at = AppTest.from_file(str(root / "app.py"), default_timeout=60)
    at.query_params.update({"page": "interview", "job": "jb_loans", "app": "ap_1"}); at.run()
    at.button(key="iv_jb_loans_ap_1_run").click().run()
    print("AI HR interview:", "OK" if not at.exception else at.exception, "| success:", [s.value for s in at.success][:1])

    # human interviewer asks one bank question
    at = AppTest.from_file(str(root / "app.py"), default_timeout=60)
    at.query_params.update({"page": "interview", "job": "jb_loans", "app": "ap_1"}); at.run()
    at.radio(key="iv_jb_loans_ap_1_mode").set_value("Human interviewer").run()
    at.selectbox[0].select_index(1).run()
    at.button[0].click().run()
    print("human question:", "OK" if not at.exception else at.exception,
          "| answered:", any("Credit Appraisal Agent:" in m.value for m in at.markdown))

    # hire via UI on jb_loans
    at = AppTest.from_file(str(root / "app.py"), default_timeout=30); at.query_params["page"] = "job"; at.query_params["id"] = "jb_loans"; at.run()
    at.button(key="hire_ap_1").click().run()
    print("hire click:", "OK" if not at.exception else at.exception, "| success:", [s.value for s in at.success][:1])
finally:
    if backup is not None:
        data.write_bytes(backup)
    elif data.exists():
        data.unlink()
