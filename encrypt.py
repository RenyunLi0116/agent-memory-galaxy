#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把完整 graph.json 用密码加密成 docs/galaxy/graph.enc.json（供公开 Pages 发布）。
方案：PBKDF2-HMAC-SHA256(600k) 派生密钥 + AES-256-GCM，与浏览器 Web Crypto 解密完全兼容。
公网只发密文，谁都下载不到明文；只有持密码者在浏览器本地解密查看。

双密码方案：需 pw1 与 pw2 都正确才能解密。
  combined = pw1 + "\\x00" + pw2（NUL 分隔，typed 密码不含 NUL）
  key = PBKDF2-HMAC-SHA256(combined_utf8, salt, 200000, 32B) → AES-256-GCM
任一密码错 → 派生 key 不同 → GCM 认证失败 → 解不开。查看器与此逐字节一致。

密码来源（都不进 git、不进对话）：
  pw1：本机受保护文件 .amg_password（供 cron 无人值守；务必 chmod 600、已 gitignore）
  pw2：本机受保护文件 .amg_password2（同上，用户自己写）
  任一文件缺失 → 交互式 getpass 分别提示（不回显）。
密码绝不写入 git、绝不打印。

依赖：cryptography（pip install cryptography）。换机迁移见 PORTABILITY.md。
"""
import json, os, sys, base64, getpass, secrets
from hashlib import pbkdf2_hmac
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

HERE = os.path.dirname(os.path.abspath(__file__))
ITER = 600_000   # PBKDF2 迭代次数（OWASP 2023+ 建议 ≥600k）
SEP = "\x00"   # 合并两密码的分隔符（NUL；查看器用 "\u0000" 与此一致）

def main():
    src = os.path.join(HERE, "graph.json")
    out = os.path.join(HERE, "docs", "galaxy", "graph.enc.json")
    if not os.path.exists(src):
        sys.exit("找不到 graph.json，请先跑 python3 collect.py")

    pw1file = os.path.join(HERE, ".amg_password")
    pw2file = os.path.join(HERE, ".amg_password2")
    if os.path.exists(pw1file):
        pw1 = open(pw1file, encoding="utf-8").read().strip()
        print("· 用本机 .amg_password 中的密码 1 加密")
    else:
        pw1 = getpass.getpass("设置/输入加密密码 1（建议 ≥16 位或一句话）: ")
        if len(pw1) < 8:
            sys.exit("密码 1 太短，至少 8 位（强烈建议 ≥16）。")
    if os.path.exists(pw2file):
        pw2 = open(pw2file, encoding="utf-8").read().strip()
        print("· 用本机 .amg_password2 中的密码 2 加密")
    else:
        pw2 = getpass.getpass("设置/输入加密密码 2（建议 ≥16 位或一句话）: ")
        if len(pw2) < 8:
            sys.exit("密码 2 太短，至少 8 位（强烈建议 ≥16）。")
    if not pw1 or not pw2:
        sys.exit("两个密码都不能为空。")
    if SEP in pw1 or SEP in pw2:
        sys.exit("密码不得包含 NUL 字符。")

    combined = pw1 + SEP + pw2                 # 用 NUL 分隔；与查看器 p1 + SEP + p2 (SEP=\u0000) 逐字节一致
    data = open(src, "rb").read()
    salt = secrets.token_bytes(16)
    iv = secrets.token_bytes(12)
    key = pbkdf2_hmac("sha256", combined.encode("utf-8"), salt, ITER, dklen=32)
    ct = AESGCM(key).encrypt(iv, data, None)   # 返回 密文||16字节tag，与 Web Crypto 一致
    blob = {
        "v": 2, "alg": "AES-GCM", "kdf": "PBKDF2-SHA256", "iter": ITER, "dual": True,
        "salt": base64.b64encode(salt).decode(),
        "iv": base64.b64encode(iv).decode(),
        "ct": base64.b64encode(ct).decode(),
    }
    os.makedirs(os.path.dirname(out), exist_ok=True)
    json.dump(blob, open(out, "w"), separators=(",", ":"))
    print(f"✓ 写出 {out}（明文 {len(data)} B → 密文 {len(ct)} B，双密码 v2）")
    print("  docs/galaxy/ 将只含 viewer + 密文。明文 graph.json / standalone.html 不入库。")

if __name__ == "__main__":
    main()
