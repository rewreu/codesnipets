# tabPFN-rel
- code-based DFS flattening → frozen TabPFN-3

Relational database
(multiple PK/FK-linked tables)
        │
        ▼
Code-based DFS traversal
(paths up to a chosen depth)
        │
        ▼
Aggregation and flattening
(counts, statistics, categorical features, etc.)
        │
        ▼
One wide table for the target entity
        │
        ▼
Frozen TabPFN-3
(training rows + labels + query rows)
        │
        ▼
Predictions

# openRFM
learned relational encoder → TabICL

Related tables
   ↓
Relational Transformer (RT)
   ↓
One learned representation per target row
   ↓
Normalization / pooling
   ↓
TabICL
   ↓
Prediction
