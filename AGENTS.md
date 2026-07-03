# AGENTS.md — 给在本仓库工作的 agent（Codex / 任意 agent）

> 你正在一台机器上、在 **CyberMemory** 同步中枢仓库里。本文件告诉你**怎么把这台机器的 agent 工作记忆同步进总图**。Claude 看同目录 `CLAUDE.md`，内容一致。完整说明见 `ONBOARDING.md`。

## 这台机器要做的事（一条命令）

把本机的 agent 记忆采集成"碎片"并推送到共享私有仓库：

```bash
./contribute.sh <本机唯一名> <工具> [扫描根目录]
# 例（Codex 机器）:   ./contribute.sh mac-codex   codex
# 例（Claude 机器）:  ./contribute.sh lab-pc      claude
# 例（指定目录）:     ./contribute.sh work-pc     codex   /home/me/projects
```
- `<本机唯一名>`：给这台机起个**唯一**名字，别和别的机重名。
- `<工具>`：写 `codex` / `claude` / `human`，用于在图里区分"这条记录是哪个 agent 产出的"。
- 默认扫描 `$HOME`；家目录太大就指定具体项目目录。

它会：① 采集本机 `agent_memory.md`(及 `.claude/projects/*/memory/` 若有) → `fragments/<本机名>.json`；② **自动提炼原生会话**（见下）→ `fragments/<本机名>-distilled.json`；③ `git add/commit/push`。
**汇总端**（主力机）下次跑 `update.sh` 会自动 `git pull` 取回、合并（两个碎片都吃）、（可选）加密、更新发布。你**不需要**加密、不需要碰 `docs/`、不需要密码。

### 前置条件
- `python3`（≥3.8，**只用标准库，无需 pip 装任何东西**）、`git`。
- 对仓库 `git@github.com:CyberOrigin2077/CyberMemory.git` 有 **push 权限**（SSH key 或 token）。没有就先配，或问用户。

## 让"以后的工作"也被记录：维护 `agent_memory.md`

采集器读的是各项目目录下的 **`agent_memory.md`**（纯 markdown，与具体 agent 无关）。请在之后的工作中持续维护它：

- 会话开始先读项目根 `agent_memory.md`，理解前人改动；没有就新建。
- **每次做出有意义改动后**追加一条，按时间组织，包含：
  - `## YYYY-MM-DD —— 简短标题`
  - **改了什么 / 为什么 / 状态(doing|done) / 验证 / 涉及文件**
- 复杂任务可加 `## doing / 进行中` 区块登记当前在做的事，方便多 agent 协作不撞车。

只要照此维护，`contribute.sh` 就能把它收进总图，**无需任何代码改动**——这是 Codex 与 Claude 通用的桥梁。

## 原生会话「自动提炼」补缺口（distill.py，contribute.sh 已内置，无需你手动做）

即使某项目**没写** `agent_memory.md`、也没 Claude `memory/` 覆盖，`contribute.sh` 的 `[2/4]` 步会跑 `distill.py`，从本机原生会话里**只抽结构化字段**把它补进图：
- **三源**：Claude `~/.claude/projects/<slug>/*.jsonl`、Codex `~/.codex/sessions/**/rollout-*.jsonl`、Cursor `~/.config/Cursor/.../state.vscdb`（纯标准库+sqlite3，无需 pip）。某源不存在则自动跳过。
- **只抽结构化字段**：标题、日期、编辑过的**文件路径**、工具名/次数——**绝不**提取对话正文/代码/工具输出/密钥。
- **仅补缺口**：项目已有 `agent_memory.md` 或 Claude `memory/` 就跳过；按**项目×天**聚合成一条 `derived` 记录（图里更黯淡、可一键筛掉）。
- **开关**：默认开；`AMG_DISTILL=0 ./contribute.sh …` 关闭。想预览：`python3 distill.py --machine <名> --dry-run -v`。

**所以：照常维护 `agent_memory.md` 仍是最佳（人工筛过、最准）；但即便没写，原生会话也会被自动提炼补上。**

## 基站模式（server 接入的推荐路径）
新 server **无需 push 权限、无需自己的 cron**：server 上放一份仓库副本（只读 clone 即可），主基站（汇总端）的 `sources.json` 加一条 `remote_collect:true` 的 ssh 源，`./update.sh --pull` 会经 `pull_remote.sh` 主动 ssh 过去远程跑 collect+distill、取回 fragment、合并发布。

## 红线
- 别把明文记忆放进 `docs/`（若启用公开 Pages，那里只放加密密文）。
- 碎片 `fragments/*.json` 是明文，但只存在于**私有**仓库，可接受。
- 别在贡献端开 Pages、别动加密口令（`.amg_password`/`.amg_password2`，仅汇总端用）。

## 多 agent 实时协作（多机同时干一个 project）
1. **声明同一 project**：项目目录放 `.amg_project`（一行 canonical id），或在 `projects.json` aliases 里映射。相同 canonical id 归并成同一项目节点。
2. **报到心跳**（准实时，~10min）：
   ```bash
   ./heartbeat.sh <machine> <agent> <canonical_project> "<正在做什么>"   # 可配 cron 或 --loop
   ./heartbeat.sh <machine> <agent> --idle                              # 收工
   ```
   它会先**列出别的 agent 在做什么**（避免撞车），再 pull 回别人的状态/记忆、push 你的。
3. 正在工作的 agent 在星空图显示为**红光**。详见 `ONBOARDING.md` §6。

## 更多
- `ONBOARDING.md` — 完整多机同步手册（角色模型、多 agent 协作、手动命令、cron、排错）。
- `PORTABILITY.md` — 换机/换 AI/脱离特定工具的迁移说明。
- `README.md` — 架构与数据模型。
