#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把 docs/index.html 的 <body> 内容 + 内联 graph.json 打包成一个自包含、无外链的页面，
用于发布 Artifact 或离线单文件分享（双击即可看，无需本地服务器）。"""
import json, re, os, sys, argparse

HERE = os.path.dirname(os.path.abspath(__file__))

def build(out_path, standalone=False):
    html = open(os.path.join(HERE, "docs", "index.html"), encoding="utf-8").read()
    data = open(os.path.join(HERE, "graph.json"), encoding="utf-8").read()
    data = data.replace("</", "<\\/")               # 防止 JSON 里的 </script> 截断脚本
    body = re.search(r"<body>(.*)</body>", html, re.S).group(1)
    inject = f'<script>window.GRAPH={data};</script>\n'
    if standalone:
        # 完整可双击打开的单文件 HTML
        head = re.search(r"<head>(.*?)</head>", html, re.S).group(1)
        page = (f"<!doctype html>\n<html lang=\"zh-CN\">\n<head>{head}</head>\n"
                f"<body>\n{inject}{body}\n</body>\n</html>\n")
    else:
        # Artifact 片段：无 doctype/html/head/body（发布时由平台包裹）
        page = ('<title>CyberMemory · 知识图谱</title>\n'
                '<meta name="description" content="多机多项目 agent 工作记录的交互式知识图谱">\n'
                + inject + body)
    open(out_path, "w", encoding="utf-8").write(page)
    print(f"✓ {out_path}  ({os.path.getsize(out_path)} bytes)")

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--standalone", action="store_true", help="产出完整可双击的 HTML（否则产出 Artifact 片段）")
    a = ap.parse_args()
    build(a.out, a.standalone)
