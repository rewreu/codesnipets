# RelGT Statistical Expert Routing Research Plan

Extend the existing multi-dataset RelGT foundation model, which already runs on RelBench, with neural experts selected using learned statistical context. Test whether this improves prediction on unseen databases beyond routing from node embeddings alone or simply adding model capacity.

The core plan takes **18 weeks**, with **3–4 additional weeks of contingency**. Evidence acquisition is an optional extension with a separate time allowance.

## Architecture changes

The main prediction pipeline is:

`Fixed graph sampling → shared RelGT layers → statistical-context expert routing inside RelGT → normalized node embeddings → pretrained tabular prediction head`

| Component | Planned change |
| --- | --- |
| RelGT backbone | Reuse the existing foundation-model setup and shared relational attention. Add expert modules after one or two late RelGT blocks. |
| Learned statistical context | Encode statistics such as missingness, feature dispersion, relation degrees, neighborhood variation, and temporal recency. Use a shared set encoder to summarize local sampled inputs and the current task’s support features and metadata across different schemas. |
| Neural experts | Start with four small residual feed-forward adapters that produce the same embedding dimension. Initially route target/entity tokens. Let specialization emerge during training rather than assigning expert roles in advance. |
| Router | Combine the current node embedding, local statistical context, and task-level context to select two experts per routed node. Combine their weighted outputs with the shared residual path. Execute only the selected experts. |
| Prediction head | Start with the complete pretrained TabICL model, keeping its weights frozen. Feed normalized RelGT embeddings as numeric features. Test TabPFN on a smaller compatibility experiment. Head LoRA is a later ablation. |
| Joint training | Warm up the new context encoder, router, and experts with RelGT frozen, then train them jointly with RelGT at a smaller backbone learning rate. Backpropagate prediction loss through the frozen head; verify that input gradients reach the graph model. Add mild expert-balancing and router-stability penalties. |

Keep graph sampling and available evidence identical across the main comparisons. Derive context from those sampled inputs and declared support features; query labels are used only for training loss or evaluation. Separate source-training, development, and final-test databases.

The main comparisons are shared RelGT, expert routing based only on node embeddings, and expert routing with learned statistical context. Include a dense adapter using the same context and controls matched for parameter count or active computation. Give the shared baseline the same source-training procedure through the frozen prediction head.

### Optional evidence acquisition

A separate controller can choose which database paths, columns, time windows, or records to retrieve before RelGT runs. This changes the input evidence; the main neural router chooses which experts process that evidence.

If included, compare fixed versus adaptive acquisition with both shared RelGT and expert-routed RelGT, producing four experimental conditions. Allow **2–3 extra weeks** for a basic variant using a reusable retrieval interface, or **4–6 extra weeks** for a learned controller built from scratch. Start this option after the core routing result is promising; it is excluded from the 18-week effort budget below.

## 18-week schedule and effort allocation

Effort is measured in **total team person-days**, with eight hours per person-day. Each row spans two calendar weeks; coding, experiment work, and analysis can proceed in parallel. Experiment effort includes preparing and monitoring runs, debugging failures, and collecting results, rather than GPU runtime alone.

| Weeks | Main activities and deliverable | Architecture and code | Experiments | Analysis and writing |
| --- | --- | --- | --- | --- |
| 1–2 | Reproduce the existing baseline; define database splits and fixed sampling; integrate the frozen head; verify gradients, prediction consistency, and memory use. | 8 | 3 | 4 |
| 3–4 | Implement statistical context, four residual experts, and top-two routing. Verify dispatch correctness, router/expert gradients, utilization, and no dropped nodes. | 10 | 3 | 2 |
| 5–6 | Train across source datasets. Test transfer to development databases against shared RelGT, embedding-only routing, and context-conditioned dense controls. | 5 | 7 | 3 |
| 7–8 | Tune context summaries, expert count, and routed blocks on a bounded development subset. Check capacity and compute fairness; select and lock the architecture. | 5 | 6 | 4 |
| 9–10 | Run the main classification experiments across tasks, support-label budgets, and independent training seeds. Collect prediction quality and compute measurements. | 1 | 10 | 4 |
| 11–12 | Complete routing, context, and capacity ablations; test the second head on a subset. Produce a full draft and lock the final evaluation protocol. | 2 | 7 | 6 |
| 13–14 | Evaluate the locked models on unseen final-test databases. Measure active computation, complete pipeline latency, and memory. | 1 | 8 | 6 |
| 15–16 | Analyze transfer, expert specialization, context usefulness, uncertainty, and failure cases. Prepare figures and reproducible result tables. | 1 | 4 | 10 |
| 17–18 | Incorporate internal review, resolve concrete remaining issues, and finish the manuscript, supplement, and reproducibility package. | 1 | 2 | 12 |
| **Total** | **18 calendar weeks** | **34** | **50** | **51** |

Total estimated effort is **135 team person-days**, or **27 person-weeks**:

- Architecture and code: **34 days / 6.8 person-weeks**.
- Experiments: **50 days / 10 person-weeks**.
- Analysis and writing: **51 days / 10.2 person-weeks**.

This assumes one dedicated researcher at approximately 40 hours per week, three helpers at approximately 10 hours each per week, and roughly 4–8 GPUs for parallel jobs. That provides about 31.5 gross person-weeks over the core schedule. Reserve the additional 3–4 weeks for integration problems, necessary reruns, and paper revisions. These are planning estimates to refine after the first two weeks of measured throughput.
