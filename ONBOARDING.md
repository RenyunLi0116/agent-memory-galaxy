# 多机同步维护手册（给其他机器上的 agent / 人看）

> 目标：让**任意一台机器**把它本地的 agent 工作记录（`agent_memory.md` + Claude 自动记忆 `.claude/projects/*/memory/`）汇聚进同一张 **CyberMemory** 知识图谱，最终在本地 `standalone.html` 或（可选）加密在线页面上查看。

## 0. 角色模型（先理解）

| 角色 | 是谁 | 做什么 |
|---|---|---|
| **汇总端 (builder)** | 主力机（团队指定一台） | 跑 `update.sh`：采集本机 + ssh 拉 server + **合并所有机器的 fragment** → （可选）加密 → 推送 → 更新展示 |
| **贡献端 (contributor)** | 你的其他机器（笔记本/台式/server…） | 把本机记忆采集成 `fragments/<机器名>.json`，**git 推送**到共享私有仓库即可。不需要加密、不需要碰展示 |

为什么贡献端走 **git 推送**而不是被 ssh 拉取：笔记本常在 NAT 后、IP 不固定，无法被主力机反向 ssh；而 git push 是**出站**的，任何网络都能用。

```
你的机器A ─┐ push fragments/A.json
你的机器B ─┤ push fragments/B.json ─►  私有仓库  ─►  汇总端 update.sh --merge  ─►  展示
server    ─┘ (汇总端 ssh 拉取/基站)        (fragments/)     合并成一张总图        (本地/可选加密在线)
```

合并是按**节点 id 去重**的：各机的"工作记录"互不冲突（id 带机器名），而**共享实体**（同一个数据集、同一个项目、同一台 server…）会**自动合并成一个节点**，于是不同机器的工作通过共享实体连成一张网。

---

## 1. 在一台新机器上接入（一次性）

### 前置条件
- `python3`（≥3.8，**只用标准库，无需 pip 安装任何东西**）
- `git`
- 对私有仓库有 **push 权限**：`git@github.com:CyberOrigin2077/CyberMemory.git`
  - 用 SSH：把这台机的 SSH 公钥加到你的 GitHub 账号；或用 HTTPS + Personal Access Token。

### 步骤
```bash
# 1) 克隆仓库
git clone git@github.com:CyberOrigin2077/CyberMemory.git
cd CyberMemory

# 2) 一条命令：采集本机记忆 → 生成碎片 → 提交 → 推送
#    <本机名> 起个**唯一**的名字（如 mac-home / work-pc / lab-server），不要和别的机器重名
./contribute.sh <本机名> claude
#    默认扫描 $HOME；如果家目录太大/太慢，指定具体目录：
#    ./contribute.sh work-pc claude /home/me/projects
```

**汇总端**下次跑 `update.sh`（手动或定时 cron）会自动把你的 `fragments/<本机名>.json` 合并进总图。

### 想自动化（可选）
在这台机加一条 cron，每周推一次本机记忆：
```cron
17 9 * * 1  cd /路径/CyberMemory && ./contribute.sh <本机名> claude >> contribute.log 2>&1
```

---

## 2. 手动方式（不想用脚本时）

`contribute.sh` 等价于：
```bash
cd CyberMemory
git pull
python3 collect.py --local-only --machine <本机名> --tool claude --roots "$HOME" --out fragments/<本机名>.json
python3 distill.py --machine <本机名> --out fragments/<本机名>-distilled.json   # 可选，兜底补缺
git add fragments/<本机名>.json fragments/<本机名>-distilled.json
git commit -m "memory: <本机名>"
git push
```
- `--local-only`：只扫本地、跳过 ssh（贡献端不需要拉 server）。
- `--roots`：要扫描的根目录，逗号分隔多个。
- `--machine`：本机标识，决定碎片文件名与机器节点名。

---

## 3. 汇总端怎么收（通常你不用管）

汇总端（主力机）的 `update.sh`：
- `git pull`：取回各机推上来的 fragments/；
- `[0.3]` 基站远程采集（`--pull` 时，见 §3.1）；
- `[0.4]` auto-presence：自动点亮本机"正在工作"的红光；
- `[0.5]` 提炼本机缺口项目；
- `collect.py --merge`：合并 `fragments/*.json`；
- **（可选）** `encrypt.py` → `docs/graph.enc.json`，用于加密在线发布；
- `build_artifact.py` → 本地 `standalone.html`（含明文，仅本地）；
- 提交推送。

> 换一台机当汇总端：配好对 server 的免密 ssh（若用 `--pull`），（如要加密在线）再配两个口令文件 `.amg_password` / `.amg_password2`，跑 `./update.sh --pull`。详见 `PORTABILITY.md`。

### 3.1 基站模式（新增 server 的推荐路径）
汇总端即**主基站**：`update.sh --pull` 的 `[0.3]` 步经 `pull_remote.sh` 主动 ssh 到各 `remote_collect:true` 的 server，**远程**跑 `collect --local-only` + `distill`（nohup 抗断连、完成标记轮询、scp 取回 fragments/）。server 只需一份仓库副本，**无需 git push 权限、无需自己的 cron**。配置样例见 `sources.json` 的 `_examples.remote_collect`（把它拷进 `sources` 数组并改值）。

---

## 4. 注意事项

- **机器名唯一**：两台机用同名会互相覆盖碎片。
- **隐私**：`fragments/*.json` 是**明文完整数据**，只存在于这个**私有**仓库里。默认全私有、本地看图；若启用加密在线发布，对外只发**密文**，两者分离——所以贡献端**不要**手动开 Pages、不要把 fragment 放进 `docs/`。
- **不需要密码**：加密口令只在汇总端、且只在启用加密在线时用；贡献端只产出明文碎片、推到私有仓库。
- **删除一台机的记忆**：删掉 `fragments/<机器名>.json` 并 push，汇总端下次合并就不再包含它。
- **扫描太慢**：`--roots` 指到具体项目目录，别扫整个 `$HOME`；采集器会自动跳过 `node_modules`、`.cache`、`venv`、`miniconda3` 等（见 `sources.json` 的 prune 列表）。

---

## 5. Codex / 其他 agent 也能接入（agent 无关）

- **桥梁是 `agent_memory.md`**（纯 markdown，与具体 agent 无关）。只要那台机上的 agent（Codex 等）按约定维护它，`contribute.sh` 就原样收录，**无需任何代码改动**。
- 入口文档已双份：**Codex 自动读 `AGENTS.md`**、Claude 自动读 `CLAUDE.md`（内容一致）。
- 贡献时第二参标明工具：`./contribute.sh <名> codex`；图里可按「工具」着色，区分 claude / codex / human。
- **原生会话已自动提炼**（`distill.py`，`contribute.sh [2/4]` 已内置）：从 Claude/Codex/Cursor 原生会话里**只抽结构化字段**（标题/日期/编辑文件/工具，绝不进对话正文/代码/密钥）补缺口，标 `derived`。开关 `AMG_DISTILL=0`。

## 6. 多 agent 实时协作（识别同项目 + 心跳 + 红光）

> 场景：多台机器 / 多个 agent（Claude、Codex…）同时在同一个 project 上干活，想彼此知道进展、避免撞车。基于 git 的**准实时**协作——粒度 ~10 分钟，非秒级长连接。

### 6.1 识别"同一个 project"（canonical id）
不同机器上同一个项目往往目录名不同。用 **canonical id** 归并成图里的**同一个项目节点**，两种声明方式（任一即可）：
- **`.amg_project` 文件**：在项目目录放一个文件 `.amg_project`，内容一行就是 canonical id（优先级最高，各机自己放）。
- **`projects.json` 别名表**：在仓库根 `projects.json` 的 `aliases` 里写 `"各机目录名": "canonical-id"`，`labels` 里写 `"canonical-id": "友好显示名"`。

### 6.2 报到 / 心跳
```bash
./heartbeat.sh <machine> <agent> <canonical_project> "<正在做什么>"
./heartbeat.sh <machine> <agent> <canonical_project> "<...>" --loop   # 每10分钟自动上报
./heartbeat.sh <machine> <agent> --idle                              # 收工，置 idle
# 可选 AMG_TOOL=claude|codex|human 标明工具
```
它做三件事：① 更新自己的 `presence/<machine>__<agent>.json`；② `git pull` 拉回**别人的状态与记忆**；③ push 自己的状态（rebase 重试，一个 agent 一个文件、多机并发不冲突）。建议 cron：`*/10 * * * * cd /路径 && ./heartbeat.sh ...`。

### 6.3 开工前先查重
`heartbeat.sh` 每次运行会先**列出别的 agent 在做什么**。开工前先看：若已有别的 agent 在同一 canonical project 标 working，读它的 `current` 与该项目最近的 `agent_memory.md`，协调分工，别重复。

### 6.4 可视化：红光=正在工作
汇总端 `update.sh` 会把 `presence/` 併入图。查看器里：
- **🔴 红光强脉冲** = 正在工作的 agent（心跳新鲜且 status=working；查看器用时间戳现算，过期自动降级）。
- 同一 project 上的多个 live agent 之间画**红色协作链路**，汇聚到共同的项目节点。
- 顶栏显示"◉ N agent 在线"；页面定时自动刷新 live 状态。
- 🟢 绿光表示"最近有记录"（历史活跃），与红光（此刻在线）并存。

### 6.5 隐私
`presence/*.json` 是明文，只存在于**私有**仓库；别放进 `docs/`。

## 7. 给 AI agent 的速记

你被叫来"把这台机器的 agent memory 同步上去"，照做：
1. 确认能 push 到 `git@github.com:CyberOrigin2077/CyberMemory.git`（不能就先配 SSH key / token，或问用户）。
2. `git clone` 该仓库（若本地没有）。
3. 跑 `./contribute.sh <给这台机起的唯一名字> <claude|codex|human>`。
4. 告诉用户：已推送 N 节点的碎片，汇总端下次刷新即并入。
不要在贡献端加密或动 Pages；不要把明文放进 `docs/`。
