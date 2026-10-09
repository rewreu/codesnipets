# Side-chat summary: combining RDBLearn and ReFuGe

Date: October 9, 2026

This document summarizes the technical discussion in this side conversation. It is a synthesis, not a verbatim transcript. It separates findings from the papers from our proposed research direction; no implementation or experimental results are claimed.

## 1. Main conclusion

Our recommended starting point is **semantic-guided, budgeted relational feature search**:

> Combine the systematic relational feature construction of RDBLearn with the task-aware feature proposals and feedback loop of ReFuGe. Use a fixed tabular foundation model to evaluate and predict from the resulting feature table.

The important question is not simply whether concatenating their features improves accuracy. It is whether a hybrid planner can identify a **small, complementary, informative feature set before expensive materialization**, improving the accuracy–cost trade-off.

This would initially be a feature-engineering and search system that uses foundation models—not a new graph foundation model. A longer-term direction is to learn an aggregation planner that transfers across previously unseen databases.

## 2. How the conversation developed

### 2.1 Starting direction: plan which relational information to aggregate

We discussed a planner that chooses useful relational context, join paths, aggregation operations, and potentially computation budgets before passing an augmented target table to a predictor.

The key distinction is between:

- A fixed, schema-driven feature-generation recipe.
- A task-aware planner that decides what information to compute.
- A workload-aware planner that also considers execution costs and reuse across tasks.

These are different scopes. A task-aware aggregation system does not automatically provide workload-level optimization or cross-database transfer.

### 2.2 How is this different from RDBLearn?

[RDBLearn: Simple In-Context Prediction Over Relational Databases](https://arxiv.org/abs/2602.18495) already follows the central recipe of relational feature construction followed by a single-table foundation model. Its implementation uses Featuretools descriptions and DuckDB execution, with SQL aggregation pushdown, intermediate reuse, and cutoff constraints. These are existing capabilities, not novelty claims for our proposal. [Paper §4.4](https://arxiv.org/html/2602.18495#S4.SS4).

The possible distinction is **adaptive selection of feature computations under a budget**, rather than merely reproducing SQL-backed DFS. A strong contribution would need evidence that this selection policy improves on ordinary pruning, random search, and the existing pipelines.

### 2.3 Does DFS repeatedly train a model to choose the next search?

No. Here, **DFS means Deep Feature Synthesis**, not a depth-first-search procedure guided by prediction metrics.

DFS constructs features by composing permitted transformations and aggregations over relationships. In RDBLearn's reported experiments, validation selects among maximum DFS depths `{2, 3, 4}` and predictor backends. This configuration selection is separate from DFS feature construction. The paper states that its depth-4 feature set subsumes the shallower sets and can be computed once. [RDBLearn §§5–6](https://arxiv.org/html/2602.18495#S5).

The downstream pretrained predictor performs in-context prediction without per-task gradient training. This does not mean there are no labeled examples, preprocessing, fitting-interface calls, or validation-based choices.

### 2.4 Could an LLM propose the aggregation strategy first?

Yes. The proposed input would include:

- The prediction task and target entity.
- Table schemas, column types, and primary/foreign-key relationships.
- Timestamp meanings and prediction-time availability constraints.
- Training-data statistics, relationship cardinalities, and a computation budget.

The LLM could propose join paths, expressions, filters, aggregation operators, and time windows. A deterministic system would validate and execute these specifications, then pass the augmented table to a predictor.

We favored **structured feature specifications compiled to SQL** over unrestricted LLM-generated code. Correctness checks should enforce legitimate joins, predictable output granularity, temporal availability, and bounded execution.

However, LLM-driven relational feature generation is already central to [ReFuGe](https://arxiv.org/abs/2601.17735). The broad idea alone is not new.

### 2.5 What predictors do ReFuGe and RDBLearn use? Does RDBLearn use RelGT?

| System | Feature construction | Downstream predictor |
| --- | --- | --- |
| ReFuGe | LLM-guided proposals and validation filtering | LightGBM in the inspected released implementation; the framework permits a replaceable tabular predictor |
| RDBLearn | Deterministic DFS aggregation | TabPFN v2, TabPFN v2.5, or LimiX-16M in the paper's experiments |
| RelGT | Learned processing of a relational graph | A supervised graph transformer |

ReFuGe's LLMs are feature engineers, not the final prediction model. Its paper describes retraining a tabular predictor when assessing candidate features; the released example explicitly uses LightGBM. [ReFuGe §3](https://arxiv.org/html/2601.17735#S3), [official example implementation](https://github.com/K-Kyungho/REFUGE/blob/main/amazonchurn.py).

**RelGT is a comparison baseline in RDBLearn, not a component of its pipeline.** [RDBLearn §5](https://arxiv.org/html/2602.18495#S5).

## 3. Proposed method: semantic-guided, budgeted DFS

The following is our proposal, not an implemented capability of either paper.

### Step 1: establish inexpensive systematic coverage

Start with target-table attributes and a small, inexpensive DFS feature set. Counts, sums, means, and shallow relational paths provide a useful starting point without relying entirely on semantic judgments.

Generate descriptions of additional legal DFS candidates without necessarily computing all their values.

### Step 2: use semantic reasoning to prioritize and extend candidates

Give the LLM the task, schema, training-only summaries, existing feature descriptions, and previous search feedback. Ask it to:

- Prioritize plausible DFS paths, columns, and operators.
- Propose conditional aggregations and suitable time windows.
- Introduce cross-column expressions missing from the starting configuration.
- Identify redundant candidates and propose complementary alternatives.

One possible feature specification is:

```text
entity: customer at prediction time t
path: customer -> orders -> order_items
expression: quantity * unit_price
aggregation: SUM
window: [t - 30 days, t)
output: spending_last_30_days
```

This is an illustrative specification, not executable SQL or a verified benchmark schema.

### Step 3: validate and compile features deterministically

The compiler—not the LLM alone—must check:

- Tables, columns, types, and join relationships.
- One output row per target entity and prediction time.
- Join multiplicity, especially when joining several one-to-many branches.
- Event-time and, where available, information-availability cutoffs.
- Exclusion of unavailable target/outcome information.
- Supported operations and resource limits.

Group compatible computations to reuse scans and intermediate results. Reuse is an implementation foundation; the research question concerns which computations are selected.

### Step 4: evaluate small feature batches using the actual predictor

Use one fixed tabular foundation model initially. Evaluate candidate batches for improvement over the current feature set and record their actual computation costs.

Do not assume that features selected using LightGBM will be equally useful to TabPFN. Predictor-dependent feature selection is an experimental question.

Evaluate some feature groups jointly: two features may be useful together even if neither is helpful alone. Conversely, several individually useful features may become redundant when combined.

### Step 5: adapt the search under a budget

Return measured gains, failures, redundancy, and execution costs to the planner. It can then:

- Deepen a promising relational path.
- Refine a filter, expression, or time window.
- Explore an overlooked table.
- Stop when improvements are unstable or the budget is exhausted.

Reserve an exploration allowance so an incorrect LLM judgment does not permanently exclude useful features. Consider shared incremental execution costs rather than assuming every feature has an independent cost.

## 4. Why the hybrid could help

### Systematic coverage plus semantic specialization

DFS provides reliable coverage of its configured operator space. LLM proposals can focus computation on task-relevant paths and extend the feature vocabulary. Neither alone guarantees that the resulting features will help; empirical evaluation remains necessary.

### Preserve interactions before aggregation

Consider an orders table with `quantity` and `unit_price`. Separately aggregating those columns does not generally recover:

```text
SUM(quantity * unit_price)
```

The pairing between values must be preserved before summation. An LLM might propose this expression while the relational engine computes it consistently.

This illustrates a limitation of **column-wise aggregation configurations**, not an inherent inability of Featuretools or all DFS variants to support custom interaction primitives. Simple products can also be enumerated without an LLM; the proposed advantage must be demonstrated in selecting useful expressions from a much larger space.

### Control width before materialization

Selecting candidates before expensive execution may reduce SQL work, feature-table width, and predictor overhead. This is a hypothesis: a hybrid can also incur substantial LLM and evaluation costs. Measure the full pipeline, not only final inference.

## 5. Novelty boundaries and related work

| Proposed ingredient | Existing overlap | Implication |
| --- | --- | --- |
| SQL-backed DFS, caching, cutoff constraints | RDBLearn | Reuse these capabilities; do not present them as new |
| LLM-generated relational features with feedback | ReFuGe | A feedback loop alone is insufficient differentiation |
| LLM feature engineering with TabPFN | CAAFE | Changing the downstream predictor is a baseline, not a strong contribution |
| Addressing feature explosion and lost interactions | RelICL | Compare alternative representations and aggregation strategies |

[CAAFE's official implementation](https://github.com/noahho/CAAFE) explicitly supports tabular base predictors including TabPFN. Therefore, “LLM-generated features plus a tabular foundation model” is established prior art.

A particularly recent related paper is **[RelICL: Training-free Relational Learning with Tabular Foundation Models](https://arxiv.org/abs/2610.01725)**, submitted October 1, 2026. It studies feature explosion and interaction blindness in column-wise DFS pipelines, using tabular-model row embeddings and schema-wise propagation/fusion instead. Our proposed explicit-expression search would be a different mechanism, but not the first work to identify these problems.

The most defensible research hypothesis is:

> Semantic guidance, deterministic relational construction, and cost-aware adaptive search can find complementary explicit features more efficiently than either method alone.

Novelty is **not established** by this discussion. A fuller literature review is required before claiming a new method or first result.

## 6. Suggested experimental plan

Start with a fixed predictor and tasks from the same relational benchmark version and evaluation protocol.

### Essential comparisons

1. Target-table attributes only.
2. DFS only.
3. ReFuGe-style features only, using the same predictor.
4. Simple union of DFS and LLM-generated features.
5. Guided, budgeted hybrid search.
6. Random or conventional statistical selection under a matched budget.

Add RelICL where compatible. RelGT can be a separate supervised reference; it is not needed inside the proposed pipeline.

### Ablations

- LLM prioritization versus random prioritization.
- Candidate selection only versus adding new interaction features.
- One-shot proposals versus feedback-driven search.
- Cost-aware versus accuracy-only search.
- Individual feature evaluation versus batch/group evaluation.
- Feature selection with LightGBM versus selection with the actual foundation-model predictor.

### Metrics and fairness

Report predictive performance, retained feature count, SQL runtime, peak memory, LLM usage/cost, predictor evaluation cost, and total search time. Compare accuracy across budgets rather than only reporting one best configuration.

Keep label access, in-context examples, predictor settings, and test protocol consistent. Use training-only statistics for proposals, temporally appropriate validation, repeated seeds or windows, and an untouched test set. Repeated validation queries can overfit the search process even when the predictor is frozen.

## 7. Longer-term direction and final recommendation

**Near term:** implement and evaluate the hybrid aggregation planner with a fixed pretrained tabular predictor. Establish whether it improves accuracy–cost trade-offs beyond simple feature union and ordinary selection.

**Longer term:** collect search traces across databases and learn a planner that transfers feature-selection and aggregation policies to unseen schemas. Evaluate on held-out databases, not just new tasks sharing the same schema. This could support a foundation-style aggregation policy, but would still not automatically constitute a graph foundation model.

**Final recommendation:** pursue the hybrid as a focused relational feature-search project first. Keep the central contribution on *what to compute, how to preserve useful interactions, and how to allocate the search budget*—not on relabeling a familiar pipeline as a new foundation model.

## References

- [RDBLearn: Simple In-Context Prediction Over Relational Databases](https://arxiv.org/abs/2602.18495).
- [ReFuGe: Feature Generation for Prediction Tasks on Relational Databases with LLM Agents](https://arxiv.org/abs/2601.17735).
- [ReFuGe official repository](https://github.com/K-Kyungho/REFUGE).
- [CAAFE: Large Language Models for Automated Data Science](https://arxiv.org/abs/2305.03403).
- [CAAFE official repository](https://github.com/noahho/CAAFE).
- [RelICL: Training-free Relational Learning with Tabular Foundation Models](https://arxiv.org/abs/2610.01725).
