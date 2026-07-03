#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""不依赖 Claude 的 Notion 同步：用 Notion 官方 API token 把 graph.json 的工作记录写进 Notion 数据库。
仅用标准库（urllib），任何机器/任何人都能跑。

准备：
  1) 到 https://www.notion.so/my-integrations 建 integration，拿 token（secret_xxx / ntn_xxx）。
  2) 打开目标数据库页面 → ··· → Connections → 接入该 integration。
  3) export NOTION_TOKEN=...   然后 python3 to_notion.py --database <数据库ID>

注意：本脚本是「追加创建」记录（适合写入空库或增量）。它不会改动/删除已有页面。
数据库 ID 用 --database 传入，或填到下面的 DEFAULT_DB。
"""
import json, os, sys, time, argparse, urllib.request, urllib.error

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_DB = ""   # 你的 Notion 数据库 ID（建库后填入；也可用 --database 传入）
API = "https://api.notion.com/v1/pages"
VER = "2022-06-28"

def create_page(token, db, props):
    body = json.dumps({"parent": {"database_id": db}, "properties": props}).encode()
    req = urllib.request.Request(API, data=body, method="POST", headers={
        "Authorization": f"Bearer {token}", "Notion-Version": VER,
        "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.status

def entry_props(e):
    p = {
        "Record": {"title": [{"text": {"content": (f"{e.get('date') or '—'} · {e['label']}")[:100]}}]},
        "Project": {"select": {"name": e.get("project") or "—"}},
        "Machine": {"select": {"name": e.get("machine") or "—"}},
        "Status": {"select": {"name": e.get("status") or "logged"}},
        "Weight": {"number": e.get("weight", 0)},
        "Source": {"rich_text": [{"text": {"content": (e.get("source") or "")[:1900]}}]},
    }
    if e.get("date"):
        p["Date"] = {"date": {"start": e["date"]}}
    if e.get("agent"):
        p["Agent"] = {"select": {"name": e["agent"]}}
    return p

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--database", default=DEFAULT_DB)
    ap.add_argument("--graph", default=os.path.join(HERE, "graph.json"))
    a = ap.parse_args()
    token = os.environ.get("NOTION_TOKEN")
    if not token:
        sys.exit("请先 export NOTION_TOKEN=...（见文件头说明）")
    if not a.database:
        sys.exit("请用 --database <数据库ID> 指定 Notion 数据库（或在文件里设 DEFAULT_DB）")
    entries = [n for n in json.load(open(a.graph, encoding="utf-8"))["nodes"] if n["type"] == "entry"]
    print(f"将写入 {len(entries)} 条工作记录到数据库 {a.database}")
    ok = err = 0
    for i, e in enumerate(entries, 1):
        try:
            create_page(token, a.database, entry_props(e))
            ok += 1
        except urllib.error.HTTPError as ex:
            err += 1
            print(f"  ! 第{i}条失败 {ex.code}: {ex.read()[:200]}", file=sys.stderr)
        time.sleep(0.34)        # Notion 限速 ~3 req/s
        if i % 20 == 0:
            print(f"  …{i}/{len(entries)}")
    print(f"✓ 完成：成功 {ok}，失败 {err}")

if __name__ == "__main__":
    main()
