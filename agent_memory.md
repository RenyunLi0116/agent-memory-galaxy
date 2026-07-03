# CyberMemory — 工作记录

> 本文件是 CyberMemory 仓库自身的 agent 工作记录，也是 `agent_memory.md` 格式的示例。
> 约定：每次有意义改动后，按时间追加一节；采集器（`collect.py`）会把它解析进知识图谱。

## 2026-07-03 —— CyberMemory 初始化 (claude)
- **改了什么**：从一套个人的多机 agent 记忆图谱方法中**提炼通用框架**，去除全部私人信息（个人路径 / 主机 IP / 用户名 / 私有数据集与模型名 / Notion 账号 / 密钥），整理成可复用框架 CyberMemory。
- **为什么**：让团队各机、各 agent（Claude/Codex/Cursor/人）的工作记忆能统一汇聚成一张知识图谱，便于协作与检索。
- **状态**：done
- **验证**：`collect.py`（贡献端/汇总端两种模式）、`build_artifact.py`、`encrypt.py` 均本地跑通；实体抽取（IP/ViT/wandb/思路N）、跨项目引用检测、双密码加密均正常。全仓库无残留私人标识。
- **涉及文件**：collect.py, distill.py, encrypt.py, build_artifact.py, to_notion.py, auto_presence.py, contribute.sh, update.sh, heartbeat.sh, pull_remote.sh, sources.json, projects.json, docs/index.html, README.md, ONBOARDING.md, AGENTS.md, CLAUDE.md, PORTABILITY.md
