---
name: discover-cross-domain-opportunities-zh
description: 面向 Claude Code 或 Codex 的端到端跨领域研究机会发现 skill。适用于从目标领域论文中抽取有证据支持的开放问题，分析问题尚未解决的原因，检索其他领域可迁移的方法，执行新颖性检查，设计具体应用方案，评估可行性，并生成包含研究假设和最小实验的报告。这是中文用户入口；不要让用户手动串联规划、抽取、迁移或报告流程。
---

# 跨领域研究机会发现

## 触发方式

`/discover-cross-domain-opportunities-zh <目标领域>`

这是中文用户的唯一入口。用户只需要给出目标研究领域，agent 必须在内部完成所有阶段，不要让用户选择或串联子流程。

## 目标

本 skill 的目标不是生成泛泛综述，而是发现可验证、可落地的研究机会：

- 从目标领域论文中抽取开放问题，重点关注 limitations、future work、open challenges、benchmark gaps、负结果和部署约束。
- 解释现有方法为什么仍未解决这些问题。
- 将问题抽象成可跨领域迁移的机制。
- 检索其他领域已经有效、但尚未直接应用到目标领域的方法。
- 检查是否已有直接应用或机制等价方法。
- 生成具体应用方案、研究假设、最小实验、可行性评估和最终报告。

## 工作流

### 阶段 0：记录运行元数据

检索前先获取当前年月：

- Windows PowerShell：`Get-Date -Format "yyyy-MM"`
- POSIX shell：`date +%Y-%m`

将结果记为 `{current_year_month}`，写入 `outline.yaml`、JSON 输出和 `report.md`。

同时用检索方式加载迁移模式库，避免把整份 YAML 放入上下文：

1. 如果用户提供了模式库路径，优先读取用户指定的 YAML。
2. 否则读取当前仓库根目录的 `transfer-patterns.yaml`。
3. 不要直接全文读取模式库。先从当前 gap 的 `problem_statement`、`why_unsolved`、`failure_modes`、`evaluation_gap`、`candidate_source_domains` 和目标领域关键词中提取 5-12 个检索关键词。
4. 优先用 `python scripts/select_patterns.py transfer-patterns.yaml <keyword1> <keyword2> ... --max 5` 选择命中块；如果脚本不可用，再用 `rg -n -i "<keyword1>|<keyword2>|..." transfer-patterns.yaml` 或 PowerShell `Select-String` 搜索 `# @pattern` 索引行。
5. 每个索引行的格式为 `# @pattern id=<id> keywords=<keywords>`。只读取命中 id 对应的 YAML 块：从该 `# @pattern` 行开始，到下一个 `# @pattern` 行之前结束。
6. 若没有命中，用 `python scripts/select_patterns.py transfer-patterns.yaml --index` 或 grep 只读取全部 `# @pattern` 索引行，不要读取全部 pattern 正文；根据索引关键词选择最可能相关的 1-3 个块。
7. 如果存在多个模式库，按 `id` 去重后合并命中的块。
8. 如果模式库不存在，不要中断任务，但要在报告中说明“未加载动态迁移模式库”。

每个模式只需要包含 `id`、`transfer`、`use_when`、`queries`、`apply` 和 `risks`。这些模式不是最终结论，只是用于生成候选迁移假设的启发式种子。

### 阶段 1：建立项目 outline

创建或更新 `{target_domain}/outline.yaml` 和 `{target_domain}/fields.yaml`。

`outline.yaml` 至少包含：

```yaml
topic: "<target_domain>"
created_at_month: "<current_year_month>"
scope:
  target_domain: "<目标领域>"
  time_range: "近五年，必要时追溯经典论文"
  include_preprints: true
papers:
  - title: "<论文标题>"
    year: 2025
    venue: "<venue 或 arXiv>"
    url: "<URL 或 DOI>"
    reason: "<选择原因>"
research_questions:
  - id: "RQ1"
    problem: "<有论文证据支持的开放问题>"
    evidence_type: "limitation"
    source_papers: ["<论文标题>"]
    why_unsolved: "<现有方法为什么仍未解决>"
candidate_source_domains:
  - domain: "<外部领域>"
    analogous_problem: "<外部领域中的相似问题>"
    search_keywords: ["<方法关键词>", "<问题关键词>"]
search_policy:
  search_depth: "deep"
  target_domain_layers:
    - "survey/review/taxonomy/roadmap"
    - "benchmark/dataset/challenge/leaderboard"
    - "limitation/failure/error/robustness/OOD"
    - "SOTA method/framework/toolkit/pipeline/system"
    - "data construction/curation/annotation/synthetic data"
    - "real-world/deployment/efficiency/cost/human-in-the-loop"
  expansion_rings:
    R0: "用户给定的目标领域关键词"
    R1: "核心论文、survey、benchmark、dataset"
    R2: "R1 的引用论文和被引论文"
    R3: "相邻任务领域"
    R4: "抽象问题对应的外部领域"
    R5: "代码、数据集、工具、benchmark 页面、工业系统"
  search_budget:
    target_domain_queries: 20
    source_domain_queries: 40
    novelty_check_queries_per_method: 8
    citation_snowball_depth: 2
    max_candidate_methods_per_problem: 8
    max_final_recommendations: 5
  non_paper_sources:
    - "Papers with Code"
    - "Hugging Face datasets/models"
    - "GitHub"
    - "PyPI/npm/conda when relevant"
    - "official benchmark pages"
execution:
  output_dir: "results"
  transfer_output_dir: "results/transfer_candidates"
  batch_size: 3
```

`fields.yaml` 至少覆盖：

- 论文证据：`problem_statement`、`evidence_from_papers`、`evidence_type`、`why_unsolved`
- 目标领域已有尝试：`current_attempts`、`failure_modes`、`evaluation_gap`
- 跨领域检索：`problem_abstraction`、`external_method`、`source_domain`、`not_yet_applied_evidence`、`possible_existing_equivalent`、`novelty_check`
- 应用方案：`application_plan`、`target_component`、`mechanism_mapping`、`implementation_steps`、`required_signals_or_data`、`baseline_to_modify`、`success_metrics`
- 验证设计：`hypothesis`、`minimal_experiment`、`engineering_difficulty`、`data_difficulty`、`dataset_or_benchmark`、`risk_or_limitation`、`evidence_level`、`feasibility_review`、`top_conference_innovation_review`

### 阶段 2：抽取有论文证据的问题缺口

对每个 `research_question` 生成 `{output_dir}/{rq_slug}.json`。如果文件已存在，则跳过，以支持断点续跑。

证据规则：

- 没有论文或 benchmark 证据时，不要输出为 confirmed problem。
- 单篇论文证据必须标记为 `weak_evidence`。
- 优先选择多篇论文或 benchmark 反复出现的问题。
- 区分作者明确提出的问题和 agent 推断的问题。
- 不确定字段写 `[uncertain]`，并加入顶层 `uncertain`。

单个问题 JSON 结构：

```json
{
  "id": "RQ1",
  "created_at_month": "2026-06",
  "problem_statement": "清晰的问题表述",
  "target_domain": "目标领域",
  "paper_evidence": [
    {
      "paper": "论文标题",
      "venue_year": "NeurIPS 2025",
      "evidence_type": "future_work",
      "evidence_summary": "限制或未来工作摘要",
      "url": "https://..."
    }
  ],
  "current_attempts": [
    {
      "method": "目标领域已有方法",
      "limitation": "为什么仍然不足"
    }
  ],
  "why_unsolved": "未解决原因",
  "failure_modes": ["失败模式"],
  "evaluation_gap": "现有评测无法覆盖的缺口",
  "search_expansion": {
    "search_depth": "deep",
    "target_domain_layers_checked": ["survey", "benchmark", "failure_analysis"],
    "citation_snowball_used": true,
    "non_paper_sources_checked": ["official benchmark pages"],
    "missed_risk": "low/medium/high"
  },
  "candidate_source_domains": [
    {
      "domain": "外部领域",
      "analogous_problem": "相似问题",
      "search_keywords": ["关键词"]
    }
  ],
  "uncertain": []
}
```

当 `fields.yaml` 存在时，用 `validate_json.py` 验证字段覆盖。

### 阶段 3：寻找跨领域迁移方法

对每个已抽取 gap：

1. 先构造 `problem_abstraction`，再做外部领域检索。
2. 将 `problem_abstraction` 与已检索加载的迁移模式块匹配，优先尝试 `use_when` 与当前 gap 相符的模式。
3. 不只依赖初始 `candidate_source_domains`，必须结合模式库中的 `transfer` 自动扩展外部领域和同领域相邻环节。
4. 按 `R0` 到 `R5` 搜索环扩展检索。
5. 对每个匹配模式，用其 `queries` 生成检索式；将 `{target_domain}`、`{target_task}`、`{target_problem}`、`{method}` 等占位符替换为当前任务内容。
6. 记录外部方法及其来源证据。
7. 执行双向 novelty check，并复用模式库中的 `queries` 生成反向和等价机制查询。
8. 用模式库中的 `apply` 作为应用方案草稿，但必须结合目标领域改写为具体可落地的 application plan。
9. 把模式库中的 `risks` 写入风险检查，不要把模式匹配直接当成创新点。
10. 优先保留工程难度为 `low`、`medium`、`medium-high` 的机会。

问题抽象结构：

```yaml
problem_abstraction:
  surface_problem: "<目标领域原始表述>"
  abstract_problem: "<跨领域通用问题>"
  mechanism_keywords:
    - "<机制关键词>"
  source_domain_seeds:
    - "<外部领域>"
```

novelty check 查询必须包含：

```text
"<method name>" "<target domain>"
"<method synonym>" "<target task>"
"<core algorithm>" "<target benchmark>"
"<target problem>" "<method family>"
"<target domain>" "<abstract mechanism>"
"<target domain>" "hard example mining"
"<target domain>" "curriculum learning"
"<target domain>" "data filtering"
"<target domain>" "calibration"
```

应用状态：

- `already_applied`：已找到目标领域直接应用。
- `possible_existing_equivalent`：找到目标领域机制等价方法。
- `candidate_gap`：未发现直接应用证据。
- `unclear`：证据不足。

将迁移结果写入 `{transfer_output_dir}/{rq_slug}_transfer.json`。

每个候选方法必须包含：

```json
{
  "transfer_pattern_id": "evaluation-to-training",
  "transfer_pattern": "evaluation -> training: 把评价准则转成训练监督或奖励信号",
  "method": "外部方法",
  "source_domain": "来源领域",
  "source_evidence": ["url"],
  "application_status": "candidate_gap",
  "not_yet_applied_evidence": "在已检查来源中未发现目标领域直接应用；这不是绝对断言。",
  "possible_existing_equivalent": "[uncertain]",
  "application_plan": {
    "target_component": "应落到目标系统的哪个模块",
    "mechanism_mapping": "源领域机制如何映射到目标问题",
    "implementation_steps": ["步骤1", "步骤2", "步骤3"],
    "required_signals_or_data": ["需要的信号或数据"],
    "baseline_to_modify": "建议改造的目标领域 baseline",
    "success_metrics": ["验证指标"]
  },
  "hypothesis": "可验证研究假设",
  "minimal_experiment": "最小验证实验",
  "engineering_difficulty": "low/medium/medium-high/high，并说明原因",
  "data_difficulty": "low/medium/high，并说明原因",
  "dataset_or_benchmark": "数据集或 benchmark",
  "risk_or_limitation": "风险或反例",
  "evidence_level": "A/B/C/D"
}
```

### 阶段 4：可行性与顶会创新性评估

为每个 `candidate_gap` 添加 `feasibility_review`：

```json
{
  "feasibility": "high/medium/low",
  "minimum_viable_path": "最先能测试什么",
  "blocking_dependencies": ["阻塞依赖"],
  "validation_risks": ["验证风险"],
  "fallback_plan": "更小或离线的降级验证方案",
  "top_conference_innovation_review": {
    "target_venues": ["CVPR/ICCV/ECCV/NeurIPS/ICML/ICLR/ACL/EMNLP/KDD/SIGIR/WWW/AAAI/IJCAI 中最相关的 2-4 个"],
    "nearest_prior_work": [
      {
        "paper": "最接近的目标领域或源领域论文",
        "venue_year": "会议/年份",
        "overlap": "与候选方案重合之处",
        "remaining_delta": "候选方案相比该论文还剩什么实质差异"
      }
    ],
    "claimed_paper_contribution": "若投稿顶级计算机会议，论文主贡献应如何一句话表述",
    "innovation_type": "new_problem/new_method/new_benchmark/new_theory/new_system_or_dataset_with_methodological_insight",
    "is_more_than_engineering_integration": true,
    "top_conference_bar": "strong/medium/weak",
    "why_meets_or_misses_bar": "是否满足顶会论文创新性要求；必须明确说明差距、非平凡性、通用性和实验说服力",
    "must_validate_for_publication": [
      "与最近邻工作的清晰差异",
      "非平凡方法或机制，而不只是把已有模块拼接到目标领域",
      "能支撑顶会审稿的强 baseline、ablation、泛化或失败分析",
      "对多个数据集/任务/场景有可迁移价值，或提出高质量 benchmark/数据构造机制"
    ]
  },
  "review_verdict": "go/revise/hold"
}
```

判断标准：

- `go`：依赖可获得，最小实验清楚，指标可信，且 `top_conference_bar` 至少为 `medium`；需要能解释为什么该方案可能满足顶级计算机会议论文的创新性要求。
- `revise`：方向有价值，但顶会创新性证据不足、最近邻工作重合过高、贡献表述不清，或需要缩小范围、替换数据、调整 baseline、补充 ablation/泛化实验、重新设计评估。
- `hold`：关键依赖不可获得，当前没有能验证核心假设的最小实验，或判断为只属于工程集成/常规应用，难以满足顶级计算机会议论文发表的创新性要求。

顶会创新性评估规则：

- 可行性评估的重点不是“能否实现”，而是“最小实验能否验证该方向具有顶级计算机会议论文级别的创新性”。工程可做但论文创新性弱的候选必须标记为 `revise` 或 `hold`。
- 必须显式列出 2-5 篇最近邻 prior work，并说明候选方案和它们的实质差异。若差异只是换数据集、换 backbone、换 prompt、增加常规模块或简单系统拼接，不要判为 `go`。
- 必须给出可被审稿人接受的论文主贡献句。如果无法用一句话说明非平凡贡献，应标记为 `revise`。
- 必须设计能验证创新性的实验，而不只是验证性能提升；优先包括强 baseline、消融实验、泛化到不同数据集/领域、失败模式分析、成本/鲁棒性分析和统计显著性。
- 如果候选方向主要是 benchmark 或 dataset，必须说明数据构造机制、标注质量控制、任务定义和 evaluation protocol 为什么本身具有研究贡献，而不仅是收集更多数据。

### 阶段 5：生成最终报告

生成 `{target_domain}/report.md`：

报告语言和术语限制：

- 报告中的专有名词、方法名、指标名、数据集名、benchmark 名称、模型名、算法名和论文简称首次出现时，必须写成 `English term(中文释义)` 的形式，例如 `Rubrics as Rewards(作为奖励的评分规程)`、`HealthBench(健康评测基准)`；若没有自然中文释义，括号内给出简短中文解释。后续可使用英文原词或英文简称。

```text
# {topic} 研究机会报告

生成年月：{current_year_month}

## 1. 领域现状
## 2. 有论文证据的开放问题
## 3. 问题聚类
## 4. 可迁移的跨领域方法
## 5. 尚未应用证据
## 6. 搜索覆盖与遗漏风险
## 7. 可行性与顶会创新性 Review
## 8. 研究假设排序
## 9. 最小实验
## 10. 风险、反例与排除项
## 11. 参考文献
```

每个机会必须包含：

- 问题
- 论文证据
- 为什么仍未解决
- 外部方法
- 迁移理由
- 应用方案
- novelty check 结果
- 可能的等价方法
- 可行性与顶会创新性 review
- 最小实验
- 工程和数据难度
- 预期贡献
- 风险
- 证据等级

## 搜索深度

默认使用 `deep`。

- `light`：快速扫描，只查核心 survey/benchmark 和少量 novelty query。
- `standard`：覆盖核心论文、benchmark、limitations 和候选源领域。
- `deep`：默认；加入 citation snowball、相邻任务、抽象问题检索、代码/数据/工具来源和双向 novelty check。
- `exhaustive`：加入专利、工业报告、更深 citation snowball 和更多反向等价机制检查。

## 停止条件

遇到以下情况时停止或降级候选：

- 连续 10 条结果没有新方法族或反证。
- 两个独立来源确认该方法已在目标领域直接使用。
- 找不到可信 baseline、数据或评估指标。
- 工程难度为 `high`，且不能降到 `medium-high` 的最小实验。

## 最终交付

生成：

```text
{target_domain}/outline.yaml
{target_domain}/fields.yaml
{target_domain}/results/*.json
{target_domain}/results/transfer_candidates/*.json
{target_domain}/report.md
```

最后给出最值得优先尝试的 3-5 个研究假设，并说明排序理由。
