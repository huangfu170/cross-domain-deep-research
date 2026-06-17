# cross-domain-deep-research

Language: [中文](#中文) | [English](#english)

## 中文

本项目为 Claude Code 或 Codex 提供跨领域 idea 发现 skill。仓库根目录下直接提供两份 skill：

- `discover-cross-domain-opportunities-zh`：中文说明和中文输出结构。
- `discover-cross-domain-opportunities-en`：英文说明和英文输出结构。
- `discover-transfer-patterns-from-pdf-zh`：从中文用户传入的 PDF 中发现 `transfer-patterns.yaml` 尚未收录的迁移套路。
- `discover-transfer-patterns-from-pdf-en`：从英文用户传入的 PDF 中发现 `transfer-patterns.yaml` 尚未收录的迁移套路。

用户不需要自己建立 workflow，也不需要手动串联多个阶段。选择对应语言的 skill 后，只需要给出目标研究领域，agent 会自动完成从论文问题抽取、跨领域方法检索、novelty check、应用方案设计、可行性 review 到最终报告生成的完整流程。

### 使用方式

```text
/discover-cross-domain-opportunities-zh <目标领域>
```

或：

```text
/discover-cross-domain-opportunities-en <target_domain>
```

如果希望从一篇 PDF 反向维护迁移模式库，可使用：

```text
/discover-transfer-patterns-from-pdf-zh <pdf_path>
```

或：

```text
/discover-transfer-patterns-from-pdf-en <pdf_path>
```

### 动态迁移模式库

仓库根目录的 `transfer-patterns.yaml` 维护一组可复用的“领域迁移套路”。skill 运行时会动态加载这个文件，并用其中的模式扩展问题抽象、检索式、novelty check、应用方案草稿和风险检查。

为避免把整份 YAML 加入上下文，`transfer-patterns.yaml` 采用 grep 友好的块索引格式。每个 pattern 前都有一行：

```text
# @pattern id=<id> keywords=<searchable keywords>
```

运行时优先用下面的脚本只加载命中的 pattern 块：

```text
python scripts/select_patterns.py transfer-patterns.yaml <keyword1> <keyword2> --max 5
```

如果没有命中，只读取索引行：

```text
python scripts/select_patterns.py transfer-patterns.yaml --index
```

例如：

```text
evaluation -> training
benchmark -> reward
annotation rubric -> optimization signal
diagnostic tool -> data selection
failure analysis -> curriculum
confidence score -> routing/control signal
```

新增迁移套路时，只需要向 `transfer-patterns.yaml` 添加一个 pattern。为保持轻量，每个 pattern 只保留这些字段：

- `id`：稳定唯一标识。
- `transfer`：一句话描述“来源角色 -> 目标角色”和抽象迁移机制。
- `use_when`：什么类型的 gap 适合尝试。
- `queries`：用于发现证据、候选方法和 novelty check 的检索式模板。
- `apply`：默认应用步骤草稿。
- `risks`：常见失败条件和风险。

### 目标

这些 skills 的目标不是生成泛泛综述，而是帮助研究者形成可验证的研究机会：

- 从目标领域论文的 limitations、future work、open challenges、benchmark gaps 和负结果中抽取开放问题。
- 分析现有方法为什么仍未解决这些问题。
- 将问题抽象成可跨领域迁移的机制。
- 检索其他行业、学科或技术方向中已经有效的方法。
- 检查这些方法是否已经在目标领域被直接使用，或是否存在机制等价方案。
- 如果仍有空白，生成 application plan、研究假设、最小验证实验和可行性 review。

### 输出

skill 会为目标领域生成：

```text
{target_domain}/outline.yaml
{target_domain}/fields.yaml
{target_domain}/results/*.json
{target_domain}/results/transfer_candidates/*.json
{target_domain}/report.md
```

最终报告会给出最值得优先尝试的 3-5 个研究假设，并说明论文证据、跨领域方法、尚未应用证据、应用方案、最小实验、工程/数据难度和风险。

## English

This repository provides cross-domain idea discovery skills for Claude Code or Codex. Two skill folders are exposed directly at the repository root:

- `discover-cross-domain-opportunities-en`: English instructions and English output structure.
- `discover-cross-domain-opportunities-zh`: Chinese instructions and Chinese output structure.
- `discover-transfer-patterns-from-pdf-en`: Discover transfer patterns missing from `transfer-patterns.yaml` from a user-provided PDF.
- `discover-transfer-patterns-from-pdf-zh`: Chinese variant for discovering missing transfer patterns from a user-provided PDF.

Users do not need to build their own workflow or manually chain multiple phases. After choosing the language variant, the user only needs to provide a target research domain. The agent then runs the full workflow automatically: extracting paper-backed open problems, searching for transferable methods from other domains, running novelty checks, designing application plans, reviewing feasibility, and producing the final report.

### Usage

```text
/discover-cross-domain-opportunities-en <target_domain>
```

Or:

```text
/discover-cross-domain-opportunities-zh <目标领域>
```

To mine new reusable transfer patterns from a PDF and maintain the pattern library, use:

```text
/discover-transfer-patterns-from-pdf-en <pdf_path>
```

Or:

```text
/discover-transfer-patterns-from-pdf-zh <pdf_path>
```

### Dynamic Transfer-Pattern Library

The root-level `transfer-patterns.yaml` file maintains reusable transfer patterns. At runtime, the skills dynamically load this file and use its patterns to expand problem abstractions, search queries, novelty checks, application-plan drafts, and risk checks.

To avoid loading the full YAML file into context, `transfer-patterns.yaml` uses grep-friendly block indexes. Each pattern starts with:

```text
# @pattern id=<id> keywords=<searchable keywords>
```

At runtime, prefer this helper to load only matched pattern blocks:

```text
python scripts/select_patterns.py transfer-patterns.yaml <keyword1> <keyword2> --max 5
```

If nothing matches, read only the index lines:

```text
python scripts/select_patterns.py transfer-patterns.yaml --index
```

Examples:

```text
evaluation -> training
benchmark -> reward
annotation rubric -> optimization signal
diagnostic tool -> data selection
failure analysis -> curriculum
confidence score -> routing/control signal
```

To add a new transfer pattern, add one pattern entry to `transfer-patterns.yaml`. To keep the file lightweight, each pattern only keeps these fields:

- `id`: stable unique identifier.
- `transfer`: one sentence describing the source role, target role, and abstract transfer mechanism.
- `use_when`: which kinds of gaps should trigger this pattern.
- `queries`: query templates for evidence, candidate methods, and novelty checks.
- `apply`: draft application steps.
- `risks`: common failure modes and risks.

### Goal

The goal is not to produce a generic literature review. The goal is to help researchers produce verifiable research opportunities:

- Extract open problems from limitations, future work, open challenges, benchmark gaps, and negative results.
- Explain why existing methods still fail.
- Abstract each problem into a transferable cross-domain mechanism.
- Search for methods that already work in other industries, disciplines, or technical areas.
- Check whether those methods have already been applied in the target domain, or whether an equivalent mechanism already exists.
- If a real gap remains, generate an application plan, research hypothesis, minimal validation experiment, and feasibility review.

### Outputs

The skill generates:

```text
{target_domain}/outline.yaml
{target_domain}/fields.yaml
{target_domain}/results/*.json
{target_domain}/results/transfer_candidates/*.json
{target_domain}/report.md
```

The final report recommends the top 3-5 research hypotheses and explains the paper evidence, transferable method, not-yet-applied evidence, application plan, minimal experiment, engineering/data difficulty, and risks.
