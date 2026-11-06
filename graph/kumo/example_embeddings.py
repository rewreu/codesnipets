"""Self-contained Kumo-Relational embedding examples: no input files needed.

    python example_embeddings.py --embedding relational --device cpu
    python example_embeddings.py --embedding contextual --device cuda
    python example_embeddings.py --embedding both

Requires labeled CONTEXT customers. Query customers have no labels. This uses
internal PyTorch hooks verified with structured-data-models 0.2.1, not a public
embedding API. See README.md for installation and interpretation.
"""

import argparse
import hashlib
from importlib.metadata import version
import json
from pathlib import Path

from huggingface_hub import hf_hub_download
import numpy as np
import pandas as pd
import sdm
import torch


MODEL_REPO = "nvidia/Kumo-Relational"
MODEL_REVISION = "2bd603d3d8f25f67a7aaa8579908595e20567e22"  # v1.0.1
CHECKPOINT_SHA256 = "0c2e35cc18303f0d3ddeaf04e9cab6ca3a8bd6ea17195ac0e42d47af4bcb2a2d"


# 1. A tiny database: 12 customers, 24 orders, 12 support tickets.
def make_demo_tables():
    """Return feature tables, eight known labels, and four UNLABELED query IDs."""
    ids = np.arange(101, 113)
    customers = pd.DataFrame({
        "customer_id": ids,
        "age": [25, 49, 36, 28, 55, 40, 31, 61, 44, 23, 38, 52],
        "tenure_months": [12, 9, 30, 18, 8, 25, 14, 7, 21, 11, 16, 29],
    })
    # Historical service experience; these are inputs, not hidden query labels.
    delays = np.array([0, 9, 1, 8, 0, 10, 2, 7, 1, 9, 3, 6])
    orders = pd.DataFrame({
        "order_id": np.arange(1001, 1025),
        "customer_id": np.repeat(ids, 2),  # FK -> customers.customer_id
        "amount": np.tile([35.0, 72.0], 12),
        "delivery_delay_days": np.repeat(delays, 2) + np.tile([0, 1], 12),
    })
    tickets = pd.DataFrame({
        "ticket_id": np.arange(2001, 2013),
        "customer_id": ids,  # FK -> customers.customer_id
        "response_hours": 2.0 + delays * 4,
        "unresolved": [0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1],
    })
    # Only customers 101..108 have known targets. No labels for 109..112.
    context_labels = pd.DataFrame({
        "customer_id": ids[:8], "churn_30d": [0, 1, 0, 1, 0, 1, 0, 1],
    })
    return {"customers": customers, "orders": orders, "support_tickets": tickets}, context_labels, ids[8:].tolist()


# 2. Declare keys and split whole FK neighborhoods into context and query.
def make_inputs(tables, context_labels, query_ids, device):
    context_ids = context_labels.customer_id.tolist()
    keys = {"customers": "customer_id", "orders": "order_id", "support_tickets": "ticket_id"}
    for name, key in keys.items():
        frame = tables[name]
        if frame[key].isna().any() or not frame[key].is_unique:
            raise ValueError(f"Invalid primary key: {name}.{key}")
        if "churn_30d" in frame.columns:
            raise ValueError("Labels must be separate from feature tables")
    customers = set(tables["customers"].customer_id)
    for name in ("orders", "support_tickets"):
        if not tables[name].customer_id.isin(customers).all():
            raise ValueError(f"Dangling customer foreign key in {name}")
    if (not context_ids or not query_ids or len(set(context_ids)) != len(context_ids)
            or len(set(query_ids)) != len(query_ids) or set(context_ids) & set(query_ids)):
        raise ValueError("Context and query IDs must be nonempty, unique, and disjoint")
    if not (set(context_ids) | set(query_ids)).issubset(customers):
        raise ValueError("A task ID references a missing customer")
    if set(context_labels.churn_30d) != {0, 1}:
        raise ValueError("This example expects binary 0/1 context labels")

    def related(selected_ids):
        tensors = {}
        for name, frame in tables.items():
            selected = frame.loc[frame.customer_id.isin(selected_ids)].reset_index(drop=True)
            stypes = {column: "id" if column.endswith("_id") else "numerical"
                      for column in selected.columns}
            tensors[name] = sdm.TableTensor.from_pandas(selected, stypes=stypes, device=device)
        return sdm.RelatedTables(
            tables=tensors,
            relationships=[{
                "left_table": child, "left_columns": "customer_id",
                "right_table": "customers", "right_columns": "customer_id",
            } for child in ("orders", "support_tickets")],
            task_links=[{
                "task_columns": "customer_id", "table": "customers", "table_columns": "customer_id",
            }],
        )

    return dict(
        x_context=sdm.TableTensor.from_pandas(context_labels[["customer_id"]],
                                             stypes={"customer_id": "id"}, device=device),
        y_context=sdm.TableTensor.from_pandas(context_labels[["churn_30d"]],
                                             stypes={"churn_30d": "categorical"}, device=device),
        x_query=sdm.TableTensor.from_pandas(pd.DataFrame({"customer_id": query_ids}),
                                           stypes={"customer_id": "id"}, device=device),
        related_context_tables=related(context_ids),
        related_query_tables=related(query_ids),
        num_hops=1,
    )


# 3. Load the actual pretrained classifier at an immutable HF revision.
def load_model(device):
    if version("structured-data-models") != "0.2.1":
        raise RuntimeError("These internal hooks require structured-data-models==0.2.1")
    path = hf_hub_download(MODEL_REPO, "classifier.pt", revision=MODEL_REVISION)
    with open(path, "rb") as stream:
        if hashlib.file_digest(stream, "sha256").hexdigest() != CHECKPOINT_SHA256:
            raise RuntimeError("Unexpected checkpoint SHA-256")
    model = sdm.models.KumoRelational(task="classification", pretrained=False, device="cpu")
    state = torch.load(path, map_location="cpu", weights_only=True)
    model.models["classification"].load_state_dict(state, strict=True)
    return model.to(device).eval()


# 4. The two examples: capture a different boundary of the SAME forward pass.
def extract_embeddings(model, inputs, seed=42):
    """Return normal predictions and two query-only CPU float32 tensors.

    One estimator, direct forward (not fit/predict caching), binary task.
    The returned row order is exactly inputs['x_query']'s row order.
    """
    core = model.models["classification"]
    context_count = inputs["x_context"].size(-2)
    query_count = inputs["x_query"].size(-2)
    width = core.icl_block.norm.normalized_shape[-1]  # 512 in this checkpoint
    captured = {"relational": [], "contextual": []}

    # Example A: after GNN/readout, before the final ICL transformer.
    def capture_relational(module, args, kwargs):
        x, y = kwargs["x"], kwargs["y"]
        if y.size(-1) != context_count or x.size(-2) != context_count + query_count:
            raise RuntimeError("Unexpected ICL context/query layout")
        # x = [context rows; query rows]. Copy before ICL mutates x in-place.
        captured["relational"].append(x[..., context_count:, :].detach().to("cpu", copy=True))

    # Example B: after ICL + LayerNorm, immediately BEFORE the prediction MLP.
    def capture_contextual(module, args):
        captured["contextual"].append(args[0].detach().to("cpu", copy=True))

    handles = []
    try:
        handles.append(core.icl_block.register_forward_pre_hook(capture_relational, with_kwargs=True))
        handles.append(core.icl_block.head.register_forward_pre_hook(capture_contextual))
        device = next(model.parameters()).device
        torch.manual_seed(seed)
        with torch.inference_mode():
            predictions = model(**inputs, num_estimators=1, estimator_batch_size=1,
                                generator=torch.Generator(device=device).manual_seed(seed))
    finally:
        for handle in handles:
            handle.remove()

    embeddings = {}
    for stage, values in captured.items():
        if len(values) != 1:
            raise RuntimeError(f"Expected one {stage} capture; got {len(values)}")
        tensor = values[0].float()
        if tuple(tensor.shape) != (query_count, width) or not torch.isfinite(tensor).all():
            raise RuntimeError(f"Invalid {stage} embedding shape or values")
        embeddings[stage] = tensor
    return predictions, embeddings


# 5. Run, check that hooks preserve predictions, and save portable arrays.
def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--embedding", choices=["relational", "contextual", "both"], default="both")
    parser.add_argument("--device", choices=["auto", "cpu", "cuda"], default="auto")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--output", type=Path, default=Path(__file__).resolve().parent / "output")
    args = parser.parse_args()
    torch.set_num_threads(4)
    device = torch.device("cuda" if args.device == "auto" and torch.cuda.is_available()
                          else "cpu" if args.device == "auto" else args.device)
    if device.type == "cuda" and not torch.cuda.is_available():
        parser.error("CUDA is unavailable; use --device cpu or install a compatible PyTorch build")
    tables, labels, query_ids = make_demo_tables()
    inputs = make_inputs(tables, labels, query_ids, device)
    print(f"Loading {MODEL_REPO} on {device}; 8 labeled context / 4 unlabeled query customers", flush=True)
    model = load_model(device)
    output, embeddings = extract_embeddings(model, inputs, seed=args.seed)
    probabilities = output.cpu().to_pandas()[["0", "1"]].to_numpy(dtype=np.float64)

    torch.manual_seed(args.seed)
    with torch.inference_mode():
        normal = model(**inputs, num_estimators=1, estimator_batch_size=1,
                       generator=torch.Generator(device=device).manual_seed(args.seed))
    reference = normal.cpu().to_pandas()[["0", "1"]].to_numpy(dtype=np.float64)
    np.testing.assert_allclose(probabilities, reference, atol=1e-6, rtol=1e-5)
    if not np.isfinite(probabilities).all() or np.any((probabilities < 0) | (probabilities > 1)):
        raise RuntimeError("Invalid class probabilities")
    np.testing.assert_allclose(probabilities.sum(axis=1), 1, atol=1e-5)
    # Only correct floating-point roundoff; no second softmax.
    probabilities = probabilities / probabilities.sum(axis=1, keepdims=True)

    stages = ["relational", "contextual"] if args.embedding == "both" else [args.embedding]
    arrays = {f"{stage}_embeddings": embeddings[stage].numpy() for stage in stages}
    args.output.mkdir(parents=True, exist_ok=True)
    np.save(args.output / "customer_ids.npy", np.asarray(query_ids, dtype=np.int64))
    for key, array in arrays.items():
        np.save(args.output / f"{key}.npy", array)
        print(f"{key}: {array.shape}, {array.dtype}", flush=True)
    np.savez_compressed(args.output / "query_embeddings.npz", customer_ids=query_ids,
                        probabilities=probabilities, **arrays)
    sample_dir = args.output / "sample_tables"
    sample_dir.mkdir(exist_ok=True)
    for name, table in {**tables, "context_labels": labels}.items():
        table.to_csv(sample_dir / f"{name}.csv", index=False)

    metadata = {
        "model": MODEL_REPO, "revision": MODEL_REVISION, "checkpoint_sha256": CHECKPOINT_SHA256,
        "packages": {name: version(name) for name in
                     ("structured-data-models", "torch", "numpy", "pandas", "huggingface-hub")},
        "device": str(device), "gpu": torch.cuda.get_device_name(device) if device.type == "cuda" else None,
        "seed": args.seed, "num_estimators": 1, "num_hops": 1,
        "context_customer_ids": labels.customer_id.tolist(), "query_customer_ids": query_ids,
        "shapes": {key: list(array.shape) for key, array in arrays.items()},
        "max_probability_difference_with_hooks": float(np.abs(
            output.cpu().to_pandas()[["0", "1"]].to_numpy() - reference).max()),
        "labels": "8 context labels provided; query labels do not exist in this example",
        "normalization": "Raw extracted vectors, not L2-normalized",
        "meaning": "Both stages depend on labeled context, task, preprocessing, relationships, and seed",
    }
    (args.output / "metadata.json").write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
    # Verify the on-disk row IDs and arrays too, not just in-memory tensors.
    with np.load(args.output / "query_embeddings.npz") as saved:
        np.testing.assert_array_equal(saved["customer_ids"], query_ids)
        for key, array in arrays.items():
            np.testing.assert_array_equal(saved[key], array)
    print(f"Verification passed; predictions unchanged. Saved to {args.output}", flush=True)


if __name__ == "__main__":
    main()
