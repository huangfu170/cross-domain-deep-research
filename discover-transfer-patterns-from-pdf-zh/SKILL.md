---
name: discover-transfer-patterns-from-pdf-zh
description: 从用户传入的学术 PDF 中发现 transfer-patterns.yaml 尚未收录的可复用领域迁移套路。适用于读取论文、抽取论文核心新思路背后的角色迁移机制，与现有迁移模式库去重对比，并输出可追加到 YAML 的候选 pattern，包括证据、示例、检索式、应用步骤和风险。不要把只适用于单篇论文的具体方法误收录为通用套路。
---

# 从 PDF 发现新的迁移套路

## 触发方式

`/discover-transfer-patterns-from-pdf-zh <pdf_path>`

这个 skill 用来维护 `transfer-patterns.yaml`，不是用来泛泛总结论文。目标是从论文中发现可复用的“新思路生成套路”。

## 输入

- 用户提供的 PDF 路径。
- 现有模式库路径。默认使用当前仓库根目录的 `transfer-patterns.yaml`。
- 用户可选提供目标领域。

## 工作流

### 阶段 0：加载输入

1. 确认 PDF 文件存在。
2. 从 PDF 抽取文本；如果文本抽取质量差，渲染关键页或做视觉检查。
3. 不要直接全文读取 `transfer-patterns.yaml`。先用论文标题、摘要、贡献描述和候选 `transfer` 关键词生成 5-12 个检索词。
4. 优先用 `python scripts/select_patterns.py transfer-patterns.yaml <keyword1> <keyword2> ... --max 5` 选择命中块；如果脚本不可用，再用 `rg -n -i "<keyword1>|<keyword2>|..." transfer-patterns.yaml` 或 PowerShell `Select-String` 搜索 `# @pattern` 索引行。
5. 每个索引行的格式为 `# @pattern id=<id> keywords=<keywords>`。只读取命中的 pattern 块：从该 `# @pattern` 行开始，到下一个 `# @pattern` 行之前结束。
6. 如果没有命中，用 `python scripts/select_patterns.py transfer-patterns.yaml --index` 或 grep 只读取全部 `# @pattern` 索引行进行粗筛，不要读取全部正文；根据索引选择最可能重合的 1-5 个 pattern 块。
7. 如果模式库不存在，就以空模式库继续，并在输出中说明未加载基线模式库。
8. 对已加载的候选块，记录 `id`、`transfer`、`use_when`、`queries`、`apply` 和 `risks`。

### 阶段 1：抽取论文的新思路机制

将论文核心贡献抽象成“角色迁移”或“可复用机制”。优先寻找以下信号：

- 某种信号从一个用途转为另一个用途。
- 评价产物被转化为优化信号。
- 诊断工具被转化为数据选择或课程学习机制。
- benchmark、annotation、verifier、simulator、constraint 被重新用作训练、推理、路由或控制信号。
- 原本离线分析的组件被迁移到在线训练、推理或控制流程。

对每个候选机制抽取：

```yaml
paper_mechanism:
  paper_title: "<论文标题>"
  source_evidence:
    - section: "<章节名或页码>"
      summary: "<简短证据摘要>"
  transfer: "<来源角色> -> <目标角色>: <泛化后的迁移机制>"
  concrete_method_in_paper: "<论文中的具体方法>"
  why_it_is_reusable: "<为什么它能迁移到其他领域或系统环节>"
```

不要把每个算法细节都当成 pattern。只有能跨领域、跨任务或跨系统模块复用的机制，才算值得收录的迁移套路。

### 阶段 2：和现有 YAML 模式库对比

对每个候选机制，与现有 patterns 做去重对比：

- `transfer` 是否相同或近似。
- `use_when` 是否覆盖同类 gap。
- `queries` 是否高度重合。
- `apply` 方案是否本质相同。
- `risks` 是否相同或高度重合。

给每个候选机制分类：

- `already_recorded`：已经被现有 pattern 明确覆盖。
- `variant_of_existing`：是现有 pattern 的有价值变体，建议扩展旧 pattern，而不是新增条目。
- `new_pattern`：尚未覆盖，且足够通用，建议新增。
- `paper_specific_only`：有趣但太窄，只适合这篇论文，不应加入模式库。

### 阶段 3：生成 YAML 候选

对每个 `new_pattern`，输出完整 YAML 条目：

```yaml
- id: "<稳定的 kebab-case id>"
  transfer: "<来源角色> -> <目标角色>: <一句话描述抽象迁移机制>"
  use_when:
    - "<适用条件>"
  queries:
    - "\"{target_domain}\" \"<关键词>\""
  apply:
    - "<步骤>"
  risks:
    - "<风险>"
```

对每个 `variant_of_existing`，输出扩展建议：

```yaml
extend_existing_pattern:
  id: "<existing-pattern-id>"
  add_use_when: []
  add_queries: []
  add_apply: []
  add_risks: []
```

### 阶段 4：收录判断规则

只有同时满足以下条件时，才建议新增 YAML pattern：

- 机制比论文里的具体算法更通用。
- `transfer` 中明确包含来源角色和目标角色。
- 该 pattern 能为未来领域或论文生成检索式。
- 至少能形成一个具体 `apply` 步骤。
- 现有 `transfer-patterns.yaml` 尚未覆盖。

不确定时，优先标记为 `variant_of_existing` 或 `paper_specific_only`，不要勉强新增。

## 输出

返回：

1. 论文层面的新思路机制摘要。
2. 和现有 pattern 的匹配关系及理由。
3. 可能新增的通用迁移套路。
4. 可直接追加到 `transfer-patterns.yaml` 的 YAML 片段。
5. 被拒绝的候选及原因。

除非用户明确要求应用修改，否则不要直接修改 `transfer-patterns.yaml`。
