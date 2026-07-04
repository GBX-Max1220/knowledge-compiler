# Benchmark Protocol — Phase 0 Mini Benchmark

> **目标：** 用最小成本验证"Knowledge Compiler 是否优于 PDF+RAG"这个故事是否成立。
> **范围：** ACSM 12th Ed., Chapters 1–3
> **样本量：** 6-10 题（详见下方补救规则）

---

## 条件

| ID | Condition | Description |
|----|-----------|-------------|
| A | **Raw LLM** | 直接问 GPT-4o-mini，无 context |
| B | **RAG on PDF** | sentence-transformers `all-MiniLM-L6-v2` 检索 top-3 chunks + GPT-4o-mini 回答 |
| C | **Knowledge Compiler** | 74 个 validated objects，`knowledge_compiler.Skill.get()` 直接查找 |

### Baseline 说明

当前 RAG baseline 使用轻量级 embedding（`all-MiniLM-L6-v2`），CPU 可运行。
后续 Phase 2 完整 Benchmark 会补充更强的 baseline（BGE / OpenAI embedding）。

---

## 题目设计要求

### 类型分布（防止 sampling bias）

| Type | Minimum | Source |
|------|---------|--------|
| Concept (definition) | ≥2 | Ch1-3 |
| Threshold (range/value) | ≥2 | Ch1-3 |
| Procedure (steps) | ≥2 | Ch2-3 |
| Warning / Recommendation | ≥2 | Ch1-2 |

### 防 Evaluation Leakage

**Question 不能直接来自 object 的 `canonical_name` 或标题。**

✅ 正确示例：
> "A 55-year-old man with hypertension wants to start jogging. What should he do before beginning?"
> → 对应对象：`procedure.acsm_screening_algorithm`, `recommendation.medical_clearance_exercise`

❌ 错误示例：
> "What is the ACSM screening algorithm for preparticipation evaluation?"
> → 问题直接用了 object 标题，evaluation leakage

---

## 评分标准

每道题对每个条件独立评分：

| Metric | Definition | Scoring |
|--------|-----------|---------|
| **Accuracy** | 回答是否与教材一致 | 0 (wrong) / 0.5 (partial) / 1 (correct) |
| **Citation Correctness** | 引用的章节/页码是否真实存在 | 0 (no/fake citation) / 1 (correct citation) |
| **Faithfulness** | 回答是否有 hallucination（编造不在原文中的信息） | 0 (有 hallucination) / 1 (无 hallucination) |

---

## 决策门

```
继续执行 Phase 1 的条件（需同时满足）：
  KC accuracy ≥ 80%
  KC accuracy − RAG accuracy ≥ 10 个百分点

黄色预警（可以继续但需记录）：
  5% ≤ KC − RAG < 10%

红色停止（先不进入 Phase 1）：
  KC accuracy < 80%
  KC − RAG < 5%
```

### 小样本补救规则

Phase 0 仅 6-10 题，一道题可改变 10-17 个百分点。

- 如果所有指标在阈值临界区（±5pp 内）→ 扩展到 **15-20 题**再判断（多花 0.5 天）
- 如果远超阈值或远低于阈值 → 6-10 题足够做决策
- 无论结果如何，记录中必须标注样本量局限

---

## 输出格式

每个条件的结果记录在 `docs/benchmark/results-phase0.json`：

```json
{
  "condition": "raw_llm | rag_minilm | knowledge_compiler",
  "timestamp": "...",
  "model": "gpt-4o-mini",
  "questions": [
    {
      "id": "q01",
      "question": "...",
      "expected_answer": "...",
      "actual_answer": "...",
      "accuracy": 0.0,
      "citation_correctness": 0,
      "faithfulness": 1,
      "notes": "..."
    }
  ],
  "summary": {
    "accuracy": 0.0,
    "citation_correctness": 0.0,
    "faithfulness": 0.0
  }
}
```

---

## 局限性

**Phase 0 验证的是：** "在当前 ACSM Ch1-3 的数据上，我们有没有资格讲这个故事。"
**Phase 0 不能验证的是：** "KC 是否在任意教材上都优于 RAG。"

如果 Phase 0 数字好，只能确认 ACSM Ch1-3 上成立，**不能**自动泛化到 NSCA 或其他书。
如果 Phase 0 数字差，NSCA 大概率也不会更好。

**阈值来源说明：** 以上 thresholds 是 engineering targets，非统计推导得出。Phase 2 会在此基础上做统计检验。
