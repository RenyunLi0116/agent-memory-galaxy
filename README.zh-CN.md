# Agent Memory Galaxy

[English](README.md) | [中文](README.zh-CN.md)

让你的 agents 一起记住工作，并保持私有。

Agent Memory Galaxy 会把分散在多台机器和多种 AI agent 工具中的工作痕迹汇成一个私有、可检查、可搜索的记忆图谱。它采集已审阅的 `agent_memory.md`、可选的安全会话元数据、机器 fragments 和在线 presence，生成 `graph.json`，并用静态 Galaxy Viewer 展示。

这个 public repo 是可复用框架、skill 包和公开宣传/demo 站点。真实 fragments、presence、明文图谱和本地 viewer 应放在私有 fork、私有 hub 或本地 checkout。

## 作为 Claude Code Plugin/Skill 安装

在 Claude Code 中分两条消息运行：

```text
/plugin marketplace add https://github.com/RenyunLi0116/agent-memory-galaxy
```

然后运行：

```text
/plugin install agent-memory-galaxy@agent-memory-galaxy
```

安装后用自然语言调用 skill，例如：“Use Agent Memory Galaxy to create a private hub” 或“Use Agent Memory Galaxy to review this repo before public release”。plugin 安装的是指导流程；运行脚本仍需要 repo checkout。

## 选择一条路径

### A. 公开宣传页与合成 demo

这条路径不会扫描你的机器，只会重建 `docs/demo/` 下的虚构 demo 数据。

```bash
git clone https://github.com/RenyunLi0116/agent-memory-galaxy.git
cd agent-memory-galaxy
python3 scripts/build-public-demo.py
python3 scripts/build-landing-concepts.py
python3 -m http.server 8765 --directory docs
```

打开 `http://127.0.0.1:8765/` 查看宣传页，打开 `http://127.0.0.1:8765/demo/?lang=zh` 查看中文合成 demo。demo 图谱是虚构、脱敏、可公开发布的。

### B. 单机私有预览

这条路径扫描一个明确指定的项目目录，并生成本地明文 viewer。不要从 `$HOME`、`/` 或整个 workspace 开始。

```bash
git clone https://github.com/RenyunLi0116/agent-memory-galaxy.git
cd agent-memory-galaxy
./scripts/build-private-preview.py --machine laptop-a --tool codex --roots ~/projects/my-app
```

本地打开 `standalone.html`。它包含明文记忆数据，已被 gitignore。

### C. 多机器私有 Hub

真实协作应使用私有仓库或私有 fork。

```bash
git clone https://github.com/RenyunLi0116/agent-memory-galaxy.git my-memory-hub
cd my-memory-hub
git remote set-url origin git@github.com:<your-user-or-org>/<private-hub>.git
```

每台贡献机器在私有 hub checkout 中运行，并传入窄范围项目根目录：

```bash
AMG_PRIVATE_HUB=1 ./contribute.sh workstation-a codex ~/projects/my-app
```

聚合机器运行：

```bash
./update.sh
```

如果你在私有 hub 中明确希望 Git 跟踪 private fragments、presence 或加密 Pages blob，使用：

```bash
AMG_TRACK_PRIVATE=1 ./update.sh
```

## 它做什么

```text
已审阅笔记        安全会话元数据        贡献机器 fragments       在线 presence
agent_memory.md   Claude/Codex/Cursor   fragments/*.json        presence/*.json
        \                  |                    |                     /
         \                 |                    |                    /
          collect.py + distill.py + merge fragments + presence injection
                                      |
                                  graph.json
                                      |
                本地 standalone viewer 或可选加密 Pages viewer
```

核心文件：

- `collect.py` 扫描本地/远端 sources，并归一化为 `graph.json`。
- `distill.py` 从 agent 原生会话元数据中补全结构化事实，不复制原始对话。
- `fragments/*.json` 允许多台机器向同一个私有 hub 贡献。
- `presence/*.json` 让 viewer 显示当前活跃 agent。
- `viewer/index.html` 是运行时 Galaxy Viewer。
- `docs/index.html` 是公开宣传页，支持 `?lang=en` / `?lang=zh`。
- `docs/demo/` 是完全合成的公开 demo，支持中英文 UI 与节点内容。
- `docs/galaxy/` 预留给可选的加密 viewer shell。

## GitHub Pages URL 策略

公开站点地址：

```text
https://renyunli0116.github.io/agent-memory-galaxy/
```

| URL/path | 用途 | 数据策略 |
|---|---|---|
| `/agent-memory-galaxy/` | 公开宣传页 | 没有真实数据 |
| `/agent-memory-galaxy/?lang=zh` | 中文宣传页 | 没有真实数据 |
| `/agent-memory-galaxy/demo/?lang=zh` | 中文合成交互 demo | 仅虚构图谱 |
| `/agent-memory-galaxy/demo/?lang=en` | 英文合成交互 demo | 仅虚构图谱 |
| `/agent-memory-galaxy/concepts/` | 设计探索存档 | 公开、次级页面 |
| `/agent-memory-galaxy/galaxy/` | 可选加密 viewer shell | 公开可访问 shell，不含明文图谱 |
| `/agent-memory-galaxy/galaxy/graph.enc.json` | 可选加密图谱 blob | 仅密文 |
| `standalone.html` | 本地明文 viewer | 仅本地，已 gitignore |
| private hub/fork | 真实 fragments、presence、graph | 私有仓库/本地机器 |

启用 Pages：`Settings -> Pages -> Build and deployment -> Source -> GitHub Actions`。仓库中的 `.github/workflows/pages.yml` 会在每次 push 到 `main` 时发布静态 `docs/` 站点。

GitHub Pages 不是访问控制层。`/galaxy/` 是公开 shell；隐私依赖强客户端加密和对明文产物的私有处理。

## 隐私模型

Agent Memory Galaxy 是 privacy-first，不是 privacy-magic。

公开发布规则：

- public repo：框架代码、文档、skill 包、合成 demo 数据。
- private repo/fork：真实 `fragments/*.json`、`presence/*.json`、`graph.json`、`standalone.html`。
- 可选加密 Pages viewer：`docs/galaxy/index.html` 加 `docs/galaxy/graph.enc.json`，绝不发布明文 `graph.json`。

不要把 secrets、credentials、private keys、未经审阅的敏感代码或原始机密对话写进 memory 文件。会话提炼只应抽取结构化元数据，但发布前仍应审阅配置和生成产物。客户端加密能降低暴露，但公开密文仍可被下载并离线攻击。

## 可选加密 Pages Viewer

在私有 hub 中创建两个强密码文件：

```bash
printf '%s' 'first-strong-passphrase' > .amg_password
printf '%s' 'second-strong-passphrase' > .amg_password2
chmod 600 .amg_password .amg_password2
AMG_TRACK_PRIVATE=1 ./update.sh
```

可发布输出：

```text
docs/galaxy/index.html
docs/galaxy/graph.enc.json
```

不要发布明文 `graph.json`。

## Contributor 与 Aggregator

- Contributor machine：运行 `AMG_PRIVATE_HUB=1 ./contribute.sh <machine> <claude|codex|cursor|human> <project-root>`，写入私有 fragment 并推到私有 hub。
- Aggregator machine：运行 `./update.sh` 或 `./update.sh --pull`，合并 fragments，注入 presence，可选加密 Pages，并重建本地 standalone viewer。

Contributors 不需要加密密码，也不应修改 `docs/galaxy/`。

## 数据模型

节点包括 `project`、`entry`、`fact`、`agent`、`liveagent`、`machine`、`dataset`、`server`、`model`、`method`、`file`、`wandb`、`tech`、`notion`、`boundary`、`artifact`。

边包括 `in`、`did`、`located`、`uses`、`touches`、`trains`、`tracks`、`syncs`、`explores`、`references`、`depends_on`、`inherits_from`、`exports_to`、`working_on`、`handoff_to`、`shared_on`、`cached_on`、`redacts`、`encrypts`、`publishes`、`keeps_private`、`validates`、`serves`、`replicates_to`、`link`、`on`。

共享实体会自动连接跨机器项目。例如两个 agent 触碰同一数据集、文件、模型或 Notion 页面，它们会在图谱中相连。

## 需求

- Python 3.8+：采集、提炼、demo 生成和 artifact 构建。
- Git：多机器同步。
- `cryptography`：只有启用 `encrypt.py` 加密 Pages 发布时才需要。
- 无需前端构建步骤；viewer 是静态 HTML/CSS/JS。

## License

MIT.
