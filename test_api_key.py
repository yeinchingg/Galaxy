"""
test_gemini_key.py
------------------
單一用途：確認 GEMINI_API_KEY 有沒有被正確讀到、以及這把 Key 能不能實際呼叫 Gemini API。

用法：
    python test_gemini_key.py

把這個檔案放在跟 .env 同一層資料夾（例如放進 Galaxy-feature-brand-new-base/ 底下）再執行，
或是用第 2 種方式：直接把 GEMINI_API_KEY 設成系統環境變數後執行，也可以不靠 .env。
"""

import os
import sys
from pathlib import Path

# ------------------------------------------------------------------
# 1. 找 .env：明確指定「這個檔案所在的資料夾」，不要依賴目前終端機的所在路徑。
#    這是最常見的地雷：如果你在別的資料夾下執行 python，
#    load_dotenv() 預設只會往「目前工作目錄」找，不一定找得到你放在專案資料夾裡的 .env。
# ------------------------------------------------------------------
try:
    from dotenv import load_dotenv
except ImportError:
    print("❌ 尚未安裝 python-dotenv，先執行: pip install python-dotenv")
    sys.exit(1)

ENV_PATH = Path(__file__).resolve().parent / ".env"
loaded = load_dotenv(dotenv_path=ENV_PATH)

print(f"[1] 嘗試載入 .env 路徑: {ENV_PATH}")
print(f"    檔案存在嗎？ {ENV_PATH.exists()}")
print(f"    load_dotenv() 回傳: {loaded}  (True 代表有找到並讀取這個檔案)")

api_key = os.environ.get("GEMINI_API_KEY", "")

if not api_key:
    print("\n❌ 目前讀不到 GEMINI_API_KEY。")
    print("   可能原因：")
    print("   1) .env 檔案不在上面印出的路徑")
    print("   2) .env 裡的變數名稱打錯（要完全是 GEMINI_API_KEY=xxxx，等號兩邊不要有空白，不要加引號也可以）")
    print("   3) 這台機器/這個部署環境本來就沒有把 .env 帶進來（很多雲端平台預設不會上傳 .env，因為它被 .gitignore 排除）")
    sys.exit(1)

masked = api_key[:4] + "..." + api_key[-4:] if len(api_key) > 8 else "(太短，可能貼錯了)"
print(f"\n✅ 讀到 GEMINI_API_KEY: {masked}（長度 {len(api_key)}）")

# 支援用逗號分隔多把 key 輪播（跟 rag_engine.py 的邏輯一致），這裡全部都測過一輪
keys = [k.strip() for k in api_key.split(",") if k.strip()]
print(f"    偵測到 {len(keys)} 把 Key（以逗號分隔）\n")

# ------------------------------------------------------------------
# 2. 實際打 API，確認 Key 有效，同時列出這把 Key 能用的 model 清單。
#    這一步也能順便告訴你「哪些 model 名稱現在還能用」，
#    因為 text-embedding-004 跟部分 gemini-2.0-flash 端點在 2026 上半年陸續被 Google 關閉了。
# ------------------------------------------------------------------
try:
    from google import genai
except ImportError:
    print("❌ 尚未安裝 google-genai，先執行: pip install -U google-genai")
    sys.exit(1)

for i, key in enumerate(keys, start=1):
    print(f"--- 測試第 {i} 把 Key ---")
    client = genai.Client(api_key=key)

    # 2a. 列出可用 model（最準：能列出來就代表 Key 本身有效）
    try:
        models = list(client.models.list())
        model_names = [m.name for m in models]
        print(f"  ✅ Key 有效，可存取 {len(model_names)} 個 model")
        flash_like = [n for n in model_names if "flash" in n and "embed" not in n]
        embed_like = [n for n in model_names if "embed" in n]
        print(f"     可用的文字生成 model（節錄）: {flash_like[:5]}")
        print(f"     可用的 embedding model（節錄）: {embed_like[:5]}")
    except Exception as e:
        print(f"  ❌ 這把 Key 呼叫 ListModels 失敗: {e}")
        continue

    # 2b. 實際打一次文字生成，用「別名」模型，避免寫死已下架的版本號
    try:
        resp = client.models.generate_content(
            model="gemini-flash-latest",
            contents="請用不超過 10 個字回覆：你在嗎？",
        )
        print(f"  ✅ 文字生成測試成功: {resp.text.strip()}")
    except Exception as e:
        print(f"  ❌ 文字生成測試失敗: {e}")

    # 2c. 實際打一次 embedding，用新的 embedding model
    try:
        # ✅ 修改後的正確寫法
        embed_resp = client.models.embed_content(
            model="gemini-embedding-001",
            contents="測試向量化",
            config={"output_dimensionality": 768},
        )
        vec_len = len(embed_resp.embeddings[0].values)
        print(f"  ✅ Embedding 測試成功，向量長度 = {vec_len}")
    except Exception as e:
        print(f"  ❌ Embedding 測試失敗: {e}")

    print()

print("測試結束。若上面每一步都是 ✅，代表 Key 本身沒問題，")
print("那你專案裡原本 404 NOT_FOUND 的錯誤，根源是『model 名稱過期』，不是 Key 或 .env 的問題。")