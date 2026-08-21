# Speaker Script: OpenRFM vs TabPFN-Rel

Companion deck: `OpenRFM_TabPFN_Rel_Deep_Dive_2026.pptx`

**Audience:** research group  
**Suggested duration:** 12–15 minutes, excluding discussion  
**Central message:** OpenRFM and TabPFN-Rel both use in-context learning, but they put relational reasoning in different places. OpenRFM learns relational representations inside the model; TabPFN-Rel constructs relational aggregate features before invoking a frozen tabular foundation model.

## How to use this script

- The text under **Talk track** is written to be spoken naturally; it does not need to be read word for word.
- Text in `[brackets]` is a delivery or pointing cue, not something to say aloud.
- Each slide contains a transition that connects it to the next slide.
- Sections marked **If time permits** can be skipped for a shorter presentation.

Useful pronunciations:

- **RFM:** “R-F-M,” relational foundation model.
- **ICL:** “I-C-L,” in-context learning.
- **RT:** “R-T,” Relational Transformer.
- **DFS:** “D-F-S,” Deep Feature Synthesis.
- **ρ:** “rho.”
- **Elo:** “EE-lo.”

---

## Slide 1 — OpenRFM vs TabPFN-Rel

**Suggested time:** 45–60 seconds  
**Purpose:** Establish the comparison question and prevent the audience from treating the talk as a simple leaderboard comparison.

### Talk track

Today I want to compare two recent approaches to relational in-context learning: OpenRFM and TabPFN-Rel.

The most useful way to compare them is not to ask which paper reports the larger number. Their numbers come from different benchmarks and are not directly comparable. The more interesting question is: **where does relational reasoning happen?**

[Point to the right-hand panel.]

OpenRFM tries to **learn the relational representation**. It keeps primary-key and foreign-key structure inside a pretrained relational model.

TabPFN-Rel instead **engineers the relational view**. It converts the database into a flat feature table and then asks TabPFN-3 to make predictions.

The common element is at the bottom: both systems ultimately use a form of tabular, batch-level in-context learning. The architectural fork occurs before that final prediction stage.

This distinction will be the organizing idea for the presentation.

### Transition

Let me make that architectural fork concrete by following one query through each system.

---

## Slide 2 — Same goal, different place for relational reasoning

**Suggested time:** 1.5 minutes  
**Purpose:** Give the audience a mental model of both pipelines before discussing details.

### Talk track

Both systems start from a relational database and want to make predictions without training a new model from scratch for every task. But the two pipelines preserve different information.

[Point to the OpenRFM pipeline on the left.]

For OpenRFM, each query is associated with a sampled breadth-first-search relational context. A Relational Transformer encodes that neighborhood. Because this encoder has been pretrained on relational databases, the output is intended to be a learned representation of the query and its local relational environment.

That representation then enters a batch-level ICL module based on TabICL or TabPFN. The labeled examples in the batch act as support for the query.

[Point to the TabPFN-Rel pipeline on the right.]

TabPFN-Rel freezes the database at the prediction cutoff, enumerates join paths, and uses Deep Feature Synthesis to turn those paths into aggregate columns. TabPFN-3 sees the resulting flat rows. It does not see the original graph topology.

So this is not primarily a “Transformer versus Transformer” comparison. The important difference is:

- OpenRFM retains topology inside the learned model.
- TabPFN-Rel collapses topology into columns before modeling.

The shared idea in the black band is also important. In both cases, prediction is conditioned on labeled support rows. The disagreement is about how each support or query row should encode its relational world.

### If time permits

This distinction suggests a regime hypothesis. A learned relational representation should matter most when paths, interactions, or topology cannot be summarized by a few aggregates. A flatten-first method may be extremely hard to beat when the task is aggregate-friendly and many labels are available.

### Transition

To understand why OpenRFM adds batch-level ICL, we first need to understand its diagnosis of the original Relational Transformer.

---

## Slide 3 — RT's “zero-shot” prediction is relation-level ICL

**Suggested time:** 1.5–2 minutes  
**Purpose:** Explain label reachability and the lazy-versus-feature-learning diagnosis.

### Talk track

OpenRFM's first contribution is diagnostic. The authors argue that RT's so-called zero-shot behavior is not truly label-free. It is a form of **relation-level in-context learning**.

For each query, RT samples a relational walk. If that walk reaches labeled rows from the task table, those labels become local support examples. The prediction behaves approximately like kernel regression over this support.

The paper measures this using label reachability, rho: how readily a query's sampled context exposes labeled task-table rows.

[Point to the first two bars.]

On `st-outc`, rho is only 0.002, and RT is almost random at 0.493 AUC. On `st-adv`, rho is 0.006, and RT has negative R-squared. These are cases where the local walk contains almost no useful labeled support.

[Point to the green bar.]

In contrast, `driver-top3` has rho 0.893 and RT reaches 0.824 AUC. These examples support the idea that local label availability is a major bottleneck. They are diagnostic correlations, not by themselves a complete causal proof.

The right-hand side identifies a second bottleneck. The authors shuffle or randomize relational features and ask whether predictions change. With RT-PluRel, performance often changes very little. They call this the lazy or frozen-feature regime: the architecture is relational, but the model is not strongly using the relational features.

With co-training or suitable real-data pretraining, predictions become more sensitive to relational features. That is the feature-learning regime.

The conclusion is that OpenRFM must solve two problems: provide support beyond the local relational walk, and use a pretraining prior that makes relational reasoning necessary.

### Transition

Those two bottlenecks lead directly to OpenRFM's two main design changes: dual-stage ICL and a support-identifiable pretraining prior.

---

## Slide 4 — Dual-stage ICL repairs the missing support channel

**Suggested time:** 2 minutes  
**Purpose:** Explain exactly how TabICL relates to OpenRFM and how the final architecture was selected.

### Talk track

OpenRFM combines two axes of in-context learning.

[Point to “Horizontal.”]

The horizontal axis is relation-level. RT blocks process the sampled relational context around each query. This stage asks: what does the local database neighborhood tell us about this individual example?

[Point to “Vertical.”]

The vertical axis is batch-level. OpenRFM pools the representation for each query, normalizes it, and gives a batch of these representations to a TabICL-style module. Labeled rows elsewhere in the task table can now support the query even if they were not reached by its graph walk.

This is the direct relationship between OpenRFM and TabICL: **TabICL is the batch-level adaptation head inside OpenRFM.** TabICL does not provide the relational representation. RT provides that representation; TabICL compares the resulting examples in context.

[Point to the yellow pretraining box.]

The second change is the pretraining prior. The authors introduce a controllable homophily latent, `h`, during synthetic label generation. Labeled support examples reveal the value of this latent, so the model must use support information to make good predictions. They then continue pretraining on a mixture of this synthetic data and selected held-out real databases, with a prototype loss for multi-class tasks.

The design rule at the bottom comes from an important negative result. A fully end-to-end two-dimensional attention design reached low training loss but collapsed to nearly constant downstream predictions. The stable design is staged: pool the RT representation, normalize it, and use the original TabICL encoder and ICL stack.

### If time permits

The bridge ablations show that normalization is critical, TabICL's original encoder is stronger than a simple linear adapter, and interleaving TabICL layers between RT blocks gives limited and task-dependent improvements.

### Transition

The ablations on the next slide let us separate how much improvement comes from the ICL head, the pretraining data, the objective, and ensembling.

---

## Slide 5 — The batch-ICL head is the largest single gain

**Suggested time:** 1.5–2 minutes  
**Purpose:** Interpret OpenRFM's evidence without overstating its headline result.

### Talk track

This cumulative ablation is one of the most useful results in the paper.

[Point to the first two rows.]

The RT-PluRel starting point has a binary AUC of 0.66. Adding the TabICL batch-level head raises it to 0.76. That is the largest single classification gain in the table, which strongly supports the missing-support-channel diagnosis.

Adding the homophily-aware synthetic prior raises AUC further to 0.78. But notice the next row: adding real data naively reduces all three aggregate metrics. Real data is not automatically beneficial. The model needs an objective that organizes the data into reusable relational behavior.

The prototype loss recovers classification and ranking performance. Finally, eight-way support ensembling produces the largest regression improvement, taking R-squared from 0.14 to 0.23.

[Point to 4.92.]

Across the paper's 24-task mixed suite, OpenRFM reports a mean rank of 4.92, the best in that evaluation. It also avoids per-task training. In the reported `rel-stack` efficiency example, OpenRFM takes 21.2 minutes, compared with roughly 15 to 18 hours for per-task RDL-GNN and RelGT training.

But I would attach two qualifications. First, this is a version-one preprint. Second, this is not the RelArena protocol. The mean rank here cannot be compared numerically with the Elo scores that we will see for TabPFN-Rel.

### If time permits

The paper's JUICE timing appears lower at 13.6 minutes, but the caption says that its text-encoding stage adds another 14 minutes. This illustrates why full pipeline accounting matters.

### Transition

OpenRFM starts by learning a relational representation. TabPFN-Rel takes the opposite route: it materializes a flat relational view and relies on a very strong frozen tabular model.

---

## Slide 6 — Flatten first; let a frozen tabular FM adapt in context

**Suggested time:** 1.5–2 minutes  
**Purpose:** Explain TabPFN-Rel's full pipeline and clarify that it is no-gradient but label-rich.

### Talk track

TabPFN-Rel begins by freezing the relational database at a temporal cutoff. This is essential: only rows available at prediction time can contribute features.

[Point to Stage 1 and Stage 2.]

Deep Feature Synthesis then follows primary-key and foreign-key paths and computes aggregates. For example, it might count a driver's results, calculate a mean points value, or aggregate over a two-hop path through races.

The maximum path depth is tuned over two, three, or four. Larger depth can expose longer dependencies, but it also increases the number of join paths and the preprocessing cost.

[Point to Stage 3.]

After materialization, every entity-cutoff becomes one flat row. Labeled rows form the context, query rows have missing targets, and the frozen TabPFN-3 model performs in-context prediction.

The reported release uses eight estimators. Each estimator draws 100,000 context rows from the 400,000 most recent candidates. At test time, both training and validation labels are available in the context.

This means TabPFN-Rel requires no gradient update for the downstream task, but it is not strict zero-shot learning. It is a label-rich ICL system.

The API version also reattaches raw text from the anchor table, while the open-source version is text-free.

The conceptual takeaway is that TabPFN-3 itself does not see the relational graph. Its relational inductive bias is supplied by DFS and the temporal feature-materialization pipeline.

### If time permits

TabPFN-Rel also improves the earlier RDBLearn tuning protocol. The database is frozen at the validation cutoff for inner tuning and at the test cutoff for final evaluation, reducing temporal drift and leakage problems.

### Transition

The result is a surprisingly strong standardized model on RelArena, but we need to read the two leaderboard panels carefully.

---

## Slide 7 — Number-one standardized model, but not the number-one overall system

**Suggested time:** 1.5–2 minutes  
**Purpose:** Explain the RelArena ranking accurately and surface the benchmark caveats.

### Talk track

The left panel is the standardized model leaderboard over 21 RelArena-alpha entity-forecasting tasks.

TabPFN-Rel API is first at 1821 Elo. The open-source, text-free version is at 1706. GraphSAGE is at 1658, and RelGT is at 1575.

[Point to the right panel.]

The right panel includes methods categorized as complete systems as well as standardized models. RT-PluRel leads this board at 1861, while TabPFN-Rel API is at 1826.

So the precise statement is: **TabPFN-Rel is the number-one standardized model in this release, but it is not the number-one overall submitted system.**

The per-entity constant baseline is also important. It predicts each entity's own best historical constant and reaches 1256 Elo. Only TabPFN-Rel and RT-PluRel beat this baseline on all 21 tasks. That tells us these relational benchmarks contain strong historical priors that should not be ignored.

There are four caveats at the bottom.

First, the leaderboard uses one seed and covers entity forecasting only. Second, CPU feature-synthesis time is excluded from the headline runtime comparison. Third, the API-to-OSS gap is largely driven by two text-heavy tasks rather than a uniform benefit across the suite. Fourth, depth two is often already competitive, while deeper DFS paths become increasingly expensive.

Elo is also relative to the submitted field. It is useful for comparing entries within this board, but it is not a universal measure that can be compared with OpenRFM's mean rank.

### Transition

Because the two papers use different support budgets, benchmarks and cost accounting, the right conclusion is not that one has already defeated the other. The right conclusion is that we need a controlled experiment.

---

## Slide 8 — The missing experiment: equal support plus equal compute

**Suggested time:** 2 minutes  
**Purpose:** Synthesize the papers into an actionable evaluation and RelGT foundation-model direction.

### Talk track

This table summarizes why we cannot currently make an apples-to-apples comparison.

OpenRFM learns an RT embedding; TabPFN-Rel uses DFS aggregate columns. OpenRFM performs relational pretraining; TabPFN-Rel does not add relational pretraining to its frozen tabular model.

The support budgets are especially different. OpenRFM is limited to at most 2,048 rows and usually reports 1,024 rows across eight support draws. TabPFN-Rel uses 100,000 rows for each of eight estimators.

They also use different published benchmarks: a 24-task mixed suite for OpenRFM and 21 RelArena entity-forecasting tasks for TabPFN-Rel.

The missing experiment is therefore an equal-support, equal-compute comparison. I would use the same temporal snapshots, the same labels, the same text inputs and the same ensemble count. I would report support curves at zero, eight, 32, 128, 1,024 and 100,000 labels, and I would include CPU preprocessing in the wall-clock budget.

The task suite should contain both aggregate-friendly entity forecasting and tasks where topology is difficult to flatten, such as link prediction, retrieval, recommendation or path-sensitive prediction.

[Point to the black band.]

For a RelGT-based foundation model, the papers suggest a hybrid design: a learned graph encoder, followed by normalization and a batch-level ICL head, with a cheap DFS aggregate branch retained as a residual or control.

My testable prediction is that an OpenRFM-like learned relational model should have its greatest advantage at low label budgets and on topology-dependent tasks. TabPFN-Rel should remain extremely strong when aggregate features capture most of the signal and abundant labeled context is available.

That is a hypothesis, not a result established by the current papers. The purpose of the common experiment is to try to falsify it.

### Closing question

The question I would leave for discussion is: **what task would most clearly demonstrate that retaining relational topology inside the foundation model provides value beyond a strong flatten-first system?**

---

## Optional 60-second summary

If the presentation must be shortened, the entire argument can be summarized as follows:

> OpenRFM diagnoses RT as a relation-level in-context learner whose performance is limited by reachable labels and by a lazy pretraining regime. It adds a TabICL batch-level support channel and a homophily-aware relational prior. TabPFN-Rel instead materializes DFS aggregates and uses a frozen TabPFN-3 model with a very large labeled context. OpenRFM is closer to a relational graph foundation model; TabPFN-Rel is a strong foundation-model-based relational system and the essential flattening baseline. Their published scores are not directly comparable, so the decisive next experiment must equalize temporal snapshots, labels, context size, ensembling and full pipeline compute.

## Likely audience questions

### Is TabICL the relational part of OpenRFM?

No. RT provides the relational representation. TabICL provides batch-level ICL across pooled query and support embeddings.

### Is TabPFN-Rel zero-shot?

It does not perform a downstream gradient update, but it uses a large labeled context including training and validation examples. “No-gradient, label-rich ICL” is more precise than “zero-shot.”

### Is OpenRFM directly evaluated on RelArena?

Not in the OpenRFM paper. It uses a different 24-task mixed suite and predates the public TabPFN-Rel release.

### Which method is a graph foundation model?

OpenRFM is closer because relational topology remains inside its pretrained encoder. TabPFN-Rel flattens topology before the foundation model sees the data.

### Why could TabPFN-Rel still outperform a graph-native model?

Many entity-forecasting tasks may be captured well by recency, historical aggregates and abundant labeled examples. A graph-native model must show value beyond those strong signals.

### What is the fairest first experiment?

Run both systems on the same RelArena snapshots at matched support sizes, including 1,024 labels, and report full preprocessing plus inference time. Then add a topology-dependent task family.

## Sources

- [OpenRFM](https://arxiv.org/abs/2606.04320)
- [RelArena-α / TabPFN-Rel / RPI](https://arxiv.org/abs/2608.16319)
- [RelArena repository](https://github.com/PriorLabs/relarena)
- [RelGT](https://arxiv.org/abs/2505.10960)
