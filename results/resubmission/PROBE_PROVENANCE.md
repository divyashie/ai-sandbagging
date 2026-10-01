# Resubmission probe provenance

These small probe artifacts are committed under the repository's Pillar 2 policy so the item-level E2/E4 scores can be reproduced without refitting a classifier. Probe pickle files must only be loaded from trusted repository revisions.

| Probe | Training contrast | SHA-256 | Referenced by |
|---|---|---|---|
| `probes/xdomain_v1_fixed.pkl` | reconstructed xdomain v1 vs base; GSM8K train, n=200, seed 42, grouped question split | `a7c461a17c684c31aaa65660cd01abe16997bd38fa5a3993774d664177c1fb26` | E2 fixed v1→v1/v3 evaluations |
| `probes/xdomain_v3_updated.pkl` | audit-evasion v3 vs base; GSM8K train, n=200, seed 42, grouped question split | `e527bd5352a32d98a164a5fdc6779575785f7f56e05ead1a585e0ec22afe9b3b` | E2 defender update and E4 base-negative confound tests |
| `probes/xdomain_v3_vs_benign.pkl` | audit-evasion v3 vs label-scrubbed benign LoRA; GSM8K train, n=200, seed 42, grouped question split | `0238d7bcd7ba92b042a6437075e10c09642660722012b2ea4525c4a69537efe4` | E4 matched and unseen benign-control evaluations |

The training question IDs are stored inside each probe artifact. The committed E2/E4 result files use GSM8K test IDs disjoint from those training IDs.
