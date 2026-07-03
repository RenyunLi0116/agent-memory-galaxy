# 可迁移性 / 交接说明 (PORTABILITY)

CyberMemory 刻意做到**不绑定任何特定 AI 账号、不绑定本机**。换机器、换 AI 助手、甚至纯手动，都能接手。

## 核心原则
整套东西就是一个 **git 仓库里的纯文件**：
- `collect.py` —— 采集器，**只用 Python 标准库**，任何 Python ≥3.8 都能跑。
- `distill.py` —— 原生会话提炼，标准库（含 sqlite3）。
- `build_artifact.py` —— 打包单文件查看器，标准库。
- `docs/index.html` —— 查看器，**纯静态、零外部依赖（无 CDN）**，任何浏览器/静态托管都能开。
- `update.sh` / `contribute.sh` / `heartbeat.sh` / `pull_remote.sh` —— 一键流水线。
- `encrypt.py` —— （可选，仅加密在线发布时用）依赖 `cryptography`（`pip install cryptography`）。
- `to_notion.py` —— （可选）不依赖任何 AI 的 Notion 同步（用 Notion 官方 API token）。

**没有任何一步必须由某个特定 AI 来做。** 任何 AI 助手或人都能照本文件接手。

## 换一台新机器（当汇总端）
```bash
git clone git@github.com:CyberOrigin2077/CyberMemory.git
cd CyberMemory
# （可选）按本机情况改 sources.json 里的本地路径 / server
./update.sh                              # 采集→合并→重建本地 standalone.html→提交→推送
#   ./update.sh --pull                   # 连同 ssh 拉取/基站远程采集
```
看图：浏览器打开本地 `standalone.html`（含完整明文，仅私有）。

### 如需团队加密在线共享（可选）
```bash
pip install cryptography                 # encrypt.py 唯一外部依赖
# 双密码：两个文件都要设，都 chmod 600、都不入库；解密时两个都对才行
printf '你的强密码一' > .amg_password  && chmod 600 .amg_password    # 在自己终端做，别让密码进聊天/历史
printf '你的强密码二' > .amg_password2 && chmod 600 .amg_password2
python3 encrypt.py                       # 生成 docs/graph.enc.json（只发密文）
```
访问加密页面需输入**两个**密码，都对才在浏览器本地解密（Web Crypto）。用**强密码**（密文可下载，唯一攻击是离线暴力破解）。这样连**公开托管**都安全（只放密文 + 查看器）。

## 换一个 AI 助手
把本仓库 + `README.md` + 本文件丢给任何 AI 即可。关键事实：
- 数据模型见 `README.md`「数据模型」。
- 采集：`python3 collect.py [--pull]` → `graph.json`（完整，本地）。
- （可选）公开：`python3 encrypt.py` → `docs/graph.enc.json`（密文）。`encrypt.py` 读**两个**本地密码文件，密钥由两个密码共同派生，访问时两个都对才解密。
- 别把明文 `graph.json` / `standalone.html` 入库（已 gitignore）。

## 各部件归属（都与特定 AI 无关）
| 部件 | 在哪 | 谁拥有 |
|---|---|---|
| 代码 + (可选)密文图 | git 仓库 | 你们的 GitHub 组织 `CyberOrigin2077` |
| 银河展示（本地） | `standalone.html` | 本机文件 |
| 银河展示（可选在线） | GitHub Pages / 内网静态托管 | 你们托管 |
| Notion 镜像（可选） | Notion 工作区 | 你们的 Notion 账号 |
| 加密密码（两个，可选） | 本机 `.amg_password` + `.amg_password2` | 只在汇总端 |

## Notion：脱离特定 AI 后怎么办（可选）
- **已建好的 Notion 页/库不会消失**：它们在你们 Notion 账号下，照常访问、编辑。
- **想继续自动同步**：用 `to_notion.py`
  ```bash
  # 1. 在 notion.so/my-integrations 建一个 integration，拿到 token
  # 2. 把目标数据库 share 给该 integration
  export NOTION_TOKEN=<你的 token>
  python3 to_notion.py --database <数据库ID>
  ```
  任何机器/任何人都能刷新 Notion，完全不依赖 AI。

## 每周自动刷新（cron）
汇总端用系统 crontab 跑 `update.sh --pull`：
```
7 9 * * 1 cd /路径/CyberMemory && ./update.sh --pull >> cron.log 2>&1
```
（若启用加密在线，需该机已配两个密码文件与 ssh 免密。）

## 丢了密码（仅加密在线场景）
没事，数据没丢（明文在各机 `graph.json` / 记忆文件里）。双密码解密需**两个都对**；重设时把两个文件都重写后重新 `encrypt.py` 即可，旧密文作废、换成新双密码的。两个文件都 `chmod 600`、都不入库（已 gitignore）。
