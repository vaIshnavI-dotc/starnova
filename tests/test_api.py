import io
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.services.scoring import run_scoring_job

client = TestClient(app)


@pytest.fixture(scope="module")
def auth_token():
    # Login as demo user
    res = client.post("/api/v1/auth/login", json={
        "email": "demo@signalnoise.app",
        "password": "demo1234"
    })
    assert res.status_code == 200, res.text
    return res.json()["token"]


def test_preexisting_endpoints_still_respond():
    # Root
    r_root = client.get("/")
    assert r_root.status_code == 200
    assert r_root.json()["success"] is True

    # Meta
    r_meta = client.get("/api/v1/meta")
    assert r_meta.status_code == 200

    # Health
    r_health = client.get("/api/health")
    assert r_health.status_code == 200
    assert r_health.json()["status"] == "ok"

    # Sources
    r_sources = client.get("/api/v1/sources")
    assert r_sources.status_code == 200
    data = r_sources.json()
    assert "sources" in data or "items" in data

    # Coordination
    r_flags = client.get("/api/v1/coordination/flags")
    assert r_flags.status_code == 200

    r_graph = client.get("/api/v1/coordination/graph?ticker=TATAMOTORS")
    assert r_graph.status_code == 200

    # Archive
    r_head = client.get("/api/v1/archive/chain/head")
    assert r_head.status_code == 200

    # Eval results
    r_eval = client.get("/api/v1/eval/results")
    assert r_eval.status_code == 200

    # Analyze
    r_analyze = client.post("/api/v1/analyze", json={"text": "TATAMOTORS target 950"})
    assert r_analyze.status_code in (200, 503)


def test_auth_flow():
    # Signup a new user
    import uuid
    new_email = f"trader_{uuid.uuid4().hex[:8]}@example.com"
    r_signup = client.post("/api/v1/auth/signup", json={
        "name": "Alex Trader",
        "email": new_email,
        "password": "mypassword"
    })
    assert r_signup.status_code == 201, r_signup.text
    s_data = r_signup.json()
    assert "token" in s_data
    assert s_data["user"]["email"] == new_email

    # Login
    r_login = client.post("/api/v1/auth/login", json={
        "email": new_email,
        "password": "mypassword"
    })
    assert r_login.status_code == 200
    token = r_login.json()["token"]

    # Me
    r_me = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert r_me.status_code == 200
    assert r_me.json()["user"]["email"] == new_email


def test_sources_contract_shape(auth_token):
    headers = {"Authorization": f"Bearer {auth_token}"}
    res = client.get("/api/v1/sources", headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert "sources" in data
    sources = data["sources"]
    assert len(sources) >= 2

    # Check contract fields
    s = sources[0]
    for field in [
        "id", "name", "type", "tips_total", "tips_worked",
        "raw_hit_rate", "shrunk_hit_rate", "ci_low", "ci_high",
        "evidence_level", "label"
    ]:
        assert field in s, f"Field {field} missing from source"

    # Evidence level / label rule: label is 'Too early to tell' whenever evidence_level is none or low
    for src in sources:
        if src["evidence_level"] in ("none", "low"):
            assert src["label"] == "Too early to tell"


def test_no_thesis_chain_before_thesis(auth_token):
    headers = {"Authorization": f"Bearer {auth_token}"}
    res = client.post(
        "/api/v1/chat/message",
        headers=headers,
        data={"text": "Neel sent this tip: Tata Motors will hit 950 by next month on massive EV order win and JLR margin expansion."}
    )
    assert res.status_code == 200, res.text
    data = res.json()
    assert data["stage"] == "awaiting_thesis"
    block_types = [b["type"] for b in data["blocks"]]
    assert "claim_card" in block_types
    assert "source_record" in block_types
    assert "context_card" in block_types
    # RULE: No thesis_chain is ever returned before the user has written a thesis
    assert "thesis_chain" not in block_types


def test_image_intake_chat_flow(auth_token):
    headers = {"Authorization": f"Bearer {auth_token}"}
    fake_image = b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00H\x00H\x00\x00\xff\xdb\x00C\x00"
    res = client.post(
        "/api/v1/chat/message",
        headers=headers,
        data={"text": "Check this screenshot"},
        files={"image": ("tip.jpg", fake_image, "image/jpeg")}
    )
    assert res.status_code == 200
    data = res.json()
    assert data["stage"] == "awaiting_thesis"
    conv_id = data["conversation_id"]

    # Retrieve conversation history
    r_conv = client.get(f"/api/v1/conversations/{conv_id}", headers=headers)
    assert r_conv.status_code == 200
    conv_data = r_conv.json()
    assert conv_data["conversation_id"] == conv_id
    assert len(conv_data["messages"]) >= 2  # user + assistant


def test_one_question_per_turn_rule(auth_token):
    headers = {"Authorization": f"Bearer {auth_token}"}
    # 1. Start intake
    r1 = client.post(
        "/api/v1/chat/message",
        headers=headers,
        data={"text": "Tip: Tata Motors will surge"}
    )
    conv_id = r1.json()["conversation_id"]

    # 2. User writes thesis
    r2 = client.post(
        "/api/v1/chat/message",
        headers=headers,
        data={
            "conversation_id": conv_id,
            "text": "JLR margin expansion and domestic EV market share will drive earnings higher."
        }
    )
    assert r2.status_code == 200
    d2 = r2.json()
    assert d2["stage"] == "questioning"
    assert d2["questions_asked"] == 1
    # Check that thesis_chain is present now
    block_types = [b["type"] for b in d2["blocks"]]
    assert "thesis_chain" in block_types
    # Exactly ONE question text block
    text_blocks = [b for b in d2["blocks"] if b["type"] == "text"]
    assert len(text_blocks) == 1
    assert len(d2["quick_replies"]) > 0
    assert d2["quick_replies"][0]["value"] == "__dont_know__"


def test_six_question_cap_and_gate_transition(auth_token):
    headers = {"Authorization": f"Bearer {auth_token}"}
    # 1. Intake
    r1 = client.post(
        "/api/v1/chat/message",
        headers=headers,
        data={"text": "Tata Motors tip for audit"}
    )
    conv_id = r1.json()["conversation_id"]

    # 2. Submit thesis
    r_thesis = client.post(
        "/api/v1/chat/message",
        headers=headers,
        data={
            "conversation_id": conv_id,
            "text": "JLR sales will surge and debt will be paid off."
        }
    )
    assert r_thesis.json()["stage"] == "questioning"

    # 3. Answer questions up to the 6 question cap
    stage = "questioning"
    resp_data = r_thesis.json()
    while resp_data["questions_asked"] < 6 and resp_data["stage"] == "questioning":
        q_count_before = resp_data["questions_asked"]
        r_q = client.post(
            "/api/v1/chat/message",
            headers=headers,
            data={
                "conversation_id": conv_id,
                "text": "__dont_know__"
            }
        )
        assert r_q.status_code == 200
        resp_data = r_q.json()
        if resp_data["stage"] == "questioning":
            assert resp_data["questions_asked"] == q_count_before + 1

    # After 6 questions, it must transition to gate
    if resp_data["stage"] == "questioning" and resp_data["questions_asked"] == 6:
        r_final = client.post(
            "/api/v1/chat/message",
            headers=headers,
            data={
                "conversation_id": conv_id,
                "text": "My final answer"
            }
        )
        resp_data = r_final.json()

    assert resp_data["stage"] == "gate"
    block_types = [b["type"] for b in resp_data["blocks"]]
    assert "decision_gate" in block_types
    gate_block = next(b for b in resp_data["blocks"] if b["type"] == "decision_gate")
    assert gate_block["locked"] is False
    assert gate_block["decision_id"] is not None


def test_gate_validation_incomplete_and_success(auth_token):
    headers = {"Authorization": f"Bearer {auth_token}"}
    # First create a decision via chat flow
    r1 = client.post(
        "/api/v1/chat/message",
        headers=headers,
        data={"text": "Check Tata tip"}
    )
    conv_id = r1.json()["conversation_id"]

    client.post(
        "/api/v1/chat/message",
        headers=headers,
        data={"conversation_id": conv_id, "text": "JLR margin expansion thesis."}
    )

    # Force to gate by answering repeatedly
    resp = client.post("/api/v1/chat/message", headers=headers, data={"conversation_id": conv_id, "text": "30 days"})
    while resp.json()["stage"] == "questioning":
        resp = client.post("/api/v1/chat/message", headers=headers, data={"conversation_id": conv_id, "text": "__dont_know__"})

    assert resp.json()["stage"] == "gate"
    gate_block = next(b for b in resp.json()["blocks"] if b["type"] == "decision_gate")
    decision_id = gate_block["decision_id"]

    # 1. Incomplete gate (missing exit_target)
    r_bad = client.post(
        "/api/v1/decisions/lock",
        headers=headers,
        json={
            "decision_id": decision_id,
            "action": "bought",
            "timeframe_days": 30,
            "max_loss_pct": 8,
            "confidence": 3
            # exit_target missing
        }
    )
    assert r_bad.status_code == 422
    err_body = r_bad.json()
    assert err_body["error"]["code"] == "gate_incomplete"
    assert "exit_target" in err_body["error"]["details"]["missing_fields"]

    # 2. Complete gate
    r_good = client.post(
        "/api/v1/decisions/lock",
        headers=headers,
        json={
            "decision_id": decision_id,
            "action": "bought",
            "timeframe_days": 30,
            "exit_target": 950.0,
            "max_loss_pct": 8.0,
            "confidence": 3
        }
    )
    assert r_good.status_code == 200
    dec = r_good.json()["decision"]
    assert dec["locked_at"] is not None
    assert dec["action"] == "bought"
    assert dec["exit_target"] == 950.0

    # List decisions
    r_list = client.get("/api/v1/decisions", headers=headers)
    assert r_list.status_code == 200
    dec_list = r_list.json()["decisions"]
    assert any(d["id"] == decision_id for d in dec_list)


def test_investment_confirm_only_on_complete_purchase(auth_token):
    headers = {"Authorization": f"Bearer {auth_token}"}
    # 1. Question / intention -> NO investment_confirm
    r_intent = client.post(
        "/api/v1/chat/message",
        headers=headers,
        data={"text": "I'm thinking of buying 10 shares of Tata Motors at 200"}
    )
    assert r_intent.status_code == 200
    assert not any(b["type"] == "investment_confirm" for b in r_intent.json()["blocks"])

    # 2. Missing fields (e.g. date & price missing) -> NO investment_confirm
    r_missing = client.post(
        "/api/v1/chat/message",
        headers=headers,
        data={"text": "I bought 10 shares of TATAMOTORS"}
    )
    assert r_missing.status_code == 200
    assert not any(b["type"] == "investment_confirm" for b in r_missing.json()["blocks"])

    # 3. Complete purchase statement
    r_complete = client.post(
        "/api/v1/chat/message",
        headers=headers,
        data={"text": "Bought 10 TATAMOTORS at 200 on 2026-11-19"}
    )
    assert r_complete.status_code == 200
    blocks = r_complete.json()["blocks"]
    inv_blocks = [b for b in blocks if b["type"] == "investment_confirm"]
    assert len(inv_blocks) == 1
    token = inv_blocks[0]["confirm_token"]
    assert token is not None
    assert inv_blocks[0]["draft"]["ticker"] == "TATAMOTORS"
    assert inv_blocks[0]["draft"]["quantity"] == 10.0
    assert inv_blocks[0]["draft"]["avg_price"] == 200.0

    # 4. Confirm investment via POST /investments/confirm
    r_conf = client.post(
        "/api/v1/investments/confirm",
        headers=headers,
        json={"confirm_token": token}
    )
    assert r_conf.status_code == 201
    assert r_conf.json()["investment"]["ticker"] == "TATAMOTORS"
    assert r_conf.json()["investment"]["quantity"] == 10.0

    # List investments
    r_invs = client.get("/api/v1/investments", headers=headers)
    assert r_invs.status_code == 200
    inv_list = r_invs.json()["investments"]
    assert len(inv_list) >= 1


def test_alerts_endpoints(auth_token):
    headers = {"Authorization": f"Bearer {auth_token}"}
    r_alerts = client.get("/api/v1/alerts", headers=headers)
    assert r_alerts.status_code == 200
    data = r_alerts.json()
    assert "alerts" in data
    assert "unread_count" in data
    assert len(data["alerts"]) >= 3

    # Mark one read
    first_alert = data["alerts"][0]
    r_read = client.post(f"/api/v1/alerts/{first_alert['id']}/read", headers=headers)
    assert r_read.status_code == 200

    # Read all
    r_read_all = client.post("/api/v1/alerts/read_all", headers=headers)
    assert r_read_all.status_code == 200
    assert r_read_all.json()["unread_count"] == 0


def test_insights_endpoint(auth_token):
    headers = {"Authorization": f"Bearer {auth_token}"}
    r_insights = client.get("/api/v1/insights", headers=headers)
    assert r_insights.status_code == 200
    insights = r_insights.json()["insights"]
    assert len(insights) > 0
    assert any("8%+" in i["text"] for i in insights)


def test_scoring_job_manual_execution():
    # Calling manual scoring job function directly
    run_scoring_job()
