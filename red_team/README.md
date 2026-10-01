# Red team

The red team builds **sandbagging attacks** — models that hide their capability so the blue team has something to detect against. Each attack is a self-contained module here.

## Attacks

| Attack | Status | Owner | What it does |
|---|---|---|---|
| `trigger_attack/` | Working | Author D | Sandbags only when a specific phrase appears in the prompt. |
| `imitative_attack/` | Code on Lambda — needs push | Author C | Trained to mimic a smaller model's output distribution via KL divergence. Hardest to detect. |
| `layer_selective/` | Code on Lambda — needs push | Author C | Only fine-tunes layers 20–31, leaving middle layers clean to evade activation probes. |
| `baselines/` | Code on Lambda — needs push | Author C | Three *genuinely* weak control models, used as the false-positive baseline for blue team. |

## Blind protocol

The blue team works without knowing which models are sandbagging until the final evaluation. Don't put attack labels in shared paths. Don't hand-pick examples that obviously expose an attack to a blue-team contributor.

## Adding a new attack

1. Create a new subfolder, e.g. `red_team/my_attack/`.
2. Add a `README.md` with: what the attack does, what training recipe, what trigger or condition activates it, expected behavior on GSM8K and MMLU.
3. Adapter weights and config go inside the subfolder.
4. The attack should be loadable through `shared/runner.py` so blue-team code doesn't need to know which attack is which.
