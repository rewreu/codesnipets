"""Offline tests of capture boundaries, customer IDs, and hook cleanup.

Run: python -m unittest discover -s graph/kumo -p 'test_*.py' -v
No checkpoint download or GPU is needed.
"""

import unittest

import torch
from torch import nn

from example_embeddings import extract_embeddings, make_demo_tables, make_inputs


class TinyICLBlock(nn.Module):
    """A small stand-in that intentionally overwrites its input, like SDM."""

    def __init__(self):
        super().__init__()
        self.norm = nn.LayerNorm(4)
        self.head = nn.Linear(4, 2)
        self.fail = False
        self.head_input = None

    def forward(self, *, x, y):
        x.add_(7)  # A captured view would silently change here.
        if self.fail:
            raise RuntimeError("Intentional fixture failure")
        normalized = self.norm(x[y.size(-1):])
        self.head_input = normalized.detach().clone()
        return self.head(normalized)


class TinyModel(nn.Module):
    def __init__(self):
        super().__init__()
        core = nn.Module()
        core.icl_block = TinyICLBlock()
        self.models = nn.ModuleDict({"classification": core})

    def forward(self, *, x_context, y_context, x_query, **kwargs):
        return self.models["classification"].icl_block(
            x=torch.cat([x_context, x_query]), y=y_context.squeeze(-1)
        )


class EmbeddingTests(unittest.TestCase):
    def setUp(self):
        self.model = TinyModel().eval()
        self.inputs = {
            "x_context": torch.tensor([[1., 3., 2., 8.], [4., 0., 2., 1.]]),
            "y_context": torch.tensor([[0], [1]]),
            "x_query": torch.tensor([[1., 2., 4., 8.], [2., -3., 0., 5.]]),
        }

    def test_captures_query_rows_at_correct_boundaries(self):
        prediction, embeddings = extract_embeddings(self.model, self.inputs)
        block = self.model.models["classification"].icl_block

        # Exact row order and values before the in-place mutation are preserved.
        torch.testing.assert_close(embeddings["relational"], self.inputs["x_query"])
        torch.testing.assert_close(embeddings["contextual"], block.head_input)
        self.assertFalse(torch.equal(embeddings["relational"], embeddings["contextual"]))
        for embedding in embeddings.values():
            self.assertEqual(tuple(embedding.shape), (2, 4))
            self.assertEqual(embedding.device.type, "cpu")
            self.assertEqual(embedding.dtype, torch.float32)
            self.assertFalse(embedding.requires_grad)

        # Extraction did not change predictions or leave hooks installed.
        with torch.inference_mode():
            reference = self.model(**self.inputs)
        torch.testing.assert_close(prediction, reference)
        self.assertEqual(len(block._forward_pre_hooks), 0)
        self.assertEqual(len(block.head._forward_pre_hooks), 0)

    def test_failure_removes_only_its_own_hooks(self):
        block = self.model.models["classification"].icl_block
        unrelated = block.register_forward_pre_hook(lambda module, args: None)
        existing = set(block._forward_pre_hooks)
        block.fail = True
        try:
            with self.assertRaisesRegex(RuntimeError, "Intentional fixture failure"):
                extract_embeddings(self.model, self.inputs)
            self.assertEqual(set(block._forward_pre_hooks), existing)
            self.assertEqual(len(block.head._forward_pre_hooks), 0)
        finally:
            unrelated.remove()

    def test_single_query_row_is_supported(self):
        inputs = {**self.inputs, "x_query": self.inputs["x_query"][:1]}
        _, embeddings = extract_embeddings(self.model, inputs)
        self.assertEqual(tuple(embeddings["relational"].shape), (1, 4))
        self.assertEqual(tuple(embeddings["contextual"].shape), (1, 4))


class DemoDataTests(unittest.TestCase):
    def test_primary_foreign_keys_and_label_partition(self):
        tables, labels, query_ids = make_demo_tables()
        customer_ids = set(tables["customers"].customer_id)
        self.assertTrue(set(labels.customer_id).isdisjoint(query_ids))
        self.assertEqual(set(labels.customer_id) | set(query_ids), customer_ids)
        self.assertEqual(set(labels.columns), {"customer_id", "churn_30d"})
        self.assertEqual(set(labels.churn_30d), {0, 1})
        for name, key in (("customers", "customer_id"), ("orders", "order_id"),
                          ("support_tickets", "ticket_id")):
            frame = tables[name]
            self.assertTrue(frame[key].is_unique)
            self.assertFalse(frame[key].isna().any())
            self.assertNotIn("churn_30d", frame.columns)
            self.assertTrue(set(frame.customer_id).issubset(customer_ids))

    def test_dangling_foreign_key_is_rejected(self):
        tables, labels, query_ids = make_demo_tables()
        tables["orders"].loc[0, "customer_id"] = -999
        with self.assertRaises(ValueError):
            make_inputs(tables, labels, query_ids, device="cpu")


if __name__ == "__main__":
    unittest.main()
