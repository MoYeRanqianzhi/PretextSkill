# Pretext Skill 项目记忆

## 项目简介

- 项目名称：Pretext Skill
- Skill 名称：`pretext`
- 当前目标：基于本地参考仓库 `./pretext/` 开发一个符合统一标准的 Agent Skill
- 参考实现：`https://github.com/chenglou/pretext`，已克隆到 `./pretext/`

## 仓库约定

- Skill 开发目录：`./skills/pretext/`
- 持久化文档目录：`./docs/`
- 项目初始化方式：`npx skills init`
- 当前仓库将忽略本地参考代码目录 `./pretext/`

## 使用说明

- 当前阶段仅完成 Git 仓库初始化、忽略规则设置、远程仓库创建与首个提交
- 后续开发前，先阅读本文件与 `./docs/CHANGELOG.md`
- 重要决策、待办、已知问题与阶段性结论必须优先写入 `./docs/`

## 已知问题

- Skill 脚手架尚未初始化
- `./skills/pretext/` 尚未创建
- 参考仓库与目标 Skill 的能力映射尚未整理

## 待办事项

- 执行 `npx skills init`
- 使用 `skill-creator` 设计并生成 `skills/pretext/` 基础结构
- 梳理 `pretext` 参考仓库的核心能力、输入输出与可复用脚本
- 建立 `SKILL.md`、`scripts/`、`reference/` 的渐进式披露结构

## 开发约束

- 所有重要事项必须文档化，避免仅依赖会话上下文
- 优先保证结论可追溯、可验证、可解释
- 不确定的信息必须通过工具或资料核实，禁止猜测
