"""
tests/benchmark_chat_stream.py

量測 /api/chat/stream 目前的實際回應時間。
不是 pytest 測試（檔名不是 test_ 開頭，pytest 掃描時會自動略過），
是給人手動執行、觀察真實回應速度用的小工具。

量兩個數字：
1. TTFT (Time To First Token)：從送出請求，到收到第一個「真正回答內容」
   （event 類型為預設/message 的 data 行，排除 session 與 done 事件）為止的秒數。
   反映「使用者要等多久才看到 AI 開始打字」。
2. Total time：整段回答串流完成的總時間。

用法：
    1. 另開一個終端機，先啟動後端：python main.py（監聽在 http://127.0.0.1:8000），
       這個視窗保持開著不要關。
    2. 在這個終端機執行：python tests/benchmark_chat_stream.py

可用環境變數調整：
    BENCHMARK_BASE_URL    後端網址，預設 http://127.0.0.1:8000
    BENCHMARK_ROUNDS      要送幾次請求取平均，預設 5
    BENCHMARK_QUESTION    測試用的問題文字
"""

import json
import os
import statistics
import time
import urllib.request

BASE_URL = os.getenv("BENCHMARK_BASE_URL", "http://127.0.0.1:8000")
ROUNDS = int(os.getenv("BENCHMARK_ROUNDS", "5"))
QUESTION = os.getenv("BENCHMARK_QUESTION", "太陽的表面溫度大概是幾度？")


def run_once(round_no: int) -> dict:
    payload = json.dumps(
        {
            "question": QUESTION,
            "session_id": f"benchmark_{round_no}_{int(time.time())}",
            "top_k": 3,
        }
    ).encode("utf-8")

    req = urllib.request.Request(
        f"{BASE_URL}/api/chat/stream",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    t_start = time.perf_counter()
    t_first_token = None
    chunk_count = 0

    # 依照 SSE 規範正確追蹤目前所在的 event 區塊，
    # 而不是用字串窗口去猜——避免像之前那樣誤判 session/done 事件為內容。
    current_event = "message"  # SSE 預設事件類型

    with urllib.request.urlopen(req) as resp:
        for raw_line in resp:
            line = raw_line.decode("utf-8", errors="ignore").rstrip("\r\n")

            if line == "":
                # 空行代表一個 SSE 區塊結束，下一個區塊預設回到 "message"
                current_event = "message"
                continue

            if line.startswith("event:"):
                current_event = line[len("event:") :].strip()
                continue

            if line.startswith("data:"):
                data_value = line[len("data:") :].strip()

                if current_event == "session":
                    continue  # 這是 session_id，不是回答內容
                if current_event == "done" or data_value == "[DONE]":
                    continue  # 這是結束標記，不是回答內容

                # 真正的回答內容 chunk
                if t_first_token is None:
                    t_first_token = time.perf_counter()
                chunk_count += 1

    t_end = time.perf_counter()

    ttft = (t_first_token - t_start) if t_first_token else None
    total = t_end - t_start

    print(
        (
            f"  round {round_no}: TTFT={ttft:.3f}s"
            if ttft is not None
            else f"  round {round_no}: TTFT=N/A（沒有偵測到內容）"
        ),
        f"| total={total:.3f}s | chunks={chunk_count}",
    )
    return {"ttft": ttft, "total": total}


def main():
    print(f"對 {BASE_URL}/api/chat/stream 送出 {ROUNDS} 次請求...")
    print(f"問題：「{QUESTION}」\n")

    results = []
    for i in range(1, ROUNDS + 1):
        try:
            results.append(run_once(i))
        except Exception as e:
            print(f"  round {i}: 失敗 ({e})")
        time.sleep(1)

    ttfts = [r["ttft"] for r in results if r["ttft"] is not None]
    totals = [r["total"] for r in results if r["total"] is not None]

    print("\n===== 結果彙總 =====")
    if ttfts:
        print(
            f"TTFT  平均: {statistics.mean(ttfts):.3f}s | 中位數: {statistics.median(ttfts):.3f}s | 最慢: {max(ttfts):.3f}s"
        )
    if totals:
        print(
            f"Total 平均: {statistics.mean(totals):.3f}s | 中位數: {statistics.median(totals):.3f}s | 最慢: {max(totals):.3f}s"
        )


if __name__ == "__main__":
    main()
