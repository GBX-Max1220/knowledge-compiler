# Knowledge Compiler — 下一阶段计划

> **当前状态：** v0.1 已完成（ACSM 12th Ed. Ch1-3, 74 个 validated objects, Skill API, README 与代码一致）
> **方向调整：** 先做开源影响力，暂不追求论文发表

---

## 核心判断与依据

### 判断 1：下一步不是继续抛光仓库

README、pyproject.toml、LICENSE、CONTRIBUTING、Skill API 都已到位。继续调 README 措辞、改目录结构的 ROI 已经很低。下一阶段的杠杆在仓库之外——**证明这个 framework 是真的 framework，不是单点 demo。**

### 判断 2：跨领域泛化 > 评估实验（开源优先的逻辑）

如果是论文导向，应该先跑评估实验（Raw LLM vs RAG vs KC 的对比数据）。但开源影响力的核心驱动因素是：

- **可信度：** "它能在我的领域用吗？" → 第二本书直接回答这个问题
- **可演示性：** 两本教材的 objects 比一本更有说服力
- **信号强度：** 新增一本完全不同来源的教材是一个可见的里程碑（v0.2 release）
- **社区门槛：** 评估数据对论文有用，但对路人来说"看到一个数字对比表"不如"看到第二个成功案例"有冲击力

### 判断 3：NSCA 是最佳第二本书

- 同属运动科学领域，但与 ACSM 有足够的差异性（ACSM 偏向运动医学/健康人群筛查，NSCA 偏向力量训练/运动表现）
- schema 类型（Concept / Threshold / Procedure / Recommendation / Warning / Contraindication / Formula / TableRow）预期大部分兼容
- 如果 NSCA 不需要改 schema 就能跑通 → **Knowledge Compiler 的框架性真正成立**
- 如果 NSCA 暴露了 schema 缺口 → 正好发现"下一个需要泛化的维度"

### 判断 4：评估实验往后放，但不取消

评估数据（Raw LLM vs RAG vs KC 的 faithfulness / accuracy 对比）依然有价值，但更适合放在 v0.2（NSCA）完成之后：

- 届时有两本书的 objects，评估可以跨书做，结论更强
- 评估结果可以作为 README 里的 benchmark 板块（公开数据，不写论文）
- 如果未来决定投稿，数据已经就绪

---

## Phase 1：跨领域泛化 — NSCA 教材（核心里程碑）

**目标：** 将 NSCA Essentials of Strength Training and Conditioning 跑通完整管线，验证 schema 和 prompts 的通用性。

### 子步骤

1. **获取 NSCA PDF** — 放入 `books/nsca-essentials/source/`
2. **生成 manifest** — 运行 `python scripts/gen_manifest.py` 生成章节结构
3. **Chunk** — 将 PDF 拆分为章节 markdown 文件
4. **Extraction** — 用 AI provider（Reasonix CLI 或 OpenAI）对每个 chunk 做标注
5. **Normalization** — 将 extraction 结果转为标准化的 schema 对象
6. **Decompose** — 将 normalized 输出拆为每个对象的独立 YAML 文件
7. **Validate** — 跑 5 层 validation
8. **整合** — 更新 `registry.yaml`、`index.yaml`、README 添加 "Supported Books"

### 关键检查点

- 现有 8 个 schema 类型是否足够？（Concept, Threshold, Procedure, Recommendation, Warning, Contraindication, Formula, TableRow）
- prompts（02_extract.md, 03_object_generate.md）是否需要改动？
- 是否需要新增 schema 类型？
- 是否需要新增 ontology predicate？

### 产出物

- ✅ 第二个 validated 书籍数据集
- ✅ `README` 新增 "Supported Books" 板块
- ✅ v0.2 release tag
- ✅ 跨领域泛化的结论：兼容 or 需调整

### 谁做

| 工作 | 执行者 |
|------|--------|
| PDF → extraction → normalization（需 AI API） | 你（CLI） |
| 整合、验证、README 更新、release | 我（Desktop） |

---

## Phase 2：优化开发者体验

**目标：** 降低新用户的上手门槛，从 "clone 后能跑" 到 "clone 后 2 分钟内理解并能用"。

### 子步骤

1. **Schema 示例目录** — 在 `docs/examples/` 下放每个类型的真实 YAML 示例（从 ACSM objects 中提取）：
   - `concept.exercise.yaml` → 展示 is_a 关系、attributes、purpose
   - `threshold.met.moderate.yaml` → 展示 range、numerical_value、population
   - `procedure.one_rm_testing.yaml` → 展示 steps、inputs、outputs
   - `warning.signs_symptoms_cv_disease.yaml` → 展示 signs、action
   - `recommendation.medical_clearance.yaml` → 展示 dosage、population
2. **CLI 入口** — 给 `knowledge_compiler/` 包加命令行入口，支持 `knowledge-compiler validate acsm12` 等快捷命令
3. **安装验证** — 确保 `pip install -e .` 正常安装，demo.py 能直接 import

### 谁做

| 工作 | 执行者 |
|------|--------|
| 以上全部 | 我（Desktop） |

---

## Phase 3：公开 Benchmark + README 数据板块

**目标：** 建立一个公开可验证的 benchmark，直接放在 README 里作为技术可信度的锚点。

### 子步骤

1. **设计 25 题 evaluation set**（跨 ACSM + NSCA 两本书）
2. **建立三组对比 baseline**：
   - Raw LLM（直接问 GPT-4o，无 context）
   - RAG on PDF（chunk + sentence-transformers 检索 + GPT-4o 回答）
   - Knowledge Compiler（对象查找 + 确定性回答）
3. **跑对比**，记录 accuracy / citation correctness / faithfulness
4. **结果写入 README** 作为 "Performance" 板块

### 谁做

| 工作 | 执行者 |
|------|--------|
| evaluation set 设计 + 实验 + 数据分析 | 你（CLI） |
| 结果整合到 README | 我（Desktop） |

---

## Phase 4：社区建设

**目标：** 让别人能贡献、愿意贡献。

### 子步骤

1. **GitHub Issue 模板** — bug report + feature request
2. **"How to add a new book" 指南** — 在 `docs/` 中
3. **PR 模板**
4. **第一个外部 contributor 的 onboarding 文档**

### 谁做

| 工作 | 执行者 |
|------|--------|
| 以上全部 | 我（Desktop） |

---

## 时间线（预估）

| Phase | 内容 | 预估 | 依赖 |
|-------|------|------|------|
| 1 | NSCA 管道运行 | 3-7 天 | 有 NSCA PDF |
| 2 | 开发者体验优化 | 2-3 天 | 可在 Phase 1 并行开始 |
| 3 | Benchmark | 3-5 天 | Phase 1 完成后（可跨两本书） |
| 4 | 社区建设 | 1-2 天 | 可在 Phase 2 后开始 |

---

## 需要你确认的事项

1. **NSCA 教材的 PDF 你有吗？** — 这是 Phase 1 的前提
2. **Phase 1 的 AI 调用成本** — extraction + normalization 两本书大约需要 ~$10-20 的 API 费用（如果用 OpenAI）或 Reasonix CLI 额度
3. **v0.1 → v0.2 的版本号升级** — NSCA 完成后是否要打 v0.2 tag？

---

*以上计划由 Reasonix Desktop 生成，供 ChatGPT 和 ClaudeCode 审核。*
