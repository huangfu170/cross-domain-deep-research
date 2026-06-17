---
name: discover-transfer-patterns-from-pdf-en
description: Discover reusable transfer patterns from a user-provided academic PDF that are not yet recorded in transfer-patterns.yaml. Use when Codex or Claude Code needs to read a paper, identify the role-transfer mechanism behind its core idea, compare it with the existing pattern library, and propose deduplicated YAML additions using the compact fields id, transfer, use_when, queries, apply, and risks. Do not add paper-specific methods unless they generalize across domains or system roles.
---

# Discover Transfer Patterns From PDF

## Trigger

`/discover-transfer-patterns-from-pdf-en <pdf_path>`

Use this skill to mine reusable idea-discovery patterns from a paper. The output should help maintain `transfer-patterns.yaml`; it should not be a general paper summary.

## Inputs

- A user-provided PDF path.
- Existing pattern-library path. Default: `transfer-patterns.yaml` in the current repository root.
- Optional target domain if the user provides one.

## Workflow

### Phase 0: Load Inputs

1. Verify that the PDF exists.
2. Extract text from the PDF. If text extraction is poor, render key pages or inspect visually.
3. Do not read all of `transfer-patterns.yaml` directly. First generate 5-12 search keywords from the paper title, abstract, contribution description, and candidate `transfer` terms.
4. Prefer `python scripts/select_patterns.py transfer-patterns.yaml <keyword1> <keyword2> ... --max 5` to select matching blocks. If the script is unavailable, use `rg -n -i "<keyword1>|<keyword2>|..." transfer-patterns.yaml` or PowerShell `Select-String` to search the `# @pattern` index lines.
5. Each index line uses `# @pattern id=<id> keywords=<keywords>`. Read only the matched pattern blocks, starting at the matched `# @pattern` line and stopping before the next `# @pattern` line.
6. If nothing matches, use `python scripts/select_patterns.py transfer-patterns.yaml --index` or grep to read at most all `# @pattern` index lines for coarse screening, not the full bodies; then choose the most likely 1-5 pattern blocks from the index keywords.
7. If no pattern library exists, continue with an empty pattern list and report that no baseline library was loaded.
8. For loaded candidate blocks, record existing pattern `id`, `transfer`, `use_when`, `queries`, `apply`, and `risks`.

### Phase 1: Extract the Paper's Idea Mechanism

Identify the paper's central contribution as a role transfer or reusable mechanism. Look especially for cases where:

- a signal used in one role is reused in another role
- an evaluation artifact becomes an optimization signal
- a diagnostic tool becomes a data-selection or curriculum mechanism
- a benchmark, annotation, verifier, simulator, or constraint is repurposed
- a workflow component moves from offline analysis into training, inference, routing, or control

For each candidate mechanism, extract:

```yaml
paper_mechanism:
  paper_title: "<title>"
  source_evidence:
    - section: "<section name or page>"
      summary: "<short evidence summary>"
  transfer: "<source role> -> <target role>: <generalized transfer mechanism>"
  concrete_method_in_paper: "<paper-specific method>"
  why_it_is_reusable: "<why this can apply beyond this paper>"
```

Do not treat every method detail as a pattern. A pattern should be reusable across domains, tasks, or system components.

### Phase 2: Compare Against Existing YAML Patterns

For each candidate mechanism, compare it to existing patterns using:

- exact or near-duplicate `transfer`
- similar `use_when`
- overlapping `queries`
- equivalent `apply` plan
- overlapping `risks`

Classify each candidate:

- `already_recorded`: clearly covered by an existing pattern.
- `variant_of_existing`: useful specialization of an existing pattern; suggest extending the existing pattern instead of adding a new entry.
- `new_pattern`: not covered and reusable enough to add.
- `paper_specific_only`: interesting but too narrow for the pattern library.

### Phase 3: Propose YAML Additions

For every `new_pattern`, produce a complete YAML entry following the repository schema:

```yaml
- id: "<stable-kebab-case-id>"
  transfer: "<source role> -> <target role>: <one-sentence mechanism>"
  use_when:
    - "<trigger condition>"
  queries:
    - "\"{target_domain}\" \"<keyword>\""
  apply:
    - "<step>"
  risks:
    - "<risk>"
```

For every `variant_of_existing`, propose an update block instead:

```yaml
extend_existing_pattern:
  id: "<existing-pattern-id>"
  add_use_when: []
  add_queries: []
  add_apply: []
  add_risks: []
```

### Phase 4: Validation Rules

Recommend a new YAML pattern only when all of the following are true:

- The mechanism is more general than the paper's specific algorithm.
- The `transfer` string clearly states a source role and target role.
- The pattern can generate search queries for future papers or domains.
- The pattern has at least one concrete `apply` step.
- It is not already covered by `transfer-patterns.yaml`.

When uncertain, mark the candidate as `variant_of_existing` or `paper_specific_only` rather than forcing a new pattern.

## Output

Return:

1. Paper-level mechanism summary.
2. Existing-pattern matches and why they match.
3. New reusable patterns, if any.
4. YAML snippets ready to append to `transfer-patterns.yaml`.
5. Rejected candidates with reasons.

Do not modify `transfer-patterns.yaml` unless the user explicitly asks to apply the additions.
