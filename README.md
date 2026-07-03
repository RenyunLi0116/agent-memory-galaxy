# 🧠 CyberMemory

> 把分散在多台机器、两套格式里的 **agent 工作记录** 汇聚成一张可交互的 **3D 知识图谱银河** 🌌 · Turn scattered, multi-machine **agent work logs** into one interactive **3D knowledge-graph galaxy**.

CyberMemory 把团队里各台机器、各个 agent（Claude / Codex / Cursor / 人）的工作记忆（`agent_memory.md` + Claude 自动记忆 `.claude/projects/*/memory/`）解析成一张规范的 `graph.json`（唯一真相），再渲染成可交互银河、导出 Notion；连"没人写记录"的缺口，也能靠**提炼原生会话**补上。所有明文只留在**私有仓库**，如需在线共享可选**客户端加密**发布。✨

---

## 🏗️ 架构（解耦三层）

```
来源(多机)              采集              规范中间层            增强(定期)           发布
本地手工记忆 ─┐                                                                  ┌─► 🌌 自包含 HTML 银河图
本地自动记忆 ─┤     collect.py         graph.json           定时增强             │   (力导向·过滤·时间轴·详情)
server(ssh)  ─┼─► (解析两种格式) ─► (节点+边, 唯一真相) ─► 去重合并实体 ─────────┤
其他机/NAS   ─┤     + distill.py         (随数据增长)         + 启发式分型         ├─► 🔐 (可选)加密 Pages
原生会话     ─┘     (Claude/Codex/Cursor)                                        └─► 🗂️ (可选)Notion 关系库
```

**核心思路** 💡：所有记忆先抽成规范的 `graph.json`（唯一真相）；前接多来源解析器，后接多种渲染输出——换/加平台只是换输出，主体不动。零外部依赖（采集/提炼仅用 Python 标准库，含 sqlite3）。

## 📁 目录

| 文件 | 作用 |
|---|---|
| `collect.py` | 🧲 采集器：扫描来源 → 解析 → 产出 `graph.json`（零依赖，仅标准库） |
| `distill.py` | ✨ 从 **Claude/Codex/Cursor 原生会话**提炼**派生**记忆补缺口（只抽结构化字段·仅补缺口·`derived` 次级） |
| `sources.json` | ⚙️ 数据来源配置（本地 / 各 server）。**加新 server 只改这里** |
| `projects.json` | 🔗 (可选) 跨机项目归并 + 团队自定义实体规则 |
| `encrypt.py` | 🔐 双密码 **AES-256-GCM**（PBKDF2-SHA256）→ `docs/graph.enc.json`（仅在线发布时用） |
| `docs/index.html` | 🌌 银河查看器（单文件、零依赖；浏览器本地解密） |
| `build_artifact.py` | 🛠️ 把查看器 + 数据打包成自包含单文件页（`standalone.html`） |
| `contribute.sh` | 📤 贡献端一键：采集 + 提炼 + 推送 |
| `update.sh` | 🔄 汇总端一键：拉取 + 合并 + (加密) + 发布 |
| `heartbeat.sh` | 💓 agent 报到/心跳，支持准实时协作（红光在线） |
| `pull_remote.sh` | 📡 基站模式：汇总端主动 ssh 到各 server 远程采集并取回 |
| `to_notion.py` | 🗂️ (可选) 导出到 Notion（用官方 API token） |
| `graph.json` | 📊 生成的图数据（明文，已 gitignore、只留本地） |

## 🚀 快速开始

```bash
# 1) 采集本机记忆 → graph.json（默认读 sources.json 里 enabled 的本地源）
python3 collect.py
#    也可直接指定要扫的目录（贡献端常用）：
python3 collect.py --local-only --machine <本机唯一名> --tool claude --roots "$HOME"

# 2) 生成可双击的单文件银河图
python3 build_artifact.py --out standalone.html --standalone

# 3) 查看：浏览器打开 standalone.html（含完整明文，仅本地）
```

多机协作时用两个角色（详见 `ONBOARDING.md`）：
- **贡献端**（各台机）：`./contribute.sh <本机唯一名> <claude|codex|human>` → 采集+提炼+推送碎片。**不加密、不碰 `docs/`、不需要密码。**
- **汇总端**（主力机）：`./update.sh [--pull]` → 拉回各机碎片 + 合并 + （可选加密）+ 发布。

## 🔒 隐私 / 发布方式

- **完整明文只留本地** 🏠：`graph.json`、`standalone.html`（含路径/正文）均已 gitignore，绝不入库。
- **碎片是明文，只存私有仓库** 📦：`fragments/*.json`、`presence/*.json` 仅存在于**私有**仓库；不要放进 `docs/`。
- **默认全私有**：仓库设为 private，团队本地看 `standalone.html`。**无需**加密、无需 Pages。
- **可选：加密后在线共享** 🔐：若要团队在线访问，`encrypt.py` 用**两个**密码派生密钥 **AES-256-GCM**（PBKDF2-SHA256）加密成 `docs/graph.enc.json`，只发密文，访问者在浏览器本地输两个密码解密（任一错→进不去）。两个密码分放 `.amg_password` / `.amg_password2`（都 gitignore、`chmod 600`）。这样连公开托管都安全（只放密文+查看器）。可迁移性见 `PORTABILITY.md`。

## 🧬 数据模型

- **节点**：`project` · `entry`（一条=一个 `## ` 分节）· `fact`（自动记忆）· `agent` · `liveagent`（🔴 正在工作）· `machine` · `dataset` · `server` · `model` · `method` · `file` · `wandb` · `tech` · `notion`；`distill.py` 产出的 entry 带 `derived` 标记（更黯淡、可筛）。
- **边**：`in`（属于项目）· `did`（agent 做）· `located`（在某机）· `uses/touches/trains/tracks/syncs`（触及实体）· `explores` · `references`（项目→项目）· `working_on`（live agent→项目）· `link`（`[[双链]]`）· `on`。
- 跨文件共享实体（同一数据集 / server / 文件 / Notion 页）自动把不同项目连成一张网。
- **自定义实体**：团队专有的数据集/模型名等可在 `projects.json` 的 `entity_patterns` 里加正则，采集时自动识别成节点（内置只保留通用规则：IP、ViT、wandb、思路N）。

## ✨ 让"以后的工作"进图：维护 `agent_memory.md`

每次有意义改动后，在项目根 `agent_memory.md` 追加一节：

```markdown
## 2026-07-03 —— 简短标题 (claude)
- 改了什么：…
- 为什么：…
- 状态：doing | done
- 验证：…
- 涉及文件：a.py, b.py
```

采集器读的就是它（纯 markdown、跨 agent 通用）。即便某项目忘了写，`distill.py` 也会从原生会话**只抽结构化字段**（标题/日期/编辑文件/工具，**绝不进对话正文/代码/密钥**）兜底补进图。

## 🤖 让新机的 agent 自助接入（把下面 prompt 复制给它）

```text
你在一台新机器上。任务：把这台机器的 agent 工作记忆接入 "CyberMemory"
（一个把多机 agent 记忆汇聚成知识图谱、发布到私有仓库的中枢）。
你的角色是【贡献端】：只采集本机记忆并 git 推送，不加密、不碰 docs/、不需要密码，
绝不运行 update.sh / encrypt.py（那是汇总端主力机的事）。

按顺序：
1) cd 进 CyberMemory 目录（没有就 git clone git@github.com:CyberOrigin2077/CyberMemory.git）。
2) 读 AGENTS.md(Codex)/CLAUDE.md(Claude) + ONBOARDING.md，理解贡献端流程。
3) 确认能 push：git remote -v && git ls-remote origin >/dev/null && echo OK
4) 给这台机起个【唯一】名字，运行：
     ./contribute.sh <本机唯一名> <claude|codex|human>
   它会采集本机 agent_memory.md + Claude memory/、从原生会话提炼缺口、生成
   fragments/<名>.json(+ -distilled.json) 并 git 提交推送。
5) 报告：推了多少节点、提炼几条派生记忆、有无报错。
红线：私有仓库；碎片是明文只存私有仓；别开 Pages、别把明文放进 docs/、别动加密口令。
```

---

<sub>🤖 用 agent 构建，服务于 agent。 · Built with agents, for agents.</sub>
