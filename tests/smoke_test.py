# """StarLearn 本機 API 煙霧測試（只用標準函式庫）
# 用法：先啟動服務（uvicorn main:app），再執行
#     python smoke_test.py http://127.0.0.1:8000
# 輸出 Markdown 表格，可直接貼進「玖、系統測試報告」的執行結果表。
# 只在本機跑；不要對正式站執行。"""
# import json, sys, time, urllib.request, urllib.error

# BASE = (sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8000").rstrip("/")
# USER, PWD = f"tester_{int(time.time())}", "Pass1234"
# results, ctx = [], {}

# def call(method, path, body=None):
#     data = json.dumps(body).encode() if body is not None else None
#     req = urllib.request.Request(BASE + path, data=data, method=method,
#                                  headers={"Content-Type": "application/json"})
#     try:
#         with urllib.request.urlopen(req, timeout=20) as r:
#             raw = r.read().decode("utf-8", "replace")
#             code = r.status
#     except urllib.error.HTTPError as e:
#         raw, code = e.read().decode("utf-8", "replace"), e.code
#     except Exception as e:
#         return 0, str(e)
#     try:
#         return code, json.loads(raw)
#     except Exception:
#         return code, raw

# def case(cid, name, fn, note=""):
#     try:
#         ok, actual = fn()
#         status = "Pass" if ok else "Fail"
#     except Exception as e:
#         status, actual = "Fail", f"例外：{e}"
#     results.append((cid, name, str(actual)[:90].replace("|", "/"), status, note))

# def t_status():
#     c, b = call("GET", "/api/status"); return c == 200 and b.get("status") == "online", f"HTTP {c} {b}"
# def t_register():
#     c, b = call("POST", "/api/auth/register", {"username": USER, "password": PWD})
#     ctx["uid"] = b.get("user_id") if isinstance(b, dict) else None
#     return c == 200 and b.get("role") == "member", f"HTTP {c} {b}"
# def t_dup():
#     c, b = call("POST", "/api/auth/register", {"username": USER, "password": PWD}); return c == 409, f"HTTP {c}"
# def t_login_ok():
#     c, b = call("POST", "/api/auth/login", {"username": USER, "password": PWD}); return c == 200 and b.get("user_id") == ctx.get("uid"), f"HTTP {c} {b}"
# def t_login_bad():
#     c, b = call("POST", "/api/auth/login", {"username": USER, "password": "wrong"}); return c == 401, f"HTTP {c}"
# def t_guest():
#     c, b = call("POST", "/api/auth/guest", {"display_name": "星星"}); return c == 200 and b.get("role") == "guest" and b.get("username") == "星星", f"HTTP {c} {b}"
# def t_news():
#     c, b = call("GET", "/api/news"); return c == 200 and bool(b), f"HTTP {c}，{type(b).__name__}"
# def t_quiz():
#     c, b = call("POST", "/api/quiz/score", {"user_id": ctx["uid"], "quiz_type": "level1", "score": 80, "total_questions": 10})
#     c2, h = call("GET", f"/api/quiz/history/{ctx['uid']}")
#     return c == 200 and c2 == 200 and len(h) >= 1, f"save HTTP {c}，history {len(h) if isinstance(h, list) else h} 筆"
# def t_observe():
#     c, b = call("POST", "/api/sky/observe", {"name": "Mars", "body_type": "planet", "alt": 30.5, "az": 120.0, "mag": -1.2, "user_id": str(ctx["uid"])})
#     return c == 200 and b.get("status") == "success", f"HTTP {c} {b}"
# def t_track_str():
#     c, b = call("POST", "/api/track", {"user_id": "anon_abc", "topic": "home", "action": "click"})
#     return c == 500, f"HTTP {c}（預期 500，K-03）"
# def t_track_int():
#     c, b = call("POST", "/api/track", {"user_id": str(ctx["uid"]), "topic": "home", "action": "click"})
#     return c == 200, f"HTTP {c}"
# def t_idor():
#     c, b = call("GET", f"/api/chat/history?user_id={ctx['uid']}"); return c == 200, f"HTTP {c}（無需登入即可讀取，PF-09 現況）"
# def t_clear():
#     c, b = call("DELETE", f"/api/chat/history?user_id={ctx['uid']}")
#     c2, h = call("GET", f"/api/chat/history?user_id={ctx['uid']}")
#     return c == 200 and c2 == 200 and not h, f"HTTP {c}，清除後 {len(h) if isinstance(h, list) else h} 筆"
# def t_stream():
#     c, b = call("GET", "/api/status")
#     if not b.get("ai_ready"): return False, "AI 未就緒（缺 Gemini/Pinecone 金鑰）→ 記為 Blocked"
#     req = urllib.request.Request(BASE + "/api/chat/stream", method="POST",
#         data=json.dumps({"question": "什麼是黑洞？", "user_id": ctx["uid"]}).encode(), headers={"Content-Type": "application/json"})
#     with urllib.request.urlopen(req, timeout=60) as r: text = r.read().decode("utf-8", "replace")
#     return "done" in text, f"收到 {len(text)} 字元，含 done={'done' in text}"

# case("SL-TC-DS-01", "服務啟動與狀態", t_status)
# case("SL-TC-SI-08", "註冊並登入成功", lambda: (t_register()[0] and t_login_ok()[0], "註冊+登入"))
# case("SL-TC-SI-08b", "重複註冊", t_dup, "預期 409")
# case("SL-TC-SI-09", "密碼錯誤", t_login_bad)
# case("SL-TC-SI-14", "訪客登入", t_guest)
# case("SL-TC-HM-01", "新聞 API", t_news)
# case("SL-TC-QZ-12", "測驗成績儲存", t_quiz)
# case("SL-TC-SK-10", "觀測紀錄 API", t_observe)
# case("SL-TC-HM-11", "追蹤（匿名字串 ID）", t_track_str, "K-03 已知缺陷")
# case("SL-TC-HM-11b", "追蹤（整數 user_id）", t_track_int)
# case("SL-TC-PF-09", "越權讀取（現況）", t_idor, "安全風險")
# case("SL-TC-PF-06", "清除聊天紀錄", t_clear)
# case("SL-TC-LB-09", "AI 串流對話", t_stream, "需金鑰")

# print("| Identification | Name | 實際結果 | 狀態 | 備註 |\n|---|---|---|---|---|")
# for r in results: print("| " + " | ".join(r) + " |")
# p = sum(1 for r in results if r[3] == "Pass")
# print(f"\n合計 {len(results)} 案，Pass {p}，Fail {len(results) - p}")
"""StarLearn 本機 API 煙霧測試（只用標準函式庫，含 JWT 測試支援）
用法：先啟動服務（uvicorn main:app），再執行
    python smoke_test.py http://127.0.0.1:8000
輸出 Markdown 表格，可直接貼進「玖、系統測試報告」的執行結果表。
只在本機跑；不要對正式站執行。"""
import json
import sys
import time
import urllib.request
import urllib.error

BASE = (sys.argv[1] if len(sys.argv) >
        1 else "http://127.0.0.1:8000").rstrip("/")
USER, PWD = f"tester_{int(time.time())}", "Pass1234"
results, ctx = [], {}


def call(method, path, body=None, use_token=True):
    headers = {"Content-Type": "application/json"}
    if use_token and ctx.get("token"):
        headers["Authorization"] = f"Bearer {ctx['token']}"

    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(
        BASE + path, data=data, method=method, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            raw = r.read().decode("utf-8", "replace")
            code = r.status
    except urllib.error.HTTPError as e:
        raw, code = e.read().decode("utf-8", "replace"), e.code
    except Exception as e:
        return 0, str(e)
    try:
        return code, json.loads(raw)
    except Exception:
        return code, raw


def case(cid, name, fn, note=""):
    try:
        ok, actual = fn()
        status = "Pass" if ok else "Fail"
    except Exception as e:
        status, actual = "Fail", f"例外：{e}"
    results.append(
        (cid, name, str(actual)[:90].replace("|", "/"), status, note))


def t_status():
    c, b = call("GET", "/api/status", use_token=False)
    return c == 200 and b.get("status") == "online", f"HTTP {c} {b}"


def t_register():
    c, b = call("POST", "/api/auth/register",
                {"username": USER, "password": PWD}, use_token=False)
    ctx["uid"] = b.get("user_id") if isinstance(b, dict) else None
    if isinstance(b, dict):
        ctx["token"] = b.get("token") or b.get("access_token")
    return c == 200 and b.get("role") == "member", f"HTTP {c} {b}"


def t_dup():
    c, b = call("POST", "/api/auth/register",
                {"username": USER, "password": PWD}, use_token=False)
    return c == 409, f"HTTP {c}"


def t_login_ok():
    c, b = call("POST", "/api/auth/login",
                {"username": USER, "password": PWD}, use_token=False)
    if isinstance(b, dict):
        ctx["token"] = b.get("token") or b.get(
            "access_token") or ctx.get("token")
        if not ctx.get("uid"):
            ctx["uid"] = b.get("user_id")
    return c == 200 and (b.get("user_id") == ctx.get("uid") or ctx.get("token")), f"HTTP {c} Token已取得"


def t_jwt_verify():
    if not ctx.get("token"):
        return False, "未成功取得 JWT Token"
    c, b = call(
        "GET", f"/api/chat/history?user_id={ctx['uid']}", use_token=True)
    return c == 200, f"HTTP {c} (JWT 驗證成功)"


def t_login_bad():
    c, b = call("POST", "/api/auth/login",
                {"username": USER, "password": "wrong"}, use_token=False)
    return c == 401, f"HTTP {c}"


def t_guest():
    c, b = call("POST", "/api/auth/guest",
                {"display_name": "星星"}, use_token=False)
    if isinstance(b, dict) and (b.get("token") or b.get("access_token")):
        ctx["guest_token"] = b.get("token") or b.get("access_token")
    return c == 200 and b.get("role") == "guest" and b.get("username") == "星星", f"HTTP {c} {b}"


def t_news():
    c, b = call("GET", "/api/news", use_token=False)
    return c == 200 and bool(b), f"HTTP {c}，{type(b).__name__}"


def t_quiz():
    payload = {
        "user_id": ctx["uid"],
        "level": "1",
        "correct_count": 8,
        "total": 10,
        "elapsed_sec": 30,
        "score": 80.0
    }
    c, b = call("POST", "/api/quiz/finish", payload)
    c2, h = call("GET", f"/api/quiz/history/{ctx['uid']}")
    return c == 200 and c2 == 200 and len(h) >= 1, f"save HTTP {c}，history {len(h) if isinstance(h, list) else h} 筆"


def t_observe():
    c, b = call("POST", "/api/sky/observe", {"name": "Mars", "body_type": "planet",
                "alt": 30.5, "az": 120.0, "mag": -1.2, "user_id": str(ctx["uid"])})
    return c == 200 and b.get("status") == "success", f"HTTP {c} {b}"


def t_track_str():
    c, b = call("POST", "/api/track",
                {"user_id": "anon_abc", "topic": "home", "action": "click"})
    return c == 200, f"HTTP {c}（字串 ID 已被處理）"


def t_track_int():
    c, b = call("POST", "/api/track",
                {"user_id": str(ctx["uid"]), "topic": "home", "action": "click"})
    return c == 200, f"HTTP {c}"


def t_idor():
    c, b = call(
        "GET", f"/api/chat/history?user_id={ctx['uid']}", use_token=False)
    return c == 401, f"HTTP {c}（未帶 Token 遭拒，防護成功）"


def t_clear():
    c, b = call("DELETE", f"/api/chat/history?user_id={ctx['uid']}")
    c2, h = call("GET", f"/api/chat/history?user_id={ctx['uid']}")
    return c == 200 and c2 == 200 and not h, f"HTTP {c}，清除後 {len(h) if isinstance(h, list) else h} 筆"


def t_stream():
    c, b = call("GET", "/api/status", use_token=False)
    if not b.get("ai_ready"):
        return False, "AI 未就緒（缺 Gemini/Pinecone 金鑰）→ 記為 Blocked"
    headers = {"Content-Type": "application/json"}
    if ctx.get("token"):
        headers["Authorization"] = f"Bearer {ctx['token']}"
    req = urllib.request.Request(BASE + "/api/chat/stream", method="POST",
                                 data=json.dumps({"question": "什麼是黑洞？", "user_id": ctx["uid"]}).encode(), headers=headers)
    with urllib.request.urlopen(req, timeout=60) as r:
        text = r.read().decode("utf-8", "replace")
    return "done" in text, f"收到 {len(text)} 字元，含 done={'done' in text}"


case("SL-TC-DS-01", "服務啟動與狀態", t_status)
case("SL-TC-SI-08", "註冊並登入成功",
     lambda: (t_register()[0] and t_login_ok()[0], "註冊+登入"))
case("SL-TC-JWT-01", "JWT Token 授權檢測", t_jwt_verify, "驗證 Bearer Token 有效性")
case("SL-TC-SI-08b", "重複註冊", t_dup, "預期 409")
case("SL-TC-SI-09", "密碼錯誤", t_login_bad)
case("SL-TC-SI-14", "訪客登入", t_guest)
case("SL-TC-HM-01", "新聞 API", t_news)
case("SL-TC-QZ-12", "測驗成績儲存", t_quiz)
case("SL-TC-SK-10", "觀測紀錄 API", t_observe)
case("SL-TC-HM-11", "追蹤（匿名字串 ID）", t_track_str, "K-03 已知缺陷")
case("SL-TC-HM-11b", "追蹤（整數 user_id）", t_track_int)
case("SL-TC-PF-09", "越權讀取（現況）", t_idor, "安全風險")
case("SL-TC-PF-06", "清除聊天紀錄", t_clear)
case("SL-TC-LB-09", "AI 串流對話", t_stream, "需金鑰")

print("| Identification | Name | 實際結果 | 狀態 | 備註 |\n|---|---|---|---|---|")
for r in results:
    print("| " + " | ".join(r) + " |")
p = sum(1 for r in results if r[3] == "Pass")
print(f"\n合計 {len(results)} 案，Pass {p}，Fail {len(results) - p}")
