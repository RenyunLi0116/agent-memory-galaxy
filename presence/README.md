# presence/ — agent 实时报到状态

每个正在工作的 agent 一个文件 `<machine>__<agent>.json`，由 `heartbeat.sh` 维护：
```json
{ "agent":"codex-1", "machine":"work-pc",
  "project_canonical":"myproj", "project":"myproj",
  "status":"working", "current":"训练 myproj 阶段2",
  "heartbeat":"2026-07-01T10:32:00Z", "tool":"codex" }
```
汇总端 `collect.py`（`update.sh`）读取这些，把「心跳新鲜且 status=working」的 agent 在星空图里标成**红光**，并按 `project_canonical` 连到同一个项目节点——于是同一 project 上的多个 agent 会在图里聚到一起。

一个 agent 一个文件 → 多机并发 push 不冲突。详见根目录 `ONBOARDING.md`「多 agent 实时协作」。
