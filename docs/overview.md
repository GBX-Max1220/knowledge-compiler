# Knowledge Compiler — 项目概览

> **将教科书编译为可验证、可组合、可查询的知识对象。**
> GitHub: https://github.com/GBX-Max1220/knowledge-compiler

---

## 目录结构

```
knowledge-compiler/
├── knowledge_compiler/        # Python 包 (Skill API)
│   ├── __init__.py
│   └── skill.py               # Skill 类：get() / resolve() / list_objects()
│
├── books/                     # 教材数据
│   ├── acsm12/                # ACSM 12th Edition
│   │   ├── source/            # PDF 源文件
│   │   ├── manifest.yaml      # 章节结构
│   │   ├── chunks/            # 按节分割的文本 (378 文件)
│   │   ├── extraction/        # AI 标注结果
│   │   ├── normalized/        # 标准化 YAML 对象
│   │   ├── objects/           # 独立对象文件 (13 类型)
│   │   ├── registry.yaml      # 名称 → ID 映射
│   │   └── validation/        # 验证报告
│   │
│   └── nsca-cscs/             # NSCA-CSCS 5th Edition
│       └── ...                # (同上结构)
│
├── schema/                    # 类型定义 (8 个 YAML)
│   ├── concept.yaml
│   ├── threshold.yaml
│   ├── procedure.yaml
│   ├── recommendation.yaml
│   ├── warning.yaml
│   ├── contraindication.yaml
│   ├── formula.yaml
│   └── tablerow.yaml
│
├── prompts/                   # AI Prompt 模板 (6 个)
│   ├── 01_chunk.md
│   ├── 02_extract.md
│   ├── 03_object_generate.md
│   ├── 04_validate.md
│   ├── 05_export.md
│   └── CHANGELOG.md
│
├── scripts/                   # 自动化脚本
│   ├── batch_process.py       # 管线编排
│   ├── decompose_objects.py   # 归一化 → 独立对象
│   ├── validate.py            # 5 层自动化验证
│   ├── gen_manifest.py        # 生成 manifest
│   ├── run_queue.py           # AI 队列处理
│   ├── rag_baseline.py        # RAG 基线 (all-MiniLM-L6-v2)
│   ├── run_benchmark.py       # 三条件 Benchmark 运行器
│   └── run_benchmark_25.py    # 25 题跨书 Benchmark
│
├── compiler/                  # 编译器核心
│   ├── cli.py                 # CLI 入口
│   ├── queue.py               # 任务队列 (retry/resume)
│   └── providers/             # LLM Provider 抽象
│       ├── openai.py          # OpenAI / DeepSeek / 兼容 API
│       └── reasonix.py        # Reasonix CLI
│
├── docs/                      # 文档
│   ├── pipeline.md            # 管线流程
│   ├── ontology.md            # 本体规范
│   ├── schema.md              # Schema 说明
│   ├── failure_cases.md       # 失败案例记录
│   ├── overview.md            # 本文件
│   └── benchmark/
│       ├── README.md          # Benchmark 协议
│       ├── benchmark-25-questions.md
│       ├── error-analysis.md
│       └── results-*.json     # 三条件对比结果
│
├── pyproject.toml             # Python 包配置
├── LICENSE                    # MIT
├── CONTRIBUTING.md            # 贡献指南
└── README.md                  # 项目 README
```

---

## 支持教材

| 教材 | 版本 | 章节 | 对象 | 类型数 |
|------|:----:|:----:|:----:|:------:|
| ACSM Guidelines for Exercise Testing and Prescription | 12th | 12 章 | **707** | 13 |
| Essentials of Strength Training and Conditioning (NSCA) | 5th | 26 章 | **1598** | 13 |
| **总计** | | **38 章** | **2305** | |

---

## 对象类型

| 类型 | ACSM | NSCA | 合计 | 说明 |
|------|:----:|:----:|:----:|------|
| Concept | 142 | 920 | 1062 | 定义、术语、概念 |
| Threshold | 206 | 114 | 320 | 阈值、分类边界 |
| Recommendation | 139 | 174 | 313 | 指南、建议 |
| TableRow | 127 | 124 | 251 | 表格行数据 |
| Procedure | 29 | 98 | 127 | 流程、步骤 |
| Warning | 34 | 46 | 80 | 安全警告 |
| Formula | 5 | 24 | 29 | 计算公式 |
| Evidence | 2 | 82 | 84 | 研究证据 |
| Figure | 16 | 7 | 23 | 流程图、示意图 |
| Contraindication | 4 | 1 | 5 | 禁忌症 |
| DecisionRule | 1 | 2 | 3 | 决策规则 |
| RiskFactor | 1 | 3 | 4 | 风险因素 |
| Table | 2 | 3 | 5 | 表格元数据 |
| **合计** | **707** | **1598** | **2305** | |

---

## Validation 状态

两本书均通过 **5 层验证**，0 结构错误：

| 层 | 检查内容 | ACSM | NSCA |
|:--:|---------|:----:|:----:|
| 1 | YAML 语法、必需字段 | ✅ PASS | ✅ PASS |
| 2 | 类型特化字段完整性 | ✅ 仅 warning | ✅ 仅 warning |
| 3 | 关系目标可解析、谓词合法 | ✅ PASS | ✅ PASS |
| 4 | 无重复 ID/名称 | ✅ PASS | ✅ PASS |
| 5 | 语义质量（空定义等，建议性） | ⚠ 895 | ⚠ 789 |

> 注意：Layer 2 和 Layer 5 的 warning/issue 不影响整体 PASS 状态。Layer 2 的 warning 主要是 semantic_type 不在白名单（新类型），Layer 5 的 issue 主要是少量概念的定义为空。

---

## Benchmark 结果

### 10 题 Phase 0

| 条件 | Accuracy |
|------|:--------:|
| **Knowledge Compiler** | **100%** |
| RAG on PDF (MiniLM) | 38% |
| Raw LLM (DeepSeek) | 44% |

### 25 题跨书 Benchmark

| 条件 | 25 题 | 说明 |
|------|:-----:|------|
| **Knowledge Compiler** | **25/25** | 对象直接查询 |
| RAG on PDF | 25/25 | 多数"信息不足"（仅 ACSM 语料） |
| Raw LLM (DeepSeek) | 25/25 | 回答完整 |

---

## 使用方式

### 安装

```bash
git clone https://github.com/GBX-Max1220/knowledge-compiler.git
cd knowledge-compiler
pip install -e .
```

### 快速开始

```python
from knowledge_compiler import Skill

# 加载 ACSM
skill = Skill("books/acsm12")
obj = skill.get("threshold.bmi_classification")
print(obj["range"])
# → "<18.5 Underweight, 18.5-24.9 Normal..."
```

### 运行验证

```bash
python scripts/validate.py --book acsm12
python scripts/validate.py --book nsca-cscs
```

### 运行 Benchmark

```bash
python scripts/run_benchmark_25.py --condition kc     # KC 条件
python scripts/run_benchmark_25.py --condition rag    # RAG 条件 (需 API key)
python scripts/run_benchmark_25.py --condition raw    # Raw LLM (需 API key)
```

---

## 技术栈

| 组件 | 技术 |
|------|------|
| 编程语言 | Python 3.10+ |
| 数据格式 | YAML (对象存储) |
| 包管理 | pyproject.toml / setuptools |
| AI Provider | DeepSeek / OpenAI / Reasonix CLI |
| 向量检索 | sentence-transformers (all-MiniLM-L6-v2) |
| PDF 解析 | PyPDF2 |
| 许可证 | MIT |

---

## 管线流程

```
PDF → Chunk → Extract → Generate → Decompose → Validate → Skill
│       │         │          │          │          │
│       │    AI prompt   AI prompt  机械拆分   5层自动化
│  按 manifest    02_extract  03_object_   per-object    1-5
│  提取每节文本             generate    YAML
```

---

## API 成本

使用 DeepSeek API，管线成本极低：

| 任务 | 成本 |
|------|:----:|
| 单节 Extraction | ~$0.0007 |
| 单节 Generation | ~$0.0013 |
| ACSM 全书 (378 节) | ~$0.75 |
| NSCA 全书 (169 节) | ~$0.50 |
| 25 题 Benchmark | ~$0.02 |

---

## 相关资源

- [README.md](../README.md) — 项目介绍
- [Pipeline 详情](pipeline.md) — 管线各阶段说明
- [Ontology 规范](ontology.md) — 本体系统
- [Schema 定义](schema.md) — 类型系统
- [Benchmark 协议](benchmark/README.md) — 评估方法
- [贡献指南](../CONTRIBUTING.md) — 如何参与
