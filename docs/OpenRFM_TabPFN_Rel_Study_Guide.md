# OpenRFM and TabPFN-Rel: A Study Guide

This guide explains the two systems at three levels:

1. **What happens from database input to prediction?**
2. **Where does relational reasoning happen?**
3. **What do the experiments establish—and what remains unproven?**

The short answer is:

> **OpenRFM learns a relational representation and then performs batch-level in-context learning. TabPFN-Rel constructs relational aggregate features and then applies a frozen tabular foundation model.**

They therefore represent two different routes toward reusable prediction over relational databases.

## 1. Essential terminology

### Relational database as a graph

A relational database can be viewed as a heterogeneous graph:

- A table or row type corresponds roughly to a node type.
- A primary-key/foreign-key relationship defines an edge type.
- Table columns provide node or event attributes.
- Timestamps determine which rows are available at a prediction cutoff.

This does not mean every relational model is a graph model. A system can either preserve this topology inside the model or collapse it into flat aggregate features before prediction.

### In-context learning

In-context learning, or ICL, means adapting predictions using labeled examples supplied in the model's input context, without performing a conventional gradient-based training run for the new task.

For relational prediction, there are at least two possible contexts:

- **Relation-level context:** rows and labels found near one query through relational links.
- **Batch-level context:** a collection of labeled examples from across the task table.

OpenRFM explicitly combines both. TabPFN-Rel primarily uses batch-level ICL after relational feature synthesis.

### Foundation model

For this discussion, a relational or graph foundation model should ideally provide:

- one reusable pretrained checkpoint;
- inference on unseen databases and schemas;
- little or no task-specific gradient training;
- adaptation from zero or a small number of labels;
- transfer across different tasks and database domains;
- evidence that relational structure contributes beyond strong flat-table baselines.

This is a demanding definition. “Uses a foundation model somewhere in the pipeline” is weaker than “is itself a relational graph foundation model.”

---

## 2. OpenRFM

Paper: [OpenRFM: Dissecting Relational In-Context Learning](https://arxiv.org/abs/2606.04320), June 2026 preprint.

### 2.1 What problem does OpenRFM diagnose?

OpenRFM begins with the Relational Transformer, or RT. For a target row, RT samples a relational neighborhood using a breadth-first-search-style random walk and converts that neighborhood into a token sequence.

The important reinterpretation is:

> RT's apparently “zero-shot” prediction is actually a form of relation-level ICL.

Some rows encountered in the sampled neighborhood belong to the task table and have known labels. Those labels become the support examples for the query. The RT prediction behaves approximately like kernel regression over this locally encountered support.

### 2.2 Label reachability

OpenRFM introduces **label reachability**, denoted by `ρ`, as a diagnostic for how readily a query's sampled relational context exposes labeled task-table rows.

When `ρ` is very small, the query has almost no useful in-context support. The paper gives representative examples:

| Task | Reachability | RT result | Stronger comparison |
|---|---:|---:|---:|
| `st-outc` | 0.002 | AUC 0.493 | JUICE 0.715 |
| `st-adv` | 0.006 | R² −0.017 | JUICE 0.470 |
| `driver-top3` | 0.893 | AUC 0.824 | High-reachability case |

The interpretation is not merely that longer contexts are always better. If the relational walk rarely reaches labeled examples, increasing sequence length may add mostly unlabeled or irrelevant rows.

### 2.3 The lazy-regime diagnosis

The paper also corrupts or shuffles relational features to test whether RT truly uses them.

The results suggest two regimes:

- **Lazy or frozen-feature regime:** predictions change little after relational features are corrupted. The model is not strongly using the relational structure.
- **Feature-learning regime:** predictions depend materially on relational features, suggesting that the pretrained model learned to extract relational signal.

The PluRel synthetic-pretrained RT often behaves like the first regime. Co-training or continued training on appropriate real relational data can move the model toward the second.

The key lesson is:

> A relational architecture does not guarantee relational reasoning. The pretraining distribution must make the relational signal necessary for solving the task.

### 2.4 OpenRFM's architectural solution: dual-stage ICL

OpenRFM adds a second support channel.

```text
For every query:
    sampled relational neighborhood
        ↓
    Relational Transformer blocks
        ↓
    pooled relational embedding

Across many queries and labeled support rows:
    normalized pooled embeddings
        ↓
    TabICL / TabPFN-style batch ICL
        ↓
    predictions
```

The two stages have different responsibilities:

1. **Relation-level ICL:** RT processes the relational context surrounding each query.
2. **Batch-level ICL:** TabICL-style attention compares the query with labeled examples sampled from across the task table.

The second stage helps when the query's local relational walk contains few reachable labels.

### 2.5 Why not use one large two-dimensional Transformer?

The authors tried a fully end-to-end design that jointly attended over relational context and the batch of examples. It reached a low training loss but failed badly on downstream regression, producing nearly constant predictions and an approximately −4.3 R² in the reported diagnostic.

The successful bridge is simpler:

- pool the RT representation;
- normalize it;
- pass it through the original TabICL encoder and ICL stack;
- optionally interleave a limited number of batch-ICL layers between RT blocks.

The bridge ablations suggest:

- normalization is critical;
- the original TabICL encoder is stronger than a simple linear adapter;
- interleaving provides inconsistent, task-dependent gains.

### 2.6 OpenRFM's pretraining solution

The authors argue that the synthetic pretraining prior needs a relational latent that can be identified from support examples.

They modify synthetic label generation by sampling a controllable **homophily latent** `h`. Because labeled support examples reveal whether neighboring or related rows tend to share labels, the model must use the support set to infer `h`.

The continued pretraining recipe combines:

- homophily-aware synthetic relational databases;
- selected held-out real relational databases;
- a prototype-style auxiliary loss for multi-class tasks;
- initialization from a PluRel-pretrained RT checkpoint.

An important ablation is that adding real data naively hurts. Performance recovers after introducing a better-structured objective. The conclusion is that real data volume alone is not enough; the training objective must expose reusable relational mechanisms.

### 2.7 What drives the reported gains?

The cumulative ablation is informative:

| Configuration | Binary AUC | MRR | R² |
|---|---:|---:|---:|
| RT-PluRel | 0.66 | N/A | 0.11 |
| + TabICL batch ICL | 0.76 | 0.58 | 0.12 |
| + homophily-aware synthetic data | 0.78 | 0.56 | 0.13 |
| + real data | 0.75 | 0.50 | 0.12 |
| + prototype loss | 0.79 | 0.58 | 0.14 |
| + eight-support ensemble | **0.80** | **0.58** | **0.23** |

The largest single classification improvement comes from adding batch-level ICL. Ensembling contributes especially strongly to regression.

Across the paper's 24-task mixed suite, OpenRFM reports a mean rank of 4.92, compared with 7.19 for RT-PluRel and 7.54 for RelGT. These are results under the OpenRFM evaluation suite, not RelArena Elo scores.

### 2.8 What OpenRFM does not yet prove

- It is a June 2026 version-one preprint.
- Its evaluation is not the same protocol or task set as RelArena-α.
- It uses a maximum TabICLv2 context of 2,048 rows and normally relies on support ensembling.
- Its context selection is query-agnostic.
- Continued pretraining includes selected real databases, complicating the cleanest zero-data-transfer interpretation.
- Multi-class scaling remains constrained by the tabular head.
- The paper does not establish superiority on recommendation, link prediction, retrieval, or arbitrary non-database graphs.
- It demonstrates a relational foundation-model direction more clearly than a universal graph foundation model.

---

## 3. TabPFN-Rel

Paper: [RelArena-α, TabPFN-Rel and RPI](https://arxiv.org/abs/2608.16319), August 2026 alpha release.

TabPFN-Rel is introduced as part of the RelArena-α paper rather than as a separate standalone paper.

### 3.1 What is TabPFN-Rel?

TabPFN-Rel is a relational harness for the frozen TabPFN-3 tabular foundation model.

It does not pretrain TabPFN-3 on relational schemas. Instead, it transforms a relational prediction task into a flat table that TabPFN-3 already knows how to process.

```text
Relational database at cutoff time
    ↓
enumerate PK/FK join paths
    ↓
Deep Feature Synthesis aggregates
    ↓
one flat row per entity and cutoff
    ↓
labeled context rows + query rows
    ↓
frozen TabPFN-3
    ↓
prediction
```

### 3.2 Deep Feature Synthesis

Deep Feature Synthesis, or DFS, recursively applies aggregation operations along relational join paths.

Examples include:

- count the related transactions;
- compute the mean purchase value;
- find the maximum score across related events;
- aggregate an aggregate over a two-hop path.

TabPFN-Rel tunes the maximum DFS depth over `{2, 3, 4}`. A larger depth exposes longer relational paths, but the number of possible paths and aggregate columns can grow rapidly.

The essential representational choice is:

> Relational topology is converted into columns before the foundation model sees the data.

TabPFN-3 therefore performs in-context learning over rows and columns, not over a graph or relational neighborhood.

### 3.3 Temporal evaluation and tuning

For relational prediction, preventing future leakage is essential. TabPFN-Rel improves the earlier RDBLearn workflow by separating two database snapshots:

- an inner database frozen at the validation cutoff for tuning DFS depth;
- an outer database frozen at the test cutoff for final evaluation.

The test-time context includes both training and validation labels. Therefore, TabPFN-Rel is best described as **no-gradient, label-rich adaptation**, not strict zero-shot prediction.

### 3.4 Released inference configuration

The reported configuration uses:

- eight estimators;
- `K = 100,000` labeled context rows per estimator;
- context sampled from the 400,000 most recent candidate rows;
- training plus validation examples in the test context;
- raw anchor-table text in the hosted API version;
- no text features in the open-source version.

This context is much larger than OpenRFM's usual 1,024-row support with eight ensembles. Any direct comparison must control the label budget.

### 3.5 RelArena-α results

On the 21 RelArena-α entity-forecasting tasks, the standardized model leaderboard reports:

| Method | Elo |
|---|---:|
| TabPFN-Rel API | **1821** |
| TabPFN-Rel OSS | 1706 |
| GraphSAGE | 1658 |
| RelGT | 1575 |
| RDBLearn | 1548 |
| RelGNN | 1506 |
| Per-entity constant | 1256 |
| Global constant | 1000 |

On the combined model-and-system board, RT-PluRel leads at 1861 and TabPFN-Rel API scores 1826. Thus the accurate statement is:

> TabPFN-Rel is the highest-ranked standardized model in that RelArena-α release, but not the highest-ranked overall submitted system.

TabPFN-Rel and RT-PluRel are the only evaluated methods that beat the per-entity constant baseline on all 21 tasks.

### 3.6 Why does the API version outperform OSS?

The API-to-OSS drop is 115 Elo points. The paper reports that much of this difference is concentrated in two text-heavy tasks:

- `rel-event/user-ignore`;
- `rel-avito/user-clicks`.

This suggests that raw text can be crucial on particular tasks but is not uniformly responsible for performance across the benchmark.

It also raises practical questions about:

- access to the hosted model;
- privacy of database text;
- reproducibility;
- licensing and deployment constraints.

### 3.7 What TabPFN-Rel does not yet prove

- It does not show that TabPFN-3 learned relational structure during pretraining.
- Its released benchmark covers 21 RelBench-v1 entity-forecasting tasks, not every relational task family.
- The leaderboard uses a single seed.
- CPU feature-synthesis cost is excluded from the headline model-runtime comparison.
- Deeper DFS can become expensive as join paths multiply.
- Timestamp-boundary behavior is not yet perfectly identical across all method families.
- A context of up to 100,000 labels per estimator is far from a low-label or zero-label setting.
- The 1821 Elo value is relative to the submitted leaderboard and should not be compared directly with OpenRFM's mean rank.

---

## 4. Side-by-side comparison

| Dimension | OpenRFM | TabPFN-Rel |
|---|---|---|
| Core idea | Learn relational embeddings, then use batch ICL | Engineer relational columns, then use tabular ICL |
| Where topology is represented | Inside the Relational Transformer | In DFS-generated feature columns |
| Relational pretraining | Yes | No in the TabPFN-Rel harness |
| Foundation component | RT relational backbone plus TabICL/TabPFN head | Frozen TabPFN-3 |
| Task adaptation | Labeled batch context; no per-task training | Large labeled table context; no gradient update |
| Typical reported support | 1,024, with eight ensembles | 100,000 per estimator, with eight estimators |
| Strength | Can preserve relational paths and interactions | Strong, simple and scalable when aggregates summarize the task |
| Weakness | Small context, complex pretraining, early evidence | Loses topology before modeling; expensive feature synthesis |
| Published evaluation | 24 mixed classification/regression tasks | 21 RelArena entity-forecasting tasks |
| Best label | Relational foundation-model prototype | Relational harness using a tabular foundation model |

## 5. Are they graph foundation models?

### OpenRFM

OpenRFM is reasonably described as a **relational foundation model with a graph-structured backbone**. It directly consumes PK/FK topology through sampled relational neighborhoods and reuses a pretrained checkpoint without per-task training.

It is not yet demonstrated as a universal graph foundation model across arbitrary graph modalities and task families.

### TabPFN-Rel

TabPFN-Rel is **not a graph foundation model in the strict sense**. It is a relational system built around a tabular foundation model. Graph or relational topology has already been converted into aggregate columns before TabPFN-3 receives the input.

This distinction does not make TabPFN-Rel weak. It makes it an especially important baseline: any graph foundation model should demonstrate that retaining topology provides value beyond this strong flatten-first pipeline.

---

## 6. Why the published numbers are not directly comparable

OpenRFM and TabPFN-Rel differ in:

- task suites;
- benchmark filtering;
- metrics and aggregation;
- label-context size;
- preprocessing cost;
- database snapshot implementation;
- supported task families;
- treatment of text;
- ensembling and random seeds.

In particular:

- OpenRFM reports mean rank over 24 mixed tasks.
- TabPFN-Rel reports Elo over 21 RelArena entity-forecasting tasks.
- OpenRFM usually uses 1,024 support rows times eight draws.
- TabPFN-Rel uses 100,000 rows times eight estimators.

Consequently, “4.92 versus 1821” is meaningless. They are different quantities under different protocols.

---

## 7. The experiment that would compare them fairly

A useful common evaluation would lock:

1. the same temporal database snapshots;
2. the same train, validation and test rows;
3. the same available text fields;
4. the same labeled-support budgets;
5. the same number of ensemble members;
6. full wall-clock and memory measurement, including preprocessing;
7. the same random seeds and uncertainty reporting.

Support curves should include at least:

```text
0, 8, 32, 128, 1,024 and 100,000 labels
```

The benchmark should contain both:

- aggregate-friendly entity-forecasting tasks;
- topology-dependent tasks such as link prediction, recommendation, retrieval and path-sensitive prediction.

A useful decomposition would evaluate:

```text
DFS features only
learned graph representation only
DFS + learned graph representation
each representation with the same batch-ICL head
```

That design would reveal whether differences come from representation, pretraining, context size or the prediction head.

---

## 8. Implications for a RelGT foundation model

The two papers suggest a practical hybrid:

```text
                         ┌─ learned RelGT/RT graph embedding ─┐
relational database ────┤                                    ├─ normalization ─ batch ICL ─ prediction
                         └─ cheap DFS aggregate residual ─────┘
```

### Components worth borrowing from OpenRFM

- Treat support reachability as a first-class diagnostic.
- Add batch-level ICL rather than relying only on labels encountered inside one neighborhood.
- Normalize relational embeddings before the tabular ICL bridge.
- Construct synthetic priors whose latent relational mechanisms are identifiable from support.
- Use corruption probes to verify that the model actually depends on topology.

### Components worth borrowing from TabPFN-Rel

- Use strict cutoff-aware database snapshots.
- Include strong DFS features as a control or residual branch.
- Use recent and diverse context selection.
- Make label budgets and preprocessing costs explicit.
- Evaluate through a shared benchmark such as RelArena rather than a private pipeline.

### Testable hypothesis

The following is a research hypothesis, not a result established by either paper:

> A learned relational model should have its greatest advantage at low label budgets and on tasks where topology, paths or interactions cannot be summarized reliably by aggregates. TabPFN-Rel should remain very strong when abundant labeled rows are available and DFS features capture most of the predictive structure.

---

## 9. Questions for a research-group discussion

1. Is support reachability an intrinsic property of the task, or mainly a weakness of RT's neighborhood sampler?
2. Would query-aware retrieval reduce OpenRFM's dependence on eight support ensembles?
3. Can a graph encoder and TabPFN-style ICL head be pretrained jointly without the two-dimensional optimization collapse?
4. Which RelBench tasks genuinely require topology rather than well-designed aggregates?
5. How should context-label count be included in the compute budget?
6. Should synthetic pretraining vary homophily alone, or include richer identifiable mechanisms such as heterophily, temporal causality and path motifs?
7. Can the API text advantage be reproduced with an open text encoder?
8. Does performance improve predictably as the number and diversity of pretraining databases increase?
9. What is the smallest experiment that would falsify the need for a graph-native foundation model?

---

## 10. Recommended reading order

### OpenRFM

1. Figure 1 and the abstract for the three-part thesis.
2. Section 3.1 for label reachability and the kernel-regression interpretation.
3. Section 3.2 for the lazy-versus-feature-learning diagnosis.
4. Section 4.1 for dual-stage ICL.
5. Section 4.2 for the homophily-aware pretraining prior.
6. Tables 5–7 for ablations and context selection.
7. The limitations and discussion before interpreting the headline ranking.

### TabPFN-Rel / RelArena-α

1. Figure 1 for the complete pipeline.
2. Section 2.2 for improvements over RDBLearn.
3. Figure 2 for the distinction between model and model-plus-system leaderboards.
4. Section 3.2 for text and baseline interpretation.
5. Section 3.3 and the appendices for tuning and runtime details.
6. The benchmark limitations before generalizing beyond entity forecasting.

## Primary resources

- [OpenRFM paper](https://arxiv.org/abs/2606.04320)
- [OpenRFM full HTML](https://arxiv.org/html/2606.04320)
- [RelArena-α / TabPFN-Rel / RPI paper](https://arxiv.org/abs/2608.16319)
- [RelArena-α full HTML](https://arxiv.org/html/2608.16319v1)
- [RelArena repository](https://github.com/PriorLabs/relarena)
- [RelGT paper](https://arxiv.org/abs/2505.10960)

The companion slide deck is `OpenRFM_TabPFN_Rel_Deep_Dive_2026.pptx` in the same directory.
