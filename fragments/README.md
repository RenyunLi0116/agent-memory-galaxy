# fragments/ — 其他机器提交的记忆碎片

每台**非汇总端**机器把自己的 agent 记忆采集成 `fragments/<机器名>.json` 提交到这里（外加可选的 `fragments/<机器名>-distilled.json` 派生碎片）。
汇总端跑 `collect.py --merge`（即 `update.sh`）时会把这里所有 `*.json` 合并进总图（按节点 id 去重，共享实体如数据集/项目自动合并）。

具体怎么做见仓库根目录 **ONBOARDING.md**。

> 这些碎片是明文完整数据，**只存在于本私有仓库**；若启用加密在线发布，对外只发密文，二者分离。
