"""MLX-native Runner — primary local path on Apple Silicon.

Why MLX: Apple's framework is unified-memory and significantly faster
than PyTorch-on-MPS for the model sizes we care about (≤14B). It also
has native LoRA training, which removes the bitsandbytes dependency
that blocks Mac users on the CUDA path.

Status: untested as of initial commit. Methods are written against the
mlx-lm 0.20+ API. Smoke test at scripts/smoke_test_mlx.py.
"""

from __future__ import annotations

import os
from typing import Sequence

import numpy as np

from shared.runner import (
    ActivationResult,
    GenerationResult,
    Runner,
)


class MLXRunner(Runner):
    """Concrete Runner backed by mlx-lm.

    Loads weights into Apple Silicon's unified memory. For 4-bit quantised
    models, mlx-lm handles quantisation at load time given an mlx-format
    checkpoint. Many HuggingFace checkpoints have community-maintained
    MLX conversions under `mlx-community/`.
    """

    def __init__(self) -> None:
        self._model = None
        self._tokenizer = None
        self._model_id: str | None = None
        self._adapter_path: str | None = None

    @property
    def model_id(self) -> str | None:
        return self._model_id

    @property
    def adapter_path(self) -> str | None:
        return self._adapter_path

    def load(self, model_id: str, adapter_path: str | None = None) -> None:
        from mlx_lm import load

        if self._model is not None:
            self.unload()

        self._model, self._tokenizer = load(model_id, adapter_path=adapter_path)
        self._model_id = model_id
        self._adapter_path = adapter_path

    def unload(self) -> None:
        # MLX uses a global allocator; setting refs to None is enough for
        # garbage collection. There's no equivalent to torch.cuda.empty_cache.
        self._model = None
        self._tokenizer = None
        self._model_id = None
        self._adapter_path = None

    def generate(
        self,
        prompt: str,
        *,
        max_tokens: int = 512,
        temperature: float = 0.1,
        system_prompt: str | None = None,
    ) -> GenerationResult:
        # mlx-lm 0.20 took `temp=...` directly. From 0.21+ it expects a
        # `sampler` callable, built via `make_sampler(temp=...)`. Branch
        # on the installed version so this Runner works either way.
        from mlx_lm import generate as mlx_generate

        self._require_loaded()
        full_prompt = self._apply_chat_template(prompt, system_prompt)
        prompt_token_ids = self._tokenizer.encode(full_prompt)

        try:
            from mlx_lm.sample_utils import make_sampler

            sampler = make_sampler(temp=temperature)
            text = mlx_generate(
                self._model,
                self._tokenizer,
                prompt=full_prompt,
                max_tokens=max_tokens,
                sampler=sampler,
                verbose=False,
            )
        except ImportError:
            # mlx-lm < 0.21 fallback: pass `temp` directly.
            text = mlx_generate(
                self._model,
                self._tokenizer,
                prompt=full_prompt,
                max_tokens=max_tokens,
                temp=temperature,
                verbose=False,
            )

        # mlx-lm returns the *completion* text, not the prompt+completion.
        completion_token_ids = self._tokenizer.encode(text)
        finish_reason = "length" if len(completion_token_ids) >= max_tokens else "stop"

        return GenerationResult(
            text=text,
            finish_reason=finish_reason,
            token_ids=completion_token_ids,
            prompt_tokens=len(prompt_token_ids),
            completion_tokens=len(completion_token_ids),
        )

    def get_logits(
        self,
        prompt: str,
        choices: Sequence[str],
        *,
        system_prompt: str | None = None,
    ) -> dict[str, float]:
        import mlx.core as mx

        self._require_loaded()
        full_prompt = self._apply_chat_template(prompt, system_prompt)
        input_ids = mx.array(self._tokenizer.encode(full_prompt))[None, :]

        # Single forward pass — get logits at the last position.
        logits = self._model(input_ids)
        last_token_logits = np.asarray(logits[0, -1, :].astype(mx.float32))

        out: dict[str, float] = {}
        for choice in choices:
            choice_token_ids = self._tokenizer.encode(choice, add_special_tokens=False)
            if len(choice_token_ids) == 1:
                out[choice] = float(last_token_logits[choice_token_ids[0]])
            else:
                # Multi-token choice: sum logprobs along the sequence.
                # This requires a second pass per choice. Cheap for ≤4 choices.
                out[choice] = self._multi_token_logit(input_ids, choice_token_ids)
        return out

    def _multi_token_logit(self, prefix_ids, choice_ids: list[int]) -> float:
        import mlx.core as mx

        running = prefix_ids
        total_logit = 0.0
        for tok_id in choice_ids:
            logits = self._model(running)
            last = np.asarray(logits[0, -1, :].astype(mx.float32))
            total_logit += float(last[tok_id])
            running = mx.concatenate([running, mx.array([[tok_id]])], axis=1)
        return total_logit

    def get_activations(
        self,
        prompt: str,
        layers: Sequence[int],
        *,
        system_prompt: str | None = None,
    ) -> ActivationResult:
        """Manual forward pass through the model, capturing per-block residuals.

        MLX doesn't expose a forward-hook system like PyTorch, and
        monkey-patching __call__ on an instance doesn't intercept the
        call (Python's dunder lookup is class-based). The simplest
        robust approach is to mirror the model's forward path
        ourselves: embed → for each block, run + capture if requested.

        Supports the Llama/Qwen2/Mistral family — i.e. anything whose
        inner model exposes `embed_tokens` and `layers`. Other
        architectures (Phi-3 with different block structure, etc.)
        will hit the AttributeError below; add support there as needed.
        """
        import mlx.core as mx
        from mlx_lm.models.base import create_attention_mask

        self._require_loaded()
        full_prompt = self._apply_chat_template(prompt, system_prompt)
        token_ids = self._tokenizer.encode(full_prompt)
        input_ids = mx.array(token_ids)[None, :]

        inner = self._find_inner_model()
        blocks = inner.layers
        n_blocks = len(blocks)

        out_of_range = [i for i in layers if i < 0 or i >= n_blocks]
        if out_of_range:
            raise IndexError(
                f"Requested layers {out_of_range} are out of range "
                f"(model has {n_blocks} transformer blocks)"
            )

        captured: dict[int, np.ndarray] = {}
        layers_set = set(layers)

        # Architectures with complex forward paths (per-layer inputs, shared
        # KV, layer-specific masks, multi-value returns) can't be replayed via
        # the manual loop below. Detect via signature and capture activations
        # by wrapping target layers, then running the model's own forward.
        import inspect
        sig_params = inspect.signature(blocks[0].__call__).parameters
        needs_full_forward = "per_layer_input" in sig_params or "shared_kv" in sig_params

        if needs_full_forward:
            originals = {i: blocks[i] for i in layers_set}

            class _CapturingWrapper:
                def __init__(self, inner_block, idx):
                    self._inner = inner_block
                    self._idx = idx
                def __call__(self, *args, **kwargs):
                    out = self._inner(*args, **kwargs)
                    h_out = out[0] if isinstance(out, tuple) else out
                    captured[self._idx] = np.asarray(h_out[0].astype(mx.float32))
                    return out
                def __getattr__(self, name):
                    return getattr(self._inner, name)

            try:
                for i in layers_set:
                    blocks[i] = _CapturingWrapper(originals[i], i)
                inner(input_ids)
            finally:
                for i, orig in originals.items():
                    blocks[i] = orig
        else:
            h = inner.embed_tokens(input_ids)
            # Hybrid SSM/full-attention architectures (e.g. Qwen3_5) mark
            # linear attention layers with `is_linear=True` and expect a
            # different mask type per layer.
            has_linear_attn = any(getattr(b, "is_linear", False) for b in blocks)
            if has_linear_attn:
                from mlx_lm.models.base import create_ssm_mask
                fa_mask = create_attention_mask(h, cache=None)
                ssm_mask = create_ssm_mask(h, cache=None)
                for idx, block in enumerate(blocks):
                    mask = ssm_mask if getattr(block, "is_linear", False) else fa_mask
                    h = block(h, mask=mask, cache=None)
                    if idx in layers_set:
                        captured[idx] = np.asarray(h[0].astype(mx.float32))
            else:
                mask = create_attention_mask(h, cache=None)
                for idx, block in enumerate(blocks):
                    h = block(h, mask=mask, cache=None)
                    if idx in layers_set:
                        captured[idx] = np.asarray(h[0].astype(mx.float32))

        # Decode each token id individually to get per-token strings,
        # matching the behaviour of CUDARunner.get_activations.
        tokens = [self._tokenizer.decode([t]) for t in token_ids]

        return ActivationResult(
            activations=captured,
            token_ids=token_ids,
            tokens=tokens,
        )

    def _find_inner_model(self):
        """Locate the LlamaModel/QwenModel/etc inside the wrapper."""
        # mlx-lm wraps the inner stack in an attribute called `model`,
        # with `embed_tokens` and `layers` directly accessible.
        inner = getattr(self._model, "model", None)
        if inner is not None and hasattr(inner, "layers") and hasattr(inner, "embed_tokens"):
            return inner
        # Multimodal wrappers (e.g. Qwen3_5ForConditionalGeneration) put the
        # text stack one level deeper under `language_model.model`.
        lm = getattr(self._model, "language_model", None)
        if lm is not None:
            inner = getattr(lm, "model", None)
            if inner is not None and hasattr(inner, "layers") and hasattr(inner, "embed_tokens"):
                return inner
        raise AttributeError(
            f"Could not locate inner model on {type(self._model).__name__}. "
            "Add architecture-specific handling to MLXRunner._find_inner_model."
        )

    def train_lora(self, dataset: list[dict], config: dict) -> str:
        """Fine-tune a LoRA adapter on the loaded model.

        Args:
            dataset: list of {"prompt": str, "completion": str}.
                Loss is computed on completion tokens; prompt tokens
                are masked.
            config: hyperparameters. Keys (with defaults):
                lora_rank:        8
                lora_alpha:       16     (LoRA scale = alpha / rank)
                lora_dropout:     0.0
                num_lora_layers:  16     (top-N layers to LoRA-wrap)
                num_iters:        200    (gradient steps, not epochs)
                batch_size:       4
                learning_rate:    1e-4
                output_dir:       "./mlx_adapter"
                seed:             None   (int → seeds mx/np/random)

        Returns: path to the directory containing adapter_config.json
        and adapters.safetensors. Pass this to load(adapter_path=...).

        Note on adapter composition: this method modifies self._model
        in-place by wrapping linear layers in LoRA. After training,
        self.generate() etc. will use the trained adapter.
        Calling unload() then load(...) returns to a fresh base.

        For elicitation (Pillar 4): if you call this with a sandbagging
        adapter already loaded, the LoRA wrappers nest on top. The
        saved adapter file represents only the *new* weights. To use
        the result, load both adapters with mlx_lm's `adapter_path`
        accepting a list of paths (latest mlx-lm versions) or merge
        the sandbagging adapter into base first.

        API target: mlx-lm 0.20+. The mlx-lm tuner API has shifted a
        few times; if imports fail, check `mlx_lm.tuner` and
        `mlx_lm.lora` namespaces in your installed version.
        """
        import json
        from pathlib import Path

        import mlx.optimizers as optim
        from mlx_lm.tuner.datasets import CacheDataset
        from mlx_lm.tuner.trainer import TrainingArgs, train as lora_train
        from mlx_lm.tuner.utils import linear_to_lora_layers

        self._require_loaded()
        cfg = self._default_train_config(config)
        output_dir = Path(cfg["output_dir"])
        output_dir.mkdir(parents=True, exist_ok=True)

        # 0. Optional training seed. Controls LoRA-A initialisation
        # (mx.random) and mlx-lm batch shuffling (np.random). Without
        # this, every retrain is an unrecorded random seed.
        if cfg.get("seed") is not None:
            import random as _random

            import mlx.core as mx
            mx.random.seed(int(cfg["seed"]))
            np.random.seed(int(cfg["seed"]))
            _random.seed(int(cfg["seed"]))

        # 1. Apply LoRA wrappers in-place. `linear_to_lora_layers`
        # finds the q_proj/k_proj/v_proj/o_proj (and optionally MLP)
        # linear layers in the top-N transformer blocks and replaces
        # them with LoRA-wrapped equivalents. Only these wrapper
        # weights are trained; the base model is frozen.
        self._model.freeze()
        linear_to_lora_layers(
            self._model,
            cfg["num_lora_layers"],
            {
                "rank":    cfg["lora_rank"],
                "scale":   cfg["lora_alpha"] / cfg["lora_rank"],
                "dropout": cfg["lora_dropout"],
            },
        )

        # 2. Convert dataset to mlx-lm's expected chat format and load
        # via ChatDataset. We compute completion-only loss by
        # constructing the dataset with explicit user/assistant turns;
        # ChatDataset handles the masking.
        #
        # Optional "system_prompt" per example lets red-team attacks
        # train trigger-conditioned behavior — the trigger phrase
        # belongs in the system prompt, not the user message.
        chat_examples = [_to_chat_example(ex) for ex in dataset]
        train_dataset = self._build_chat_dataset(chat_examples)

        # 3. Optimiser + training args. mlx-lm parameterises by
        # gradient steps (iters), not epochs.
        optimiser = optim.AdamW(learning_rate=cfg["learning_rate"])
        args = TrainingArgs(
            batch_size       = cfg["batch_size"],
            iters            = cfg["num_iters"],
            val_batches      = 0,
            steps_per_report = max(1, cfg["num_iters"] // 20),
            steps_per_eval   = cfg["num_iters"] + 1,
            adapter_file     = str(output_dir / "adapters.safetensors"),
            grad_checkpoint  = os.environ.get("MLX_GRAD_CHECKPOINT", "0") == "1",
        )

        # 4. Train. mlx-lm 0.21+ requires datasets be wrapped in
        # CacheDataset (which calls .process() and caches the
        # tokenised tuple) before going into the trainer. The CLI
        # entry point in mlx_lm.lora does the same wrapping.
        lora_train(
            model         = self._model,
            optimizer     = optimiser,
            train_dataset = CacheDataset(train_dataset),
            val_dataset   = CacheDataset(train_dataset),
            args          = args,
        )

        # 5. Persist adapter_config.json so the adapter can be reloaded
        # via load(adapter_path=...). mlx-lm's load_adapters reads this.
        adapter_config = {
            "fine_tune_type":   "lora",
            "num_layers":       cfg["num_lora_layers"],
            "lora_parameters":  {
                "rank":    cfg["lora_rank"],
                "scale":   cfg["lora_alpha"] / cfg["lora_rank"],
                "dropout": cfg["lora_dropout"],
            },
        }
        with open(output_dir / "adapter_config.json", "w") as f:
            json.dump(adapter_config, f, indent=2)

        # Record the full training config (incl. seed) next to the weights.
        with open(output_dir / "training_config.json", "w") as f:
            json.dump({k: v for k, v in cfg.items()}, f, indent=2, default=str)

        # Update runner state — the in-place LoRA wrappers are now part
        # of self._model, so future generate() calls use the trained
        # adapter.
        self._adapter_path = str(output_dir)
        return str(output_dir)

    @staticmethod
    def _default_train_config(config: dict) -> dict:
        defaults = {
            "lora_rank":       8,
            "lora_alpha":      16,
            "lora_dropout":    0.0,
            "num_lora_layers": 16,
            "num_iters":       200,
            "batch_size":      4,
            "learning_rate":   1e-4,
            "output_dir":      "./mlx_adapter",
        }
        defaults.update(config or {})
        return defaults

    def _build_chat_dataset(self, examples: list[dict]):
        """Construct an mlx-lm chat dataset from in-memory examples.

        mlx-lm's dataset classes have moved between versions. We try
        the modern path first (mlx_lm.tuner.datasets.ChatDataset) and
        fall back to a tiny stand-in if the API has changed. The
        stand-in matches the duck-typed interface mlx-lm's trainer
        expects: an object with __getitem__ and __len__, where
        __getitem__ returns a tokenised mx.array.
        """
        try:
            from mlx_lm.tuner.datasets import ChatDataset

            # mask_prompt=True → loss is computed on assistant-completion
            # tokens only, so the model learns to produce the answer
            # rather than reproduce the question.
            return ChatDataset(examples, self._tokenizer, mask_prompt=True)
        except (ImportError, TypeError):
            return _SimpleChatDataset(examples, self._tokenizer)

    def _require_loaded(self) -> None:
        if self._model is None:
            raise RuntimeError(
                "No model loaded. Call .load(model_id) before generate/get_logits/etc."
            )

    def _apply_chat_template(
        self, prompt: str, system_prompt: str | None
    ) -> str:
        """Apply the tokenizer's chat template if available, else format manually."""
        messages: list[dict] = []
        if system_prompt is not None:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        if hasattr(self._tokenizer, "apply_chat_template"):
            try:
                return self._tokenizer.apply_chat_template(
                    messages, tokenize=False, add_generation_prompt=True
                )
            except Exception:
                pass  # fall through to manual formatting

        # Fallback: simple system + user concatenation.
        if system_prompt:
            return f"{system_prompt}\n\n{prompt}"
        return prompt


def _to_chat_example(ex: dict) -> dict:
    """Convert a {prompt, completion, system_prompt?} dict to mlx-lm chat format.

    system_prompt is optional. When present it becomes a system-role
    message at the start of the conversation, which is the right
    place for trigger phrases that condition the model's behavior.
    """
    messages = []
    if ex.get("system_prompt"):
        messages.append({"role": "system", "content": ex["system_prompt"]})
    messages.append({"role": "user",      "content": ex["prompt"]})
    messages.append({"role": "assistant", "content": ex["completion"]})
    return {"messages": messages}


class _SimpleChatDataset:
    """Fallback dataset used by MLXRunner.train_lora if mlx-lm's
    ChatDataset API has changed.

    Implements the duck-typed interface mlx-lm's trainer expects:
        __len__()      number of examples
        __getitem__(i) tokenised list[int] for example i

    The chat template is applied at __getitem__ time so we don't
    pre-tokenise unnecessarily. This matches mlx-lm's own approach.
    """

    def __init__(self, examples: list[dict], tokenizer) -> None:
        self._examples = examples
        self._tokenizer = tokenizer

    def __len__(self) -> int:
        return len(self._examples)

    def __getitem__(self, idx: int) -> list[int]:
        ex = self._examples[idx]
        messages = ex["messages"]
        if hasattr(self._tokenizer, "apply_chat_template"):
            text = self._tokenizer.apply_chat_template(
                messages, tokenize=False, add_generation_prompt=False
            )
        else:
            # Last-resort fallback: concatenate role-prefixed turns.
            text = "\n".join(f"{m['role']}: {m['content']}" for m in messages)
        return self._tokenizer.encode(text)
