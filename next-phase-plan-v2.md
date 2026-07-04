# Knowledge Compiler — 下一阶段计划 v2

> **基于 ChatGPT + ClaudeCode 审核后的更新版**
> 审核日期：2026-07-04
> 审核结论：**有条件支持**（两位审核者均同意方向，均建议调整 Benchmark 优先级）

---

## 距上一篇计划的变更

| 变更 | 原因 |
|------|------|
| Phase 3（Benchmark）拆分并提前 | 两位审核者一致认为 Benchmark 应在 Developer Experience 之前 |
| 新增 Phase 0：Mini Benchmark | ClaudeCode 建议先跑一个小规模 benchmark 验证叙事风险 |
| Phase 1（NSCA）增加 Pilot 阶段 | ClaudeCode 建议先处理 2-3 节验证 schema 兼容性，再铺开 |
| Phase 1 预算从 $20 调整到 $50 | ClaudeCode 指出页数可能远超 ACSM，需要 retry 缓冲 |
| 新增"发布策略"跟踪项 | ClaudeCode 指出项目目前 0 star，需要主动分发 |
| 新增失败案例记录 | ChatGPT 建议记录 schema/prompt 无法处理的情况 |
| 新增版本兼容性跟踪 | ChatGPT 建议尽早设计 schema_version / ontology_version |
| 新增 Evaluation Leakage 防范 | ChatGPT 指出 question 不应直接来自 object 标题 |

---

## Phase 0：Mini Benchmark（风险验证，2 天）

**目标：** 在大规模投入 NSCA 之前，先验证"Knowledge Compiler 比 RAG 好"这个故事是否成立。

### 子步骤

1. **从现有 25 题中挑 6-10 题**覆盖 ACSM Ch1-3 的不同类型（Concept / Threshold / Procedure / Warning / Recommendation）
2. **建立 RAG baseline**：用 sentence-transformers（`all-MiniLM-L6-v2`，CPU 可跑）对 ACSM 的 chunk 做检索
3. **三组条件**：
   - Raw LLM：直接问 GPT-4o-mini（低成本）
   - RAG：检索 top-3 chunks + GPT-4o-mini 回答
   - Knowledge Compiler：现有 74 个 objects，直接查找
4. **人工评估**：每题标注 accuracy + citation correctness
5. **决策门**：
   - 数字好（KC 明显优于 RAG）→ 继续 Phase 1，带着数字 launch
   - 数字一般 → 先完成 Phase 1（看第二本书是否改善结果），再调整 evaluation

### 注意

- Question 设计要防止 Evaluation Leakage：问题不能直接来自 object 的 `canonical_name` 或标题
- 记录每个失败案例到 `docs/failure_cases.md`

### 谁做

| 工作 | 执行者 |
|------|--------|
| RAG baseline 搭建 + 跑对比 | 你（CLI） |
| 分析 + 记录 | 你（CLI） |

---

## Phase 1：跨领域泛化 — NSCA 教材（核心里程碑，5-10 天）

### 子步骤

1. **Pilot（1 天）** — 先处理 NSCA 前 2-3 个章节，验证：
   - 现有 8 个 schema 类型是否够用
   - prompts 是否需要调整
   - 是否需要新增 schema 类型 / ontology predicate
2. **全书管线运行** — 如果 pilot 通过，铺开到全书
3. **失败案例记录** — 每遇到 schema 无法表达的内容，记入 `docs/failure_cases.md`
4. **整合** — 更新 `registry.yaml`、`index.yaml`、README 添加 "Supported Books"

### 关键检查点

- 是否需要新增 schema 类型？
- prompts（02_extract.md, 03_object_generate.md）是否需要改动？
- 是否需要新增 ontology predicate？
- 每个失败的 case 是否已记录？

### 谁做

| 工作 | 执行者 |
|------|--------|
| Pilot + 全书管线（需 AI API） | 你（CLI） |
| 整合、验证、README 更新 | 我（Desktop） |

---

## Phase 2：完整 Benchmark（3-5 天）

### 子步骤

1. **扩展 evaluation set** 到 25 题，跨两本书（ACSM + NSCA）
2. **完整跑三组对比**，控制 randomness（固定 temperature=0，多次运行取平均）
3. **将结果写入 README** 作为 "Performance" 板块

### 注意

- Question 必须独立于 object 标题设计
- 记录每题的精确 prompt 和输出，保证可复现

### 谁做

| 工作 | 执行者 |
|------|--------|
| 实验设计 + 运行 | 你（CLI） |
| 结果整合到 README | 我（Desktop） |

---

## Phase 3：发布策略（2 天）

**目标：** 让目标用户知道这个项目存在。

### 子步骤

1. **写一篇 blog post 或 Twitter/X thread** 解释 "third path" 的核心 idea
2. **做一个 30 秒的 demo GIF 或录屏**展示 demo.py 的输出
3. **准备 Show HN 的标题和摘要**
4. **分渠道发布**：运动科学社区 → ML 社区（不同的 pitch）

### 谁做

| 工作 | 执行者 |
|------|--------|
| 内容撰写 | 你（CLI），我可以帮你起草 |
| Demo 录制 | 你（CLI） |
| README 更新 + 发布物料整合 | 我（Desktop） |

---

## Phase 4：开发者体验 + 社区（2-3 天）

### 子步骤

1. **Schema 示例目录** — `docs/examples/` 下放每个类型的真实 YAML 示例
2. **CLI 入口** — 明确 `knowledge_compiler/` 和 `compiler/` 的关系（合并或重构）
3. **Issue/PR 模板**
4. **"How to add a new book" 指南**

### 谁做

| 工作 | 执行者 |
|------|--------|
| 以上全部 | 我（Desktop） |

---

## 版本兼容性（跨各 Phase 持续）

ChatGPT 提醒了一个容易被忽略的问题：schema 和 ontology 需要版本号。

- 在 `ontology_spec.md` 中加入 `ontology_version` 字段
- 在 `schema/*.yaml` 中加入 `schema_version` 字段
- 在 `compiler` 中加入 `compiler_version`
- 处理新版 schema 如何兼容旧版 objects

### 谁做

| 工作 | 执行者 |
|------|--------|
| 版本号设计 + 文档更新 | 我（Desktop） |

---

## 时间线

```
Week 1    Week 2    Week 3    Week 4
┌──────┐  ┌──────┐  ┌──────┐  ┌──────┐
│ P0   │  │ P1   │  │ P2   │  │ P3+P4│
│ Mini │  │ NSCA │  │Bench │  │Launch│
│Bench │  │      │  │      │  │+Docs │
└──────┘  └──────┘  └──────┘  └──────┘
  2天       5-10天    3-5天     4-5天
```

---

## 需要你确认的事项

1. **Mini Benchmark 先行的逻辑** — 先花 2 天跑 6-10 题验证数字，再决定是否投入 NSCA。这个策略你认可吗？
2. **NSCA PDF** — 你手头有吗？是第一版还是新版？
3. **API 预算** — NSCA 预估 $30-50，能接受吗？
