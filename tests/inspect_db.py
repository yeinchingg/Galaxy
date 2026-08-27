"""
tests/inspect_db.py

檢查 astro_platform.db 目前實際存了什麼資料的小工具。
不是 pytest 測試（檔名不是 test_ 開頭，pytest 掃描時會自動略過），
是給人手動執行、快速確認「後台到底有沒有資料」用的。

用法：
    # 印出所有資料表的筆數 + 每個表最近幾筆資料
    python tests/inspect_db.py

    # 只看某一個資料表
    python tests/inspect_db.py --table messages

    # 調整每個表要顯示幾筆（預設 10）
    python tests/inspect_db.py --limit 20

    # 資料庫路徑不是預設位置時
    python tests/inspect_db.py --db path/to/astro_platform.db
"""

import argparse
import sqlite3
from pathlib import Path

DEFAULT_DB_PATH = Path(__file__).resolve().parent.parent / "astro_platform.db"

# 每個表要用哪個欄位排序才能看到「最近」的資料（沒特別排序欄位的用 rowid）
ORDER_BY_HINTS = {
    "users": "user_id DESC",
    "sessions": "created_at DESC",
    "messages": "id DESC",
    "interactions": "ts DESC",
    "quiz_scores": "completed_at DESC",
}


def get_tables(conn: sqlite3.Connection) -> list[str]:
    rows = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name != 'sqlite_sequence'"
    ).fetchall()
    return [r[0] for r in rows]


def inspect_table(conn: sqlite3.Connection, table: str, limit: int):
    count = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
    print(f"\n--- {table} (共 {count} 筆) ---")

    if count == 0:
        print("  (空的，沒有任何資料)")
        return

    order_by = ORDER_BY_HINTS.get(table, "rowid DESC")
    try:
        rows = conn.execute(f"SELECT * FROM {table} ORDER BY {order_by} LIMIT ?", (limit,)).fetchall()
    except sqlite3.OperationalError:
        # 排序欄位不存在時退回不排序
        rows = conn.execute(f"SELECT * FROM {table} LIMIT ?", (limit,)).fetchall()

    col_names = [d[0] for d in conn.execute(f"SELECT * FROM {table} LIMIT 1").description]
    print("  欄位:", ", ".join(col_names))
    for row in rows:
        print(" ", dict(row))

    if count > limit:
        print(f"  ...(還有 {count - limit} 筆未顯示，用 --limit 調整顯示筆數)")


def main():
    parser = argparse.ArgumentParser(description="檢查 astro_platform.db 目前的資料")
    parser.add_argument("--db", type=str, default=str(DEFAULT_DB_PATH), help="資料庫檔案路徑")
    parser.add_argument("--table", type=str, default=None, help="只看指定的資料表")
    parser.add_argument("--limit", type=int, default=10, help="每個表最多顯示幾筆（預設 10）")
    args = parser.parse_args()

    db_path = Path(args.db)
    if not db_path.exists():
        print(f"❌ 找不到資料庫檔案: {db_path}")
        return

    print(f"檢查資料庫: {db_path}\n")

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row

    try:
        tables = get_tables(conn)
        if not tables:
            print("這個資料庫裡沒有任何資料表。")
            return

        if args.table:
            if args.table not in tables:
                print(f"❌ 找不到資料表 '{args.table}'，目前有的表: {', '.join(tables)}")
                return
            inspect_table(conn, args.table, args.limit)
        else:
            print(f"共 {len(tables)} 個資料表: {', '.join(tables)}")
            for t in tables:
                inspect_table(conn, t, args.limit)
    finally:
        conn.close()


if __name__ == "__main__":
    main()