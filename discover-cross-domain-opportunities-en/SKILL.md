---
name: discover-cross-domain-opportunities-en
description: End-to-end cross-domain research opportunity discovery from academic papers. Use when Codex or Claude Code needs to find paper-backed open problems, identify unresolved causes, search for methods from other domains that may transfer, run novelty checks, design concrete application plans, review feasibility, and produce a report with research hypotheses and minimal experiments. This is the single user-facing entry point; do not ask the user to run separate planning, extraction, transfer, or reporting skills.
---

# Discover Cross Domain Opportunities

## Trigger

`/discover-cross-domain-opportunities-en <target_domain>`

Use this skill as the only public entry point for cross-domain idea discovery. Internally execute all phases below. Do not ask the user to choose or manually chain sub-workflows.

## Goal

Find verifiable research opportunities rather than a generic literature review:

- Extract open problems from target-domain papers, especially limitations, future work, open challenges, benchmark gaps, negative results, and deployment constraints.
- Explain why existing methods still fail.
- Abstract each problem into a cross-domain mechanism.
- Search for methods that work in other domains but are not directly applied to the target domain.
- Run novelty checks for direct applications and mechanism-equivalent methods.
- Produce concrete application plans, research hypotheses, minimal experiments, feasibility reviews, and a final report.

## Workflow

### Phase 0: Set Run Metadata

Get the current year-month before searching:

- Windows PowerShell: `Get-Date -Format "yyyy-MM"`
- POSIX shell: `date +%Y-%m`

Record it as `{current_year_month}` in `outline.yaml`, JSON outputs, and `report.md`.

Also dynamically load the transfer-pattern library by search, without putting the full YAML file into context:

1. If the user provides a pattern-library path, read that YAML first.
2. Otherwise read `transfer-patterns.yaml` from the current repository root.
3. Do not read the whole pattern library directly. First extract 5-12 search keywords from the current gap's `problem_statement`, `why_unsolved`, `failure_modes`, `evaluation_gap`, `candidate_source_domains`, and target-domain terms.
4. Prefer `python scripts/select_patterns.py transfer-patterns.yaml <keyword1> <keyword2> ... --max 5` to select matching blocks. If the script is unavailable, use `rg -n -i "<keyword1>|<keyword2>|..." transfer-patterns.yaml` or PowerShell `Select-String` to search only the `# @pattern` index lines.
5. Each index line uses `# @pattern id=<id> keywords=<keywords>`. Only read matched YAML blocks, starting at the matched `# @pattern` line and stopping before the next `# @pattern` line.
6. If nothing matches, use `python scripts/select_patterns.py transfer-patterns.yaml --index` or grep to read at most all `# @pattern` index lines, not the full pattern bodies; then choose the most likely 1-3 blocks from the index keywords.
7. If multiple pattern libraries exist, merge matched blocks and deduplicate by `id`.
8. If no pattern library exists, continue the task but mention in the report that no dynamic transfer-pattern library was loaded.

Each pattern only needs `id`, `transfer`, `use_when`, `queries`, `apply`, and `risks`. Patterns are heuristic seeds for transfer hypotheses, not final conclusions.

### Phase 1: Create Project Outline

Create or update `{target_domain}/outline.yaml` and `{target_domain}/fields.yaml`.

`outline.yaml` must include:

```yaml
topic: "<target_domain>"
created_at_month: "<current_year_month>"
scope:
  target_domain: "<target domain>"
  time_range: "last five years, with classic papers when needed"
  include_preprints: true
papers:
  - title: "<paper title>"
    year: 2025
    venue: "<venue or arXiv>"
    url: "<url or DOI>"
    reason: "<why this paper matters>"
research_questions:
  - id: "RQ1"
    problem: "<paper-backed open problem>"
    evidence_type: "limitation"
    source_papers: ["<paper title>"]
    why_unsolved: "<why current methods still fail>"
candidate_source_domains:
  - domain: "<source domain>"
    analogous_problem: "<similar problem in the source domain>"
    search_keywords: ["<method keyword>", "<problem keyword>"]
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
    R0: "user-provided target-domain keywords"
    R1: "core papers, surveys, benchmarks, datasets"
    R2: "citations and citing papers from R1"
    R3: "neighboring tasks"
    R4: "external domains for the abstract problem"
    R5: "code, datasets, tools, benchmark pages, industrial systems"
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

`fields.yaml` must cover at least:

- paper evidence: `problem_statement`, `evidence_from_papers`, `evidence_type`, `why_unsolved`
- target-domain attempts: `current_attempts`, `failure_modes`, `evaluation_gap`
- transfer search: `problem_abstraction`, `external_method`, `source_domain`, `not_yet_applied_evidence`, `possible_existing_equivalent`, `novelty_check`
- application design: `application_plan`, `target_component`, `mechanism_mapping`, `implementation_steps`, `required_signals_or_data`, `baseline_to_modify`, `success_metrics`
- validation: `hypothesis`, `minimal_experiment`, `engineering_difficulty`, `data_difficulty`, `dataset_or_benchmark`, `risk_or_limitation`, `evidence_level`, `feasibility_review`

### Phase 2: Extract Paper-Backed Gaps

For each `research_question`, create `{output_dir}/{rq_slug}.json`. Skip existing files to support resume.

Required evidence rules:

- Do not output a confirmed problem without paper or benchmark evidence.
- Mark single-paper evidence as `weak_evidence`.
- Prefer problems repeated across multiple papers or benchmarks.
- Distinguish author-stated limitations from agent-inferred gaps.
- Use `[uncertain]` for unknown fields and list them under top-level `uncertain`.

Single-question JSON shape:

```json
{
  "id": "RQ1",
  "created_at_month": "2026-06",
  "problem_statement": "clear problem statement",
  "target_domain": "target domain",
  "paper_evidence": [
    {
      "paper": "paper title",
      "venue_year": "NeurIPS 2025",
      "evidence_type": "future_work",
      "evidence_summary": "limitation or future work summary",
      "url": "https://..."
    }
  ],
  "current_attempts": [
    {
      "method": "existing target-domain method",
      "limitation": "why it is still insufficient"
    }
  ],
  "why_unsolved": "unresolved cause",
  "failure_modes": ["failure mode"],
  "evaluation_gap": "gap not covered by existing evaluation",
  "search_expansion": {
    "search_depth": "deep",
    "target_domain_layers_checked": ["survey", "benchmark", "failure_analysis"],
    "citation_snowball_used": true,
    "non_paper_sources_checked": ["official benchmark pages"],
    "missed_risk": "low/medium/high"
  },
  "candidate_source_domains": [
    {
      "domain": "source domain",
      "analogous_problem": "similar problem",
      "search_keywords": ["keyword"]
    }
  ],
  "uncertain": []
}
```

Validate result coverage with `validate_json.py` when `fields.yaml` exists.

### Phase 3: Find Transfer Methods

For each extracted gap:

1. Build `problem_abstraction` before searching externally.
2. Match the `problem_abstraction` against the retrieved transfer-pattern blocks, prioritizing patterns whose `use_when` conditions fit the current gap.
3. Expand beyond the initial `candidate_source_domains` by using each matched pattern's `transfer` as a seed for external domains and adjacent in-domain components.
4. Search across rings `R0` to `R5`.
5. For each matched pattern, generate search queries from its `queries`; replace placeholders such as `{target_domain}`, `{target_task}`, `{target_problem}`, and `{method}` with current task content.
6. Record external methods with source evidence.
7. Run bidirectional novelty checks and reuse the pattern's `queries` to generate reverse and equivalent-mechanism checks.
8. Use the pattern's `apply` as a draft, but rewrite it into a target-specific, concrete application plan.
9. Carry the pattern's `risks` into risk analysis; do not treat a pattern match as novelty by itself.
10. Prefer engineering difficulty `low`, `medium`, or `medium-high`.

Problem abstraction shape:

```yaml
problem_abstraction:
  surface_problem: "<target-domain wording>"
  abstract_problem: "<cross-domain generic problem>"
  mechanism_keywords:
    - "<mechanism keyword>"
  source_domain_seeds:
    - "<source domain>"
```

Novelty check queries must include:

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

Application status:

- `already_applied`: direct target-domain application found.
- `possible_existing_equivalent`: mechanism-equivalent target-domain method found.
- `candidate_gap`: no direct application evidence found.
- `unclear`: evidence is insufficient.

Write transfer outputs to `{transfer_output_dir}/{rq_slug}_transfer.json`.

Each candidate method must include:

```json
{
  "transfer_pattern_id": "evaluation-to-training",
  "transfer_pattern": "evaluation -> training: Turn evaluation criteria into training supervision or reward signals.",
  "method": "external method",
  "source_domain": "source domain",
  "source_evidence": ["url"],
  "application_status": "candidate_gap",
  "not_yet_applied_evidence": "No direct target-domain application found in checked sources; not an absolute claim.",
  "possible_existing_equivalent": "[uncertain]",
  "application_plan": {
    "target_component": "where it applies in the target system",
    "mechanism_mapping": "how the source mechanism maps to the target problem",
    "implementation_steps": ["step 1", "step 2", "step 3"],
    "required_signals_or_data": ["signal or data"],
    "baseline_to_modify": "target-domain baseline to modify",
    "success_metrics": ["metric"]
  },
  "hypothesis": "verifiable research hypothesis",
  "minimal_experiment": "minimal validation experiment",
  "engineering_difficulty": "low/medium/medium-high/high with reason",
  "data_difficulty": "low/medium/high with reason",
  "dataset_or_benchmark": "dataset or benchmark",
  "risk_or_limitation": "risk or counterexample",
  "evidence_level": "A/B/C/D"
}
```

### Phase 4: Review Feasibility

For every `candidate_gap`, add `feasibility_review`:

```json
{
  "feasibility": "high/medium/low",
  "minimum_viable_path": "what can be tested first",
  "blocking_dependencies": ["dependency"],
  "validation_risks": ["risk"],
  "fallback_plan": "smaller or offline fallback",
  "review_verdict": "go/revise/hold"
}
```

Use:

- `go`: dependencies are available, minimum experiment is clear, metrics are credible.
- `revise`: direction is useful but scope, data, baseline, or evaluation must be adjusted.
- `hold`: key dependency is unavailable or no minimal experiment can test the hypothesis.

### Phase 5: Write Final Report

Generate `{target_domain}/report.md` with:

```text
# {topic} Research Opportunity Report

Generated month: {current_year_month}

## 1. Domain Status
## 2. Paper-Backed Open Problems
## 3. Problem Clusters
## 4. Transferable Cross-Domain Methods
## 5. Evidence of Not-Yet-Applied Methods
## 6. Search Coverage and Missed-Risk Analysis
## 7. Feasibility Review
## 8. Ranked Research Hypotheses
## 9. Minimal Experiments
## 10. Risks, Counterexamples, and Exclusions
## 11. References
```

For each opportunity, include:

- problem
- paper evidence
- why unresolved
- external method
- transfer rationale
- application plan
- novelty check result
- possible equivalent methods
- feasibility review
- minimal experiment
- engineering and data difficulty
- expected contribution
- risk
- evidence level

## Search Depth

Default to `deep`.

- `light`: quick scan, core survey/benchmark and a few novelty queries.
- `standard`: core papers, benchmarks, limitations, candidate source domains.
- `deep`: default; include citation snowball, neighboring tasks, abstract problem search, code/data/tool sources, and bidirectional novelty checks.
- `exhaustive`: add patents, industrial reports, deeper citation snowball, and more reverse-equivalence checks.

## Stop Conditions

Stop or downgrade a candidate when:

- 10 consecutive results add no new method family or counterevidence.
- Two independent sources confirm direct target-domain use.
- No credible baseline, data, or evaluation metric is available.
- Engineering difficulty is `high` and cannot be reduced to a `medium-high` minimal experiment.

## Final Deliverables

Produce:

```text
{target_domain}/outline.yaml
{target_domain}/fields.yaml
{target_domain}/results/*.json
{target_domain}/results/transfer_candidates/*.json
{target_domain}/report.md
```

End with the top 3-5 recommended research hypotheses and explain why they are prioritized.
