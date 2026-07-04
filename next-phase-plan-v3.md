# Knowledge Compiler — 下一阶段计划 v3

> **基于 ChatGPT + ClaudeCode v2 审核后的更新版**
> 审核日期：2026-07-04
> v2 → v3 核心变更：**所有 Decision Gate 添加量化标准**

---

## 距 v2 的变更

| 变更 | 触发者 | 原因 |
|------|--------|------|
| Phase 0/Minibenchmark + Phase 3 合并为一个完整 Phase，去掉中间的决策碎片 | 结构优化 | 两次决策门之间距离太短，实际难以独立执行 |
| **所有 Decision Gate 添加量化 Threshold** | ChatGPT | "明显优于"太模糊 |
| **NSCA Pilot 添加退出机制** | ChatGPT | 避免无限制迭代 |
| **Phase 0 添加局限性标注** | ClaudeCode | ACSM-only benchmark 不代表泛化能力 |
| **Phase 每步添加用户 Persona 定义** | ChatGPT | 不同人需要不同 pitch |
| Phase "Launch" 改名为 **"Validation & Launch"** | ChatGPT | 重点是收集外部反馈，不是发帖 |

---

## 总时间线

```
Week 1      Week 2-3     Week 4      Week 4-5
┌────────┐  ┌─────────┐  ┌────────┐  ┌────────────┐
│  Phase 0  │  Phase 1   │  Phase 2  │  Phase 3    │
│          │  │         │  │        │  │           │
│ Benchmark│  │ NSCA    │  │ 完整   │  │Validation │
│ + Launch │  │ Pilot→  │  │Benchmark│  │+ Dev Exp  │
│ 准备     │  │ 全书    │  │        │  │+ Community│
└────────┘  └─────────┘  └────────┘  └────────────┘
```

---

## Phase 0：Mini Benchmark + Launch 准备（3 天）

**目标：** 用最小成本验证"KC 是否优于 RAG"这个故事是否成立。如果成立，带着数字准备发布物料。

### 子步骤

1. **设计 6-10 题**，覆盖 ACSM Ch1-3 的 Concept / Threshold / Procedure / Warning / Recommendation
   - 每种类型至少 2 题（避免 sampling bias）
   - Question 不能直接来自 object 的 `canonical_name` 或标题（防止 evaluation leakage）
2. **建立 RAG baseline**（sentence-transformers `all-MiniLM-L6-v2`，CPU 可跑）
   > 注意：当前 baseline 为轻量级 embedding。后续完整 Benchmark（Phase 2）会补充更强的 baseline（BGE / OpenAI embedding），避免对 MiniLM 过拟合。
3. **三组条件**：Raw LLM / RAG on PDF / Knowledge Compiler
4. **人工评估**：每题标注 accuracy + citation correctness
5. **产出数字**：
   - Raw LLM accuracy: __%
   - RAG accuracy: __%
   - KC accuracy: __%
   - Citation correctness per condition
6. **如果数字达标** → 开始准备 Launch 物料（blog draft + demo GIF + Show HN 标题）
7. **如果数字不达标** → 记录失败原因，调整 prompts 或 evaluation design 后重试

### 量化决策标准

> **阈值来源说明：** 以下 thresholds 是 engineering targets，基于 ACSM Ch1-3 的内容密度和类型分布设定，非统计推导得出。完整 Benchmark（Phase 2）会在此基础上做统计检验。

```
继续执行 Phase 1 的条件（需同时满足）：
  KC accuracy ≥ 80%              ← 绝对标准：KC 本身必须有用
  KC accuracy − RAG accuracy ≥ 10%   ← 相对标准：必须明显优于 baseline

黄色预警（可以继续但需要记录）：
  5% ≤ KC − RAG < 10%            ← 优势不足，需在 Phase 1 寻找改进空间

红色停止（先不进入 Phase 1）：
  KC accuracy < 80%               ← KC 本身不够可靠
  KC − RAG < 5%                   ← 没有实际优势，需要先修 prompts/evaluation
```

### 小样本补救规则

Phase 0 仅 6-10 题，一道题可改变 10-17 个百分点，统计稳定性有限。补充规则：

- 如果所有指标在阈值临界区（±5pp 内），不要直接 stop，而是扩展到 **15-20 题**再判断（多花 0.5 天）
- 如果远超阈值或远低于阈值，6-10 题足够做决策
- 无论结果如何，Phase 0 的记录中必须标注样本量局限

### 局限性与标注

**Phase 0 验证的是：** "在当前 ACSM Ch1-3 的数据上，我们有没有资格讲这个故事。"
**Phase 0 不能验证的是：** "KC 是否在任意教材上都优于 RAG。"

如果 Phase 0 数字好，只能确认 ACSM Ch1-3 上成立，**不能** 自动泛化到 NSCA 或其他书。
如果 Phase 0 数字差，NSCA 大概率也不会更好（因为数据质量和 prompt 的通用性问题会放大）。

### 谁做

| 工作 | 执行者 |
|------|--------|
| RAG baseline + 跑对比 | 你（CLI） |
| Launch 物料准备 | 你 + 我合作 |

---

## Phase 1：跨领域泛化 — NSCA（5-10 天）

**目标：** 验证 Knowledge Compiler 的 schema 和 prompts 能否泛化到第二本教材。

### 角色

**核心用户 Persona：LLM Agent Developer**
- 想用结构化知识增强 agent 的可靠性
- 关心的是：schema 是否灵活、能否处理自己的领域
- 对他们来说 NSCA 就是"你的框架能不能处理非 ACSM 的内容"

### 子步骤

1. **Pilot（1-2 天）** — 处理 NSCA 前 2-3 个章节，验证：
   - 现有 8 个 schema 类型是否够用
   - prompts 是否需要调整
   - 是否需要新增 schema 类型 / ontology predicate

2. **Pilot 决策门**：
   ```
   继续全书处理的条件：
     新增 schema 类型 ≤ 1
     prompt 修改次数 ≤ 3
     首个 chunk 的 validation 通过率 ≥ 70%

   停止 / 重新评估的条件：
     新增 schema 类型 ≥ 2   ← schema 体系不够通用
     prompt 修改次数 > 5     ← 当前 prompt 设计有问题
     首个 chunk validation < 50%  ← 基础流程不通
   ```

3. **如果通过 → 全书管线运行**
   - extraction + normalization（预算 $30-50）
   - validate + decompose
   - 失败案例记录到 `docs/failure_cases.md`

4. **如果未通过 → 记录原因**，调整 schema/prompts 后在第二本不同的书上重试

### 谁做

| 工作 | 执行者 |
|------|--------|
| Pilot + 全书管线（需 AI API） | 你（CLI） |
| 整合、验证、README 更新 | 我（Desktop） |

---

## Phase 2：完整 Benchmark（3-5 天）

**目标：** 跨 ACM + NSCA 两本书，产出可信的对比数据。

### 角色

**核心用户 Persona：Biomedical NLP / Knowledge Graph Researcher**
- 关心 methodology 是否严谨
- 需要看到：评估方法、数据可复现、统计显著性
- 对他们来说 Benchmark 设计比绝对数字更重要

### 子步骤

1. **扩展 evaluation set 到 25 题**，跨两本书，覆盖所有 6 种 object 类型
2. **完整三组对比**，控制 randomness（固定 temperature=0，重复 3 次取平均）
3. **补充更强的 RAG baseline**（BGE 或 OpenAI embedding），避免 MiniLM 拖低 RAG 表现导致结果虚高
4. **预注册评估方案**：在执行前固定 metric → statistic → threshold，避免根据结果事后选择统计方法
   - **Accuracy**：回答是否与教材一致
   - **Citation Correctness**：引用的章节/页码是否真实
   - **Faithfulness**：回答是否有 hallucination
   - **Latency**：端到端响应时间
   - **Cost**：每次查询的 API 成本
4. **统计方法**：McNemar's test（配对分类变量）或 bootstrap 置信区间
5. **结果写入 README** 作为 "Performance" 板块

### 量化通过标准

```
完整 Benchmark 成功条件：
  KC accuracy ≥ 85%                    ← 绝对质量门槛
  KC − RAG accuracy ≥ 10 个百分点      ← 有实际意义优势
  KC citation correctness ≥ 90%        ← 引用可信度
  KC − RAG citation ≥ 15 个百分点      ← 引用是核心差异化优势

如果 KC accuracy < 75% 或 KC − RAG < 5%：
  → 暂不发布 Benchmark 结果，先排查问题
```

### 谁做

| 工作 | 执行者 |
|------|--------|
| 实验设计 + 运行 | 你（CLI） |
| 结果整合到 README | 我（Desktop） |

---

## Phase 3：Validation & Launch + 开发者体验（4-5 天）

### 角色

**核心用户 Persona：Medical AI / Sports AI Practitioner**
- 想用编译后的 objects 做实际应用
- 关心的是：能不能处理我的 PDF？API 好用吗？
- 对他们来说一个可用的 demo / API 比 100 个 star 更有价值

### 子步骤

1. **外部验证** — 邀请 3-5 个不了解项目的人：
   - Clone → 1 分钟内知道这是做什么的吗？
   - Run demo.py → 10 分钟内能跑起来吗？
   - 是否愿意拿自己的 PDF 试？
   - 记录每个卡住的地方

2. **发布物料**
   - Blog post 或 Twitter/X thread 解释 "third path"
   - 30 秒 demo GIF 或录屏
   - Show HN 标题 + 摘要
   - 分渠道：运动科学社区 vs ML 社区（不同 pitch）

3. **迭代修复** — 根据外部验证结果修复 top 3 体验问题

4. **开发者体验**
   - Schema 示例目录 `docs/examples/`
   - CLI 入口（合并 `knowledge_compiler/` 和 `compiler/`）
   - Issue/PR 模板
   - "How to add a new book" 指南

### 谁做

| 工作 | 执行者 |
|------|--------|
| 外部验证组织 + 发布 | 你（CLI） |
| 文档 + CLI 重构 + Issue 模板 | 我（Desktop） |

---

## 跨 Phase 持续事项

### 失败案例记录

每遇到 schema/prompt 无法处理的情况，记入 `docs/failure_cases.md`：
- Schema 无法表达的内容
- Prompt 歧义导致的错误
- Table / Figure 无法解析
- 这些记录未来对论文和方法论改进非常重要

### 版本兼容性

- `ontology_spec.md` 加入 `ontology_version`
- `schema/*.yaml` 加入 `schema_version`
- `compiler` 加入 `compiler_version`
- 定义新版 schema 如何兼容旧版 objects

### 论文素材积累（跨 Phase）

每个 Phase 执行时同步保存以下记录，避免半年后难以追溯：
- 每次 prompt 修改的 diff 和原因 → `docs/prompt_changelog.md`
- Benchmark 的完整输入/输出 → `docs/benchmark/`
- 失败案例 → `docs/failure_cases.md`
- 关键设计决策和取舍理由

这些素材在撰写 Method / Discussion / Limitations 时会直接可用。

---

## 决策门总览

```
Phase 0 (Mini Benchmark)
  ↓
  条件：KC acc ≥ 80% AND KC−RAG ≥ 10%
  ├─ 通过 → Phase 1 (NSCA Pilot)
  └─ 未通过 → 修复后重试或停止

NSCA Pilot (2-3 节)
  ↓
  条件：新增 schema ≤ 1, prompt 修改 ≤ 3, validation ≥ 70%
  ├─ 通过 → Phase 1 全书 + Phase 2 完整 Benchmark
  └─ 未通过 → 记录失败原因，调整后在另一本书重试

完整 Benchmark
  ↓
  条件：KC acc ≥ 85% AND KC−RAG ≥ 10%
  ├─ 通过 → Phase 3: Validation & Launch
  └─ 未通过 → 排查问题，暂不发布

Phase 3 外部验证 (3-5 人)
  ↓
  条件：≥ 80% 的人 10 分钟内能跑通 demo
  ├─ 通过 → 发布 Launch
  └─ 未通过 → 修复 top 3 问题后重试
```
