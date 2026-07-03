# CLAUDE.md — CyberMemory 同步中枢

> 你（Claude）在本仓库里工作。CyberMemory 把各机 agent 工作记忆汇聚成知识图谱，并（可选）加密发布。**与 `AGENTS.md`（给 Codex/其他 agent）内容一致**；完整手册见 `ONBOARDING.md`。

## 用户若让你"把这台机器的 agent memory 同步上来"，执行：

```bash
./contribute.sh <本机唯一名> claude        # 默认扫 $HOME；可加第三参指定目录
```
它采集本机 `agent_memory.md` + `.claude/projects/*/memory/` → `fragments/<本机名>.json`，并**自动提炼原生会话**（见下）→ `fragments/<本机名>-distilled.json` → 提交推送。汇总端（主力机）下次 `update.sh` 自动合并（两个碎片都吃）、（可选）加密、更新发布。**贡献端不加密、不碰 `docs/`、不需要密码。**

- 前置：`python3`(标准库即可，含 sqlite3) + `git` + 对 `git@github.com:CyberOrigin2077/CyberMemory.git` 的 push 权限。
- `<本机唯一名>` 要唯一；第二参 `claude` 用于在图里标记工具来源（也可 `codex`/`human`）。

## 原生会话「自动提炼」补缺口（distill.py，contribute.sh 已内置）
即使某项目**没写** `agent_memory.md`、也无 Claude `memory/` 覆盖，`contribute.sh [2/4]` 会跑 `distill.py` 从**原生会话**里**只抽结构化字段**（标题/日期/编辑文件/工具，**绝不进对话正文/代码/密钥**）把它补进图：三源 Claude(`.claude/projects/*/*.jsonl`)/Codex(`~/.codex/sessions`)/Cursor(`state.vscdb`)，不存在则跳过；**仅补缺口**（有人工记录的项目跳过）、**项目×天聚合**、标 `derived`（图里黯淡可筛）。开关 `AMG_DISTILL=0`；`--with-summary`/`--llm` 默认关。人工维护 `agent_memory.md` 仍最准，提炼只是兜底补缺。

## 维护 `agent_memory.md`（让以后的工作也进图）
每次有意义改动后，在项目根 `agent_memory.md` 追加：`## YYYY-MM-DD 标题` + 改了什么/为什么/状态(doing|done)/验证/涉及文件。采集器读的就是它（纯 markdown、跨 agent 通用）。

## 如果你是在**汇总端 = 主基站**（主力机）
跑 `./update.sh`（或 `./update.sh --pull` 连 server 一起）：`git pull` 取碎片 → **[0.3] 基站远程采集**（`pull_remote.sh`：ssh 到各 `remote_collect` server 远程跑 collect+distill 并取回 fragment）→ 采集+合并 → （可选）加密 → 推送。
- **默认全私有**：仓库设为 private，团队本地看 `standalone.html`，可完全**不用**加密/Pages。
- **可选加密在线共享**：配两个密码文件 `.amg_password`+`.amg_password2`（双密码，访问需两个都对），`encrypt.py` 生成 `docs/graph.enc.json`。详见 `ONBOARDING.md` / `PORTABILITY.md`。

## 基站模式：新增一台 server
server **无需 git push 权限、无需自己的 cron**——local 主基站主动访问它：
1. server 上 `git clone` 本仓库（只读即可；供 collect.py/distill.py 运行）。
2. 本机 `sources.json` 的 `sources` 数组加一条 `remote_collect:true` 的 ssh 源（样例见 `sources.json` 的 `_examples.remote_collect`），填 host/user/port/repo。
3. 跑 `./update.sh --pull` 即自动远程采集+提炼+取回+合并+发布。前置：本机对 server 免密 ssh。

## 多 agent 实时协作（多机同时干一个 project）
- **识别同项目**：项目目录放 `.amg_project`（一行 canonical id）或在 `projects.json` aliases 里映射；相同 canonical id 归并成同一项目节点。
- **报到心跳**（~10min 准实时）：`./heartbeat.sh <machine> <agent> <canonical_project> "<在做什么>"`（可 `--loop`/cron；收工 `--idle`）。它先列出别人在做什么（避免撞车），再 pull 回别人状态/记忆并 push 你的。
- 正在工作的 agent 在星空图显示**红光**。详见 `ONBOARDING.md` §6。

## 红线
明文记忆不进 `docs/`（若启用 Pages，公开目录只放加密密文）；碎片明文仅存私有仓库；贡献端别开 Pages、别动加密口令（`.amg_password`/`.amg_password2`，仅汇总端用）。
