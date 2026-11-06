# Kumo-Relational embedding examples

Extract two kinds of customer embeddings from the pretrained
[NVIDIA Kumo-Relational model](https://huggingface.co/nvidia/Kumo-Relational).
`example_embeddings.py` is a standalone script: it creates its own mock tables,
loads the model, extracts embeddings, verifies them, and saves the results.
It needs no database server, API key, previous example, or training step.

**Labeled context is required.** This example supplies eight labeled customers
and embeds four other customers whose labels are not supplied. It demonstrates
embeddings for unlabeled query entities, not a completely label-free encoder.

## 1. Install

Use Python 3.12 on Linux or WSL. From this directory:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip

# CPU installation:
python -m pip install torch==2.7.1 --index-url https://download.pytorch.org/whl/cpu
python -m pip install -r requirements.txt
```

For an NVIDIA GPU, replace the CPU PyTorch command with a compatible CUDA build.
The environment used for the original GTX 1080 Ti example uses:

```bash
python -m pip install torch==2.7.1 --index-url https://download.pytorch.org/whl/cu118
```

The extraction depends on SDM internals, so `structured-data-models` is pinned
to **0.2.1**. The first run downloads approximately 120 MB of classifier weights
from Hugging Face; later runs reuse the local cache. The checkpoint is pinned to
commit `2bd603d3d8f25f67a7aaa8579908595e20567e22` (v1.0.1), verified by SHA-256,
and loaded using `weights_only=True` and strict parameter matching.

## 2. Run either example

Run these commands from `graph/kumo`:

```bash
# Example A: representations immediately after the GNN and customer readout.
python example_embeddings.py --embedding relational --device cpu --output output/relational

# Example B: representations immediately before the prediction head.
python example_embeddings.py --embedding contextual --device cpu --output output/contextual

# Extract both during the same model call; automatically select CPU or CUDA.
python example_embeddings.py --embedding both
```

Use `--device cuda` to select the GPU explicitly. Each extraction also runs an
ordinary forward pass with the same seed to check that the hooks leave the
prediction probabilities unchanged. This is a small extraction example, not
an accuracy or performance benchmark.

The default seed is 42; change it with `--seed`. The `--embedding` option selects
which vectors to save; all modes keep the complete prediction path intact.

## 3. Understand the inputs and capture points

The script builds three related tables and a separate context-label table:

```text
customers.customer_id  ←  orders.customer_id
                      ←  support_tickets.customer_id
```

Primary and foreign keys are declared as SDM `id` columns. The relationships
and task-to-customer link are specified through `sdm.RelatedTables`. The eight
context customers and four query customers have separate FK neighborhoods.
Only the context customers have labels passed to the model.

```text
Customer, order, and support-ticket features + labeled context
    ↓
Row embeddings
    ↓
GNN message passing + customer readout
    ↓
relational_embeddings          ← capture here
    ↓
In-context-learning (ICL) transformer
    ↓
Final LayerNorm
    ↓
contextual_embeddings          ← capture here
    ↓
Prediction head
```

Both outputs have shape **`(4, 512)`**: one vector for each query customer.
The model concatenates four readout tokens with 128 channels each, giving 512
dimensions. This width does not depend on the number of database columns.

The two temporary PyTorch hooks are attached to
`model.models["classification"].icl_block` and `.icl_block.head`:

- The first copies the query rows from the ICL block's input, after GNN readout.
- The second copies the prediction head's input, after ICL and final normalization.

The prediction head stays intact. Activations are copied before subsequent
in-place operations, and hooks are removed in a `finally` block. The example
uses one estimator so there is one unambiguous vector per customer and stage.

## 4. Load the results

With the default `--embedding both`, outputs are written beside the script in
`output/`. A custom `--output` selects a different destination.

```python
import numpy as np

data = np.load("output/query_embeddings.npz")
customer_ids = data["customer_ids"]
relational = data["relational_embeddings"]  # (4, 512)
contextual = data["contextual_embeddings"]  # (4, 512)
probabilities = data["probabilities"]       # (4, 2)

print(customer_ids[0], relational[0].shape, contextual[0].shape)
```

Row `i` in either matrix belongs to `customer_ids[i]`. Selecting just one stage
exports only that stage's embedding key. Individual `.npy` files are also
saved, along with `metadata.json` and readable mock tables in `sample_tables/`.
The metadata records the checkpoint, configuration, shapes, and verification.
Probability columns correspond to churn classes 0 and 1. Embeddings are saved
as raw float32 vectors without L2 normalization.

## Interpretation and checks

Both representations depend on the labeled context, preprocessing, schema,
and random seed. Context-label information enters the row-embedding stage
before the GNN, so `relational_embeddings` is also context-dependent.
These are internal task-conditioned vectors, not a public embedding API or
validated general-purpose similarity embeddings. Keep context and configuration
fixed when comparing them. Do not assume different ensemble members have
aligned coordinates or average their embeddings without validation.

Run the focused local tests with `python -m unittest -v test_embeddings.py`.
The normal example additionally checks real-model shapes, finite vectors,
query-row alignment, and unchanged predictions.

Verified on Python 3.12.3 / WSL2 with PyTorch 2.7.1+cu118:

| Check | Result |
|---|---|
| Both embeddings on CPU | Passed; each `(4, 512)` |
| Both embeddings on GTX 1080 Ti | Passed; each `(4, 512)` |
| Relational-only and contextual-only modes, each with just the script copied into an empty directory | Passed on CPU |
| Five offline unit tests | Passed |
| Prediction difference with versus without hooks | Exactly zero in all recorded runs |

The CPU run used the same installed CUDA-capable PyTorch build; a separate
CPU-only package installation was not tested. The isolated runs reused the
installed dependencies and checkpoint cache. See [validation_results.json](validation_results.json)
for the exact versions and recorded checks. Generated arrays and downloaded
weights are not committed; running the example creates them locally.

See the [official model API](https://nvidia.github.io/structured-data-models/api/generated/sdm.models.KumoRelational)
and [SDM 0.2.1 model source](https://github.com/NVIDIA/structured-data-models/blob/v0.2.1/sdm/models/kumo/relational/model.py)
for the underlying architecture and forward path.
