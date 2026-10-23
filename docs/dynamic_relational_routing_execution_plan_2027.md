# Statistical Neural Expert Routing Research Execution Plan

*RelGT foundation model experiments for a 2027 main conference*

Updated 22 October 2026  |  Planned start 26 October 2026

We will extend the working RelGT foundation model with neural experts selected by learned statistical context. The main hypothesis is that local and episode-level statistical information improves computation selection on unseen databases, beyond routing on hidden states and beyond simply adding model capacity. The core experiments keep graph sampling and available evidence fixed.

**The core research schedule is 18 calendar weeks, followed by 3 to 4 weeks of contingency. Evidence acquisition is a separate optional extension with its own implementation and experiment allowance. The recommended primary submission target is NeurIPS 2027; a reduced ICML option depends on early results and the verified deadline.**

## Starting point and scope

| **Item** | **Planning basis** |
| --- | --- |
| Already available | RelGT supports multiple datasets and runs on RelBench. Reuse the existing foundation backbone, training runner, and data pipeline. Check checkpoint exposure before claiming unseen-database transfer. |
| Primary architecture | A shared RelGT stem and attention backbone, learned statistical context, a neural router, small residual experts in selected blocks, and a normalized interface to a frozen tabular predictor. |
| Core isolation | Use the same sampled records, neighborhoods, temporal cutoffs, and feature availability across neural-routing arms. Expert routing changes neural transformations. |
| Optional acquisition | A separate controller may choose database paths, columns, windows, or row budgets before retrieval. Its benefit is tested independently and jointly with neural routing. |
| People and compute | One dedicated lead plus three helpers assumed at 8–12 hours weekly each; 4–8 GPUs as a planning envelope. Measure actual memory, throughput, and availability. |
| Prediction head | Pinned whole-model TabICLv2, frozen in the primary condition. TabPFN is a second-head check. Head LoRA remains an optional later ablation. |

## Calendar targets

| **Milestone** | **Target** |
| --- | --- |
| Working expert routing and gradients | By 22 November 2026, end of week 4 |
| Initial transfer result | By 6 December 2026, end of week 6 |
| Architecture selected | By 20 December 2026, end of week 8 |
| Core paper and reproducible results | By 28 February 2027, end of week 18 |
| Core contingency complete | By 28 March 2027, end of week 22 |

All time estimates and success thresholds are planning assumptions. Acceptance is an external outcome. The acquisition proposal remains a source for the optional extension [9], rather than the specification of the primary routing mechanism.

## Architecture changes and code ownership

The initial design preserves RelGT’s shared attention and relational message processing. Add four small, same-shaped residual expert adapters after one or two selected late blocks. Begin by routing target/entity tokens; broader token routing is a later profiling choice. Each expert maps to the same hidden dimension and retains the shared residual path.

Fixed graph sampling → shared RelGT stem → node states and learned statistical context → top-two expert routing inside selected RelGT blocks → shared node representations → normalization → full frozen TabICLv2.

| **Component** | **Concrete modification** | **Owner** |
| --- | --- | --- |
| Existing pipeline | Reuse the current multi-dataset setup. Pin source/development/final databases, episode IDs, temporal visibility, sampling seeds, and pretrained checkpoint exposure. | Lead + C |
| Statistical context | Encode local structural/temporal summaries and a bounded episode support-covariate summary. Pool variable columns and relation roles through shared set encoders. | Lead + B |
| Expert adapters | Insert four small residual adapters in one or two shared blocks. Preserve backbone weights at initialization with a small residual contribution; output a common hidden space. | B |
| Neural router | Score experts from current node state, local context, and episode context. Start with top-two weights and dispatch only selected experts after correctness checks. | Lead |
| Training integration | Train router, statistics encoder, and experts through query loss; then unfreeze the source-clean RelGT backbone with a smaller learning rate. Keep the predictor frozen. | Lead + A |
| Head interface | Use normalized numeric node representations through the full tabular model. Verify input gradients, frozen head state, deployment parity, and backward memory. | A |
| Evaluation and profiling | Implement dense/static/random/hidden-state routing controls; log active and total parameters, FLOPs, dispatch, expert use, memory, latency, and prediction quality. | C + B |

### Expert design

The first experts are learned feed-forward transformations of representations that already contain relational and temporal information. Their specialization is an experimental question. They are not assigned labels such as temporal expert or fraud expert in advance. Attention experts or different receptive-field branches are later architecture variants if the simple adapters show a useful signal.

Keep expert outputs in a shared basis with a common residual path, final normalization, and prediction interface. This reduces the risk that different routing patterns create incompatible feature meanings for the frozen head. Retain the full head initially; OpenRFM found benefits from its original TabICL encoder in a related relational setting [6].

## Learned context and expert training

### Statistical inputs and a learned summary

Use a shared encoder over a variable-size set of descriptors. Initial inputs may include numerical distribution sketches, missingness, feature diversity, relation-degree summaries, neighborhood dispersion, and visible temporal recency. Pool these descriptors into a learned context vector. Compare this with feeding fixed summary statistics directly; the learned summarizer must earn its added complexity.

Derive local summaries only from the fixed sampled input. Build episode context from declared support covariates and metadata. The shared stem supplies states before expert selection, avoiding a need to run all experts first. Extra database scans are separately labeled information-access variants, with their evidence and cost matched across relevant controls; they are excluded from the core context.

Use datatype and relational-role encodings that can handle unseen schemas. The primary router does not require dataset IDs. Keep a statistics channel before normalization when normalization would erase scale or dispersion information; compare normalized and raw summary channels on development databases.

### Support labels and task context

The default statistical context uses covariates and metadata. A label-aware task summary is an explicit additional factor. For its first diagnostic, use a historical context-support pool separate from head supports, and count the unique union of labels. Do not append a head-support row’s own target to its node input. Reusing legitimate support labels can be studied later with an explicit protocol. Final query labels enter only the loss or evaluation.

### Routing and the learning objective

For each routed node, the router scores four experts from its shared state and context. Keep the two selected scores, normalize them, and add the weighted adapter outputs to the shared block output with a small learned or fixed residual scale. All expert outputs have the same dimension.

Optimize query prediction loss plus small expert-balancing and router-logit stability penalties, selected on unseen development databases. Switch Transformers and ST-MoE provide starting formulations [4,5]. Balance across suitably mixed source episodes; forcing every task to use all experts equally can defeat useful specialization.

Top-two routing gives gradients through selected mixture weights, while selected membership remains discrete. A normalized top-one weight becomes one, so ordinary task-loss gradients to router logits can vanish in that implementation. Verify router and expert gradients explicitly. Track utilization, gate entropy, output diversity, gradient norms, and dropped nodes; prefer a dispatcher that never drops graph nodes.

Warm up the new adapters/router with the pretrained backbone fixed, then train them jointly with RelGT at a lower backbone learning rate. The frozen head still needs input gradients. If that path fails, use a verified differentiable head; a proxy-head training regime is a separately labeled fallback, not an equivalent end-to-end result. Source acquisition teachers are unnecessary for the primary neural router.

## Eighteen week schedule and effort allocation

Each phase occupies two calendar weeks. The numeric columns estimate total team person-days at eight hours per day, within that phase. Jobs can run overnight or on separate GPUs. The 18-week core excludes optional acquisition development.

| **Weeks and dates** | **Primary deliverable** | **Code** | **Runs** | **Analysis and writing** |
| --- | --- | --- | --- | --- |
| 1–2<br>26 Oct–8 Nov | Fixed-sampling baseline, clean source exposure, head gradients/parity, and profiler | 8 | 3 | 4 |
| 3–4<br>9–22 Nov | Residual experts, statistical context, top-two dispatcher, and gradient/utilization checks | 10 | 3 | 2 |
| 5–6<br>23 Nov–6 Dec | Multi-source training and development transfer against hidden-only/dense controls | 5 | 7 | 3 |
| 7–8<br>7–20 Dec | Bounded architecture tuning, context/routing attribution, architecture lock | 5 | 6 | 4 |
| 9–10<br>21 Dec–3 Jan | Main classification runs, support curves, and independent training seeds | 1 | 10 | 4 |
| 11–12<br>4–17 Jan | Mechanism controls, second-head subset, draft, and final protocol lock | 2 | 7 | 6 |
| 13–14<br>18–31 Jan | Locked final databases and active-compute/end-to-end cost measurements | 1 | 8 | 6 |
| 15–16<br>1–14 Feb | Expert interventions, uncertainty, failure analysis, figures, and reproducibility | 1 | 4 | 10 |
| 17–18<br>15–28 Feb | Internal critique, targeted verification, manuscript and supplement | 1 | 2 | 12 |
| Total | 18 calendar weeks and 135 team person-days | 34 | 50 | 51 |

The workload is about 27 person-weeks: 6.8 for architecture/code, ten for experiment work, and 10.2 for analysis/writing. The capacity case is a 40-hour lead plus three helpers at ten hours weekly, giving 31.5 gross person-weeks over 18 weeks. At 35 lead hours and eight hours per helper, extend to about 20–22 core weeks, use contingency, or narrow scope.

### Parallel ownership and dependencies

The lead owns the scientific hypothesis, router, source training, decisions, and paper. A owns head gradients/parity and second-head checks. B owns expert adapters, dispatcher, context instrumentation, and profiling. C owns baselines, manifests, aggregation, and uncertainty. Optional acquisition work requires a separate allocation rather than silently reusing fully assigned helper time.

Critical path: verified query gradients → functioning expert/context routing → incremental development transfer → architecture lock → main evaluation → untouched final databases → analysis and paper. Extra GPUs shorten seeds and independent controls, not this decision chain.

Prepare resumable queues for reduced staffing on 23–29 November and 21 December–3 January. Reserve 1–28 March for core contingency; the acquisition option has an additional schedule in [Optional evidence acquisition extension](#optional-evidence-acquisition-extension).

## Weeks one through four

### Weeks one and two establish the fixed sampling baseline

Reproduce one run on the actual modified RelGT branch. Pin the sampler, target masks, support/query construction, and temporal cutoffs. Export node features and integrate a whole-model TabICLv2 checkpoint. The main experiments use identical sampled evidence across routing arms, with paired sampling/support seeds.

A verifies finite nonzero gradients from query loss into both intended input paths and a small upstream module; the entire head state must remain unchanged. Compare tensor training and deployment outputs under matched preprocessing, ensembles, and dropout. Measure forward/backward memory and one complete source episode.

If the TabICL path cannot be verified within this phase, prioritize a verified TabPFN tensor path. If neither fits or matches deployment, record a proxy-head training condition with a narrower claim and reset the timeline. A black-box head reward does not supply ordinary gradients to neural experts.

C reproduces the current shared RelGT baseline and selects runnable dense/context and external relational comparators by day 10. Cap initial external-baseline integration at three team person-days before documenting a fallback. B adds active-parameter/FLOP and dispatch traces. The lead records source, development, and final database partitions.

Audit encoder training exposure. If the existing checkpoint saw final databases, use the working pipeline to train a clean source-only checkpoint or choose genuinely unseen databases. This is checkpoint retraining, not a rebuild of the completed foundation-model setup.

### Weeks three and four implement and validate neural routing

Insert four residual adapters after one or two late RelGT blocks. Initially route target/entity tokens. Implement a shared-stem statistics summary and top-two gating. Retain the shared backbone path and a common output dimension. Use small residual contributions and different expert initializations to preserve stability without permanently identical experts.

First compare a tiny dense reference implementation with sparse dispatch on the same tokens and weights. Check output agreement, task gradients to selected gate logits and experts, reproducibility, and no dropped nodes. Profiling must show whether unselected experts actually avoid computation; a mask applied after all experts run is not sparse execution.

Run small source/development tasks. Compare the existing backbone, hidden-state-only routing, and statistical routing. Diagnose expert starvation, one-expert domination, dead gates, and head-interface instability before broad training. A short dense/noisy warm-up or mild balancing is a bounded intervention, not a guaranteed solution.

**Exit criterion at week 4: a numerically correct expert block, verified gradients, usable utilization, and measured overhead. The acquisition-oracle gate from the previous version is replaced by this neural-routing gate.**

## Weeks five through eight

### Weeks five and six test transferable expert selection

Train the context encoder, router, and experts on mixed source episodes. Start with a short frozen-backbone warm-up; then unfreeze RelGT at a smaller learning rate. Keep the tabular head fixed and differentiable. Use query loss plus a small source-development-selected balancing/stability penalty.

Continue training the shared RelGT baseline through the same frozen head, source episodes, data exposure, and backbone-unfreezing schedule. Comparing an adapted expert model only against an untouched older checkpoint would confound routing with head-aware source adaptation. Report any differences in training FLOPs.

The decisive controls are hidden-state-only routing with identical experts and active computation, and a dense adapter conditioned on the same statistical context. The first tests the statistical signal; the second tests whether useful context alone explains the gain. Include the existing shared RelGT baseline under the same head and evidence.

Use whole development databases excluded from source learning. Record global and per-task expert usage, effective expert count, gate entropy, gradient norms, prediction quality, active FLOPs, and end-to-end latency. Dataset-specific routing patterns alone do not demonstrate transferable specialization.

**Exit criterion at week 6: statistical routing adds repeatable held-out-development value beyond hidden-state routing or context-conditioned dense processing, with acceptable overhead. If it does not, allow one bounded revision of context granularity, routed block, or training stabilization before scaling.**

### Weeks seven and eight select the smallest useful architecture

Compare learned versus fixed statistical summaries, local versus episode context, and node-level versus task-level gating on a small predeclared development subset. Start with four experts/top two. Test two or eight experts, one versus two routed blocks, and a small regularizer grid only where the pilot identifies a clear uncertainty; avoid a full Cartesian sweep.

A parameter-matched dense model and an active-compute-matched dense model are different controls. Include both when feasible and report what each matches. Keep source data exposure and optimization budgets comparable. Static/random assignment with the same experts provides an additional sparse control.

The optional label-aware task summary uses only permitted historical labels, with explicit support accounting. Keep it separate from the main unlabeled statistical-context claim. Perform anonymous-schema and changed-statistics tests on development data to detect database-name shortcuts.

Lock the experts, selected blocks, context features, support protocol, and regularizers by 20 December. Prepare the main run queue and a central comparison table. Start the manuscript method/protocol sections in week 4 and have a results outline by week 8.

### Extensions after the core signal

Evidence acquisition is optional and separately budgeted. Attention experts, expert-specific receptive fields, prediction-head LoRA, persistent memory, and large expert-parallel infrastructure are later variants. The core study should first show that statistical context improves neural expert selection inside the existing RelGT.

## Weeks nine through eighteen

### Weeks nine through twelve run the main experiments

Run the shared RelGT baseline, hidden-state-only expert routing, and statistical expert routing across the declared classification tasks, three support budgets, and three source-training seeds. Pair support draws, query rows, sampled evidence, cutoffs, and final head settings. Keep a fixed evidence budget in the primary comparison.

Use the holiday period for queued, resumable jobs. In weeks 11–12, complete reduced mechanism controls and the second-head subset. Change only the head first when testing compatibility of fixed trained embeddings; separately adapting source models for a second head answers a different question. A small regression subset is optional after the central classification evidence is complete.

By 17 January, produce a complete first draft and lock checkpoints, preprocessing, evaluation code, support budgets, statistical tests, and the named final second-head/robustness subsets. Architecture selection ends earlier at week 8. Do not select final subsets after observing their outcomes.

### Weeks thirteen and fourteen evaluate final databases

Run the locked protocol on whole databases excluded from encoder/router/expert source training and all development selection. Use the source-clean checkpoint identified in week 1. Record any disclosed tabular-head pretraining exposure without claiming unknown contamination has been excluded.

C manages paired result manifests, B measures active FLOPs and complete latency/memory, and A verifies frozen-head behavior. Document infrastructure bugs and affected reruns. A method change driven by final outcomes makes that result exploratory and needs fresh confirmatory data.

### Weeks fifteen and sixteen analyze the mechanism

Report paired task differences, aggregate within databases, and use database-level or hierarchical uncertainty. Distinguish training seeds from support draws. With few independent databases, show all per-database results and leave-one-database-out sensitivity. Use AUROC as the primary binary-classification metric and log loss as a secondary metric.

Test expert removal, fixed/random gate replacement, and statistical-context shuffling as diagnostic interventions, with compute changes disclosed. Analyze when statistical context helps beyond hidden states, when experts collapse or become redundant, and whether patterns transfer across schemas. Gate heatmaps show behavior; they are not proof of semantic specialization.

Prepare four main figures: architecture and context flow, held-out transfer differences, quality versus active compute/end-to-end latency, and expert/context intervention results. Put detailed support curves and additional controls in the supplement. Package configuration hashes, checkpoints, exposure records, raw results, and scripts for the central tables.

### Weeks seventeen and eighteen finish the paper

Obtain internal reviewer-style feedback on novelty, statistical-context attribution, capacity fairness, and transfer. Reserve targeted verification for changed code, failures, or concrete unresolved concerns. Finish the anonymous manuscript, supplement, reproducible example, and eventual conference checklist/template requirements.

Target a complete core package by 28 February, with 1–28 March as contingency. The main paper can stand without evidence acquisition. If acquisition is added, its experiments and extra schedule must remain separately identifiable.

## Core experiments and analysis requirements

Pin the actual RelBench release and runnable manifest. A scope target is 12–20 classification task instances across 6–8 independent databases if supported by the current pipeline; these are planning targets, not benchmark release counts. Separate source, development, and final databases before episodes. Reserve at least two final databases where possible and audit aliases/exposure.

| **Experiment** | **Comparison and purpose** | **Scope** |
| --- | --- | --- |
| Three central systems | Shared RelGT, hidden-state-only MoE, learned statistical-context MoE; same evidence and frozen head | Full main task list, three support budgets, three training seeds |
| Useful context versus routing | Same statistics conditioning a single dense adapter or FiLM-style modulation | All named final tasks at the primary budget; paired seeds |
| Capacity and compute | Parameter-matched dense and active-FLOP-matched dense controls; identify which constraint each matches | Primary budget; report training and inference overhead |
| Assignment controls | Static/random top-two allocation with the same expert set; learned dense mixture as a diagnostic | Primary budget, paired seeds |
| Statistical mechanism | Hidden-only, fixed versus learned summaries, shuffled context, local/episode context, optional label-aware summary | Reduced declared subset; avoid full cross-products |
| Transfer and compatibility | Unseen database/schema/task checks, second frozen head, small regression subset | Subsets named before final outcomes |
| External context | Current RelGT foundation setup, compatible relational/TFM baseline, and one released competitive RFM | C selects runnable comparators by week 2 |

### Run counts and comparison rules

For 12 task instances, three central systems × three support budgets × three training seeds produce 324 evaluation cells. Six extra controls at one budget add at most 216 cells before deduplication. These are evaluation cells, not 540 independent source-pretraining runs. Add second-head and extension cells separately.

Use total historical label budgets such as 32, 128, and 512, subject to memory measurements. The main unlabeled statistics summary uses support covariates without additional labels. A label-aware context pool is counted in the unique label union, and static baselines may use the same total label budget. Never expose final query labels to the router, node features, or context.

Hold the input graph and sampler fixed for the main comparison. Report total parameters, active parameters, estimated FLOPs, observed latency, memory, and dispatcher overhead. Sparse experts can improve capacity without making the complete RelGT-plus-TFM system faster. Predeclare any matched-quality tolerance, initially 0.005 AUROC subject to source-pilot revision, before final tests.

Track utilization across mixed-source batches and individual tasks, gate entropy, expert-output diversity, gradient norms, and node drops. Test future-record invariance and anonymous schema names. Select context and regularizers only on development databases; report worst-database regressions as well as mean improvements.

## Optional evidence acquisition extension

Evidence acquisition changes which records, paths, columns, or time windows are retrieved before RelGT. Neural expert routing changes which transformations process an already sampled input. Keep separate controllers, logs, and claims. The existing acquisition proposal provides candidate designs [9].

Optional combined flow: permitted task/schema sketches → acquisition controller → selected evidence → shared RelGT stem and statistical context → neural expert routing → normalized node representations → frozen tabular predictor.

### A staged option with a separate time allowance

| **Option** | **Implementation and experiment** | **Extra calendar allowance** |
| --- | --- | --- |
| Basic adaptive acquisition | Reuse an available retrieval interface or add a small bounded heuristic for FK paths, temporal windows, and row caps. Compare under measured equal evidence/total cost. | About 2–3 weeks if the needed executor is already simple or reusable; re-estimate after a spike. |
| Learned acquisition | Build a finite candidate-program scorer and executor if missing. Train from source-only candidate rewards, validate on unseen development databases, and count sketch/teacher costs. | A separate 4–6-week project allowance if built from scratch; not promised within the basic option. |
| Interaction analysis | Run fixed/adaptive acquisition × shared/expert-routed RelGT with the same head, support exposure, and declared training budgets. | Included only if the selected option has capacity for all four arms; otherwise report it as deferred. |

### The four arm comparison

| **Acquisition** | **Shared RelGT** | **Statistical expert RelGT** |
| --- | --- | --- |
| Fixed baseline sampling | A  Core baseline | B  Core neural-routing model |
| Adaptive acquisition | C  Acquisition alone | D  Combined model |

B versus A tests neural routing with identical evidence. C versus A tests acquisition with shared computation. D versus C tests neural routing under adaptive evidence; compare this with B versus A to study interaction. Train each included arm with comparable source exposure and optimization budgets. A fixed-checkpoint plug-in study is a separate, cheaper diagnostic.

An acquisition controller must make its expensive retrieval choices using only permitted pre-retrieval sketches; it cannot first encode every candidate branch. Share task-level route definitions across support and query rows, or explicitly re-encode supports under each query route. Preserve temporal visibility, relation direction, stable feature meaning, and total label accounting.

Start the basic option only after the week-8 neural-routing gate passes, with an explicit owner and additional capacity. A sequential 2–3-week option after the core ends could run 1–21 March; preserve a further 3–4 weeks of core recovery/review afterward. A learned acquisition project can extend the calendar into April/May and requires checking the actual submission window.

Acquisition is not a prerequisite for the main result. If extra retrieval, target-task search, or new labels explain its gains, narrow the extension claim. Do not delay the neural-routing paper solely to add this option.

## Resources and conference strategy

Plan around a 40-hour research lead and three helpers near ten hours weekly each, with 4–8 GPUs for independent jobs. At lower helper availability, use the contingency or extend the core to 20–22 weeks. GPU type, memory, and actual RelGT/head episode latency remain to be measured.

| **Job family** | **Allocation from the same GPU pool** | **Main measurement** |
| --- | --- | --- |
| Integration and sparse dispatch | One GPU while debugging | Head/backbone/router gradients, parity, node handling, and peak memory |
| Source training | One or two GPUs per run when justified | Step latency, validation cadence, checkpoint cost, and mixed-source balance |
| Independent seeds and controls | Remaining GPUs as separate workers | Matched data/optimization budgets and active computation |
| Final evaluation | Parallel tasks/support draws when valid | Full sampled-input, context, expert, and frozen-head latency/memory |
| Optional acquisition | Separate allocation after core needs | Sketch, retrieval, rejected plan, and selection costs |

Replicate the initial four small experts on each GPU; avoid expert-parallel all-to-all infrastructure unless profiling shows a need. Report shared-backbone and TFM cost separately from expert cost. Cached training embeddings become invalid when the backbone/router changes. A frozen head saves optimizer state but still requires activation memory for upstream training.

Forecast source training from measured step time × steps per run × systems × seeds. For illustration, three systems × three seeds × 10,000 steps × one second per step is 25 one-GPU worker-hours. This is not a throughput estimate for the current model; replace it after week 2 and add a 25–35 percent job allowance for failures and necessary replication. Distributed runs also consume multiple GPU-hours per wall-clock hour.

### Submission windows

| **Venue** | **Evidence available on 22 October 2026** | **Decision** |
| --- | --- | --- |
| ICLR 2027 | Official full-paper deadline was 25 September 2026 [10]. | Already closed for a new submission. |
| ICML 2027 | Exact 2027 deadline unverified. ICML 2026 abstract/paper dates were 23/28 January [11]. | Conditional reduced-scope late-January planning window. |
| NeurIPS 2027 | Exact 2027 deadline unverified. NeurIPS 2026 abstract/paper dates were 4/6 May [12]. | Recommended primary target using a provisional early-May window. |

An approximately 13-week ICML sprint keeps one or two expert blocks, four experts/top two, fixed sampling, one head, binary classification, and essential capacity/context controls. It still trains neural experts and the router; it does not revert to the acquisition-policy design. Defer acquisition, broad regression, head LoRA, and extensive source retraining for multiple heads. Decide by week 8 only if the verified deadline and evidence permit.

Aim for the core internal package by 28 February and recovery/review by 28 March. Conference deadlines and acceptance are external constraints, not guaranteed milestones. Recheck official calls before finalizing submission dates and templates.

## Decision points and first ten working days

| **When** | **Evidence required** | **Response if absent** |
| --- | --- | --- |
| Week 2 | Head-to-input/backbone gradients, unchanged head state, deployment parity, feasible memory | Prioritize a verified differentiable head. A proxy-head regime needs an explicit claim and timeline change. |
| Week 4 | Correct expert dispatch, nonzero gate/expert gradients, no dropped nodes, usable utilization | Fix integration/stability; compare dense reference dispatch; cap expert count and routed blocks. |
| Week 6 | Statistical routing adds development transfer beyond hidden-only and context-dense controls | One bounded context/training revision before broad scaling. Do not use acquisition to hide a weak neural result. |
| Week 8 | Selected architecture and fair capacity/context attribution | Lock the simplest supported model. Start acquisition only with a separate allocation. |
| Week 12 | Main development evidence, full draft, frozen final protocol/subsets | Use contingency for missing essentials before final outcomes. |
| Weeks<br>14–18 | Held-out transfer, expert/context analysis, costs, and reproducibility | Narrow unsupported claims; method changes need fresh confirmatory data. |

### First ten working days

| **Days** | **Lead and parallel assignments** | **Output** |
| --- | --- | --- |
| 1–2 | Lead audits checkpoint exposure and splits. A pins the head. B locates safe residual insertion points. C reproduces one existing fixed-sampling RelBench result. | Baseline and exposure ledger |
| 3–4 | A builds the tensor prediction/loss path. B creates a shared residual adapter stub. C pairs support/query and sampler manifests. Lead defines local/episode context inputs. | Tiny differentiable episode |
| 5–6 | A checks state, input gradients, parity, and memory. B prototypes four experts and dense-reference dispatch. Lead checks router gradients. C defines dense/hidden-only controls. | Gradient and dispatch report |
| 7–8 | B adds sparse top-two dispatch and utilization logs. Lead adds learned set pooling over visible statistics. A verifies gradients across integration. C profiles matched inputs. | Statistical expert prototype |
| 9–10 | Team reviews source-clean checkpoint needs, training stability, baselines, and measured run budget. Assign week-3 small-task experiments and owners. | Week-4 gate experiment ready |

Maintain a result ledger with source exposure, checkpoint/code hash, source training seed, episode/support/query IDs, sampler seed, cutoff, expert count/top-k, routed blocks, context inputs, regularizers, active/total compute, utilization, memory, latency, metrics, and failures. Keep acquisition fields separate and label extension runs explicitly.

This revision makes learned statistical-context neural routing the primary study. The existing acquisition document remains an optional evidence-selection design. The working multi-dataset RelGT and RelBench setup are reused throughout.

## Sources and evidence boundaries

The user’s working RelGT foundation setup and clarified neural-expert objective define the scope. Architecture settings, time allowances, and numerical thresholds are recommendations rather than measured results. Related work establishes overlap, not novelty or guaranteed transfer.

[\[1\] AnyGraph Graph Foundation Model in the Wild.](https://arxiv.org/html/2408.10700v1)

Graph foundation MoE with graph-level competence routing. Relevant precedent for heterogeneous graph domains; the proposed study tests statistical context inside a relational transformer.

[\[2\] GraphMETRO Mitigating Complex Graph Distribution Shifts via Mixture of Aligned Experts.](https://arxiv.org/abs/2312.04693)

A gate identifies graph distribution-shift components and experts are representation-aligned. Distribution-conditioned graph expert routing is established prior work.

[\[3\] EvoFG Evolutionary Router Feature Generation for Zero-Shot Graph Anomaly Detection.](https://arxiv.org/abs/2602.11622)

Structural router features and transferable graph MoE are directly relevant. Its anomaly setting and generated features differ from the proposed learned relational context; this summary uses its primary abstract.

[\[4\] Switch Transformers.](https://arxiv.org/abs/2101.03961)

[\[5\] ST-MoE Designing Stable and Transferable Sparse Expert Models.](https://arxiv.org/abs/2202.08906)

Starting references for sparse dispatch, balancing, and router stability. Their coefficients, scale, and speed results are not assumed to transfer to RelGT.

[\[6\] OpenRFM Dissecting Relational In-Context Learning. Section 5.3.](https://arxiv.org/html/2606.04320v1#S5.SS3)

Supports retaining normalization and a full TabICL frontend as a starting interface in a related relational setup. It does not establish a universal result for RelGT embeddings.

[\[7\] Official TabICL implementation.](https://github.com/soda-inria/tabicl)

[\[8\] Official TabPFN input-gradient example.](https://github.com/PriorLabs/TabPFN/blob/main/examples/input_gradients.py)

Pin exact code and checkpoints. Verify gradients, frozen buffers/weights, deployment parity, and memory on the actual integration.

[\[9\] Dynamic Relational Routing with Frozen Prediction Heads. Original acquisition proposal.](/Users/zhewu/Documents/Research/research_plans/dynamic_relational_routing_2026_10_22.docx)

Used for the optional pre-retrieval evidence-selection extension. It no longer determines the primary neural-routing architecture or training objective.

[\[10\] ICLR 2027 official call for papers.](https://iclr.cc/Conferences/2027/CallForPapers)

[\[11\] ICML 2026 official dates and deadlines.](https://icml.cc/Conferences/2026/Dates)

[\[12\] NeurIPS 2026 official dates and deadlines.](https://neurips.cc/Conferences/2026/Dates)

Verified historical dates are recorded in [Submission windows](#submission-windows). Official ICML/NeurIPS 2027 submission deadlines were not verified on 22 October 2026; the 2027 windows are planning estimates.
