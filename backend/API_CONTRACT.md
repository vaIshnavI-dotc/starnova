# SIGNAL / NOISE API CONTRACT (v1, FIXED: do not rename fields or change shapes)

## Conventions
- Base URL: http://localhost:8000/api/v1
- JSON everywhere (except POST /chat/message, which is multipart/form-data)
- All field names are snake_case. All ids are strings. All timestamps are ISO 8601 UTC.
- Prices are INR numbers. Percentages are plain numbers (6.2 means 6.2%). Rates are 0 to 1.
- Auth: header  Authorization: Bearer <token>  on every endpoint except signup, login and health.
- CORS: backend allows http://localhost:5173 and http://localhost:3000.
- Error shape (any non-2xx):
  {"error": {"code": "string", "message": "string", "details": {}}}
  Codes: unauthorized (401), not_found (404), validation_error (422), gate_incomplete (422), server_error (500).

## Auth
POST /auth/signup   body {name, email, password}  -> 201 {token, user}
POST /auth/login    body {email, password}        -> 200 {token, user}
GET  /auth/me                                      -> 200 {user}
user = {id, name, email}
Demo account seeded on startup: demo@signalnoise.app / demo1234

## Chat (the core)
POST /chat/message   multipart/form-data fields:
  conversation_id (optional; omit to start a new conversation)
  text (optional string)
  image (optional file; at least one of text or image is required)
-> 200
{
  "conversation_id": "c_1",
  "stage": "intake|awaiting_thesis|auditing|questioning|gate|locked|chitchat",
  "questions_asked": 0,
  "questions_max": 6,
  "blocks": [ Block, ... ],
  "quick_replies": [ {"label": "Don't know", "value": "__dont_know__"} ]
}
GET /conversations/{conversation_id} -> 200
{ "conversation_id": "c_1", "stage": "...", "questions_asked": 0, "questions_max": 6,
  "messages": [ {"id": "m_1", "role": "user|assistant", "created_at": "...",
                 "image_url": null, "blocks": [ Block, ... ]} ] }
User messages contain a single text block. Assistant messages contain one or more blocks.

### Block types (every block has a "type")
{"type":"text", "content":"string"}

{"type":"claim_card", "tip_id":"t_9", "sender":"Neel", "source_id":"s_2",
 "stock":{"name":"Tata Motors","ticker":"TATAMOTORS"},
 "claim":"string", "red_flags":["urgency","unsupported_claim","guaranteed_returns"]}

{"type":"source_record", "source_id":"s_2", "source_name":"Neel",
 "tips_total":4, "tips_worked":1, "shrunk_hit_rate":0.31,
 "evidence_level":"none|low|medium|high", "label":"Too early to tell"}

{"type":"context_card", "ticker":"TATAMOTORS", "price_now":812.4,
 "change_7d_pct":6.2, "since_tip_pct":null, "note":"Already up 6.2% in the last 7 days."}

{"type":"thesis_chain", "links":[
   {"id":"l_1","text":"string","status":"backed|unchecked|no_evidence",
    "evidence":{"summary":"string","source_url":"string or null"}} ],
 "gaps_count":3, "total_links":6, "summary":"3 of 6 links have no evidence."}
(evidence is null when status is unchecked or no_evidence)

{"type":"decision_gate", "decision_id":"d_1", "tip_id":"t_9",
 "required_fields":["action","timeframe_days","exit_target","max_loss_pct","confidence"],
 "values":{"action":null,"timeframe_days":null,"exit_target":null,"max_loss_pct":null,"confidence":null},
 "locked":false, "locked_at":null}

{"type":"insight", "text":"You've bought after an 8%+ jump 4 times. 3 lost money."}

{"type":"investment_confirm", "confirm_token":"string",
 "draft":{"ticker":"TATAMOTORS","stock_name":"Tata Motors","quantity":10,
          "avg_price":200,"purchase_date":"2026-11-19"}}

### Chat rules (backend enforces; frontend relies on them)
- First reply to a tip: claim_card, then source_record, then context_card, then a text block asking the user to write their own reasoning. stage = awaiting_thesis.
- No thesis_chain is ever returned before the user has written a thesis.
- After the thesis: thesis_chain, then ONE question at a time as a text block (stage = questioning). Maximum questions_max (6) per tip. quick_replies always includes {"label":"Don't know","value":"__dont_know__"} while questioning. Sending __dont_know__ logs an unverified link.
- After the last question (or when 6 are used): a decision_gate block, stage = gate.
- insight blocks appear only when a stored pattern is relevant.
- investment_confirm is returned ONLY when the user clearly states a completed purchase with ticker, quantity, price and date. Questions like "what do you think of Tata?" or intentions like "I'm thinking of buying Tata" never create one. If details are missing, the assistant asks for them in a text block.
- The assistant never says buy, sell, or that something is a good investment.

## Decisions
POST /decisions/lock  body:
{ "decision_id":"d_1", "action":"bought|skipped|watching", "timeframe_days":30,
  "exit_target":950, "max_loss_pct":8, "confidence":3 }
-> 200 {"decision":{"id","tip_id","action","timeframe_days","exit_target","max_loss_pct","confidence","thesis","gaps_count","locked_at"}}
-> 422 gate_incomplete with details {"missing_fields":["exit_target"]}
Validation: timeframe_days integer > 0; exit_target number > 0; max_loss_pct number > 0 and <= 100; confidence integer 1 to 5; action one of the three values.
GET /decisions -> 200 {"decisions":[ same decision object, plus "stock":{name,ticker}, "source_name" ]}

## Investments
POST /investments/confirm  body {confirm_token, ticker?, quantity?, avg_price?, purchase_date?}
  (optional fields are user edits that override the draft) -> 201 {"investment": Investment}
GET /investments -> 200 {"investments":[ Investment ]}
Investment = {id, ticker, stock_name, quantity, avg_price, purchase_date,
              current_price (null if unavailable), current_value (null if unavailable), linked_tip_id (or null)}
GET /insights -> 200 {"insights":[ {"id":"i_1","text":"string","evidence_count":4} ]}

## Alerts
GET  /alerts -> 200
{ "unread_count":2, "alerts":[ {
   "id":"a_1", "type":"outcome_confirmed|negative_outcome|new_update",
   "title":"string", "body":"string", "tip_id":"t_3", "source_name":"Neel",
   "results":{ "d7":R, "d30":R, "d90":R }, "created_at":"...", "read":false } ] }
R = {"status":"worked|missed|pending", "return_pct":4.1, "benchmark_pct":1.2} (return_pct and benchmark_pct are null while pending)
POST /alerts/{id}/read -> 200 {"unread_count":1}
POST /alerts/read_all  -> 200 {"unread_count":0}

## Sources (profile page)
GET /sources -> 200
{ "sources":[ {"id","name","type":"friend|anonymous|finfluencer","tips_total","tips_worked",
               "raw_hit_rate","shrunk_hit_rate","ci_low","ci_high",
               "evidence_level":"none|low|medium|high","label":"Too early to tell"} ] }
(Existing endpoint: keep all existing fields and add any missing ones above.)

## Existing endpoints that stay exactly as they are (frontend does not use them)
GET /, /meta, /sources/{id}, /tips/{id}, /coordination/flags, /coordination/graph,
/archive/*, POST /analyze, /eval/*, GET /api/health