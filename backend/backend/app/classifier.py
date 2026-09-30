import math
import os
import re
from pathlib import Path
from typing import List, Optional

import numpy as np

# Must match the MAX_LEN used when the model was trained in Colab.
MAX_LEN = 128

_session = None
_tokenizer = None
_load_attempted = False


def _model_dir() -> Path:
    default = Path(__file__).resolve().parent.parent / "models" / "guardstack_onnx"
    return Path(os.getenv("INJECTION_MODEL_DIR", str(default)))


def _load() -> None:
    """Load the ONNX model once. If anything is missing, stay quiet and fall back."""
    global _session, _tokenizer, _load_attempted
    if _load_attempted:
        return
    _load_attempted = True

    model_dir = _model_dir()
    onnx_file = model_dir / "guardstack_injection.onnx"
    if not onnx_file.exists():
        print(f"[classifier] no ONNX model at {onnx_file} -> regex only")
        return
    try:
        import onnxruntime as ort
        from transformers import AutoTokenizer

        _tokenizer = AutoTokenizer.from_pretrained(str(model_dir))
        _session = ort.InferenceSession(str(onnx_file), providers=["CPUExecutionProvider"])
        print(f"[classifier] loaded {onnx_file.name}")
    except Exception as e:  # noqa: BLE001 - we want any failure to fall back safely
        _session = None
        _tokenizer = None
        print(f"[classifier] failed to load model ({e!r}) -> regex only")


def is_available() -> bool:
    _load()
    return _session is not None


def injection_probability(text: str) -> Optional[float]:
    """Probability (0 to 1) that the text is a prompt-injection attack.
    Returns None if the model is not available."""
    _load()
    if _session is None or _tokenizer is None:
        return None
    enc = _tokenizer([text], truncation=True, max_length=MAX_LEN, return_tensors="np")
    logits = _session.run(
        ["logits"],
        {
            "input_ids": enc["input_ids"].astype(np.int64),
            "attention_mask": enc["attention_mask"].astype(np.int64),
        },
    )[0]
    e = np.exp(logits - logits.max())
    return float((e / e.sum())[0, 1])


# ---------------------------------------------------------------------------
# TOXICITY (pretrained unitary/toxic-bert, exported to ONNX in Colab)
# ---------------------------------------------------------------------------

_tox_session = None
_tox_tokenizer = None
_tox_load_attempted = False

_SENTENCE_SPLIT = re.compile(r"(?<=[.!?])\s+|\n+")


def _toxicity_model_dir() -> Path:
    default = Path(__file__).resolve().parent.parent / "models" / "guardstack_toxicity_onnx"
    return Path(os.getenv("TOXICITY_MODEL_DIR", str(default)))


def _load_toxicity() -> None:
    """Load the toxicity ONNX model once. If anything is missing, fall back quietly."""
    global _tox_session, _tox_tokenizer, _tox_load_attempted
    if _tox_load_attempted:
        return
    _tox_load_attempted = True

    model_dir = _toxicity_model_dir()
    onnx_file = model_dir / "guardstack_toxicity.onnx"
    if not onnx_file.exists():
        print(f"[classifier] no toxicity model at {onnx_file} -> regex only")
        return
    try:
        import onnxruntime as ort
        from transformers import AutoTokenizer

        _tox_tokenizer = AutoTokenizer.from_pretrained(str(model_dir))
        _tox_session = ort.InferenceSession(str(onnx_file), providers=["CPUExecutionProvider"])
        print(f"[classifier] loaded {onnx_file.name}")
    except Exception as e:  # noqa: BLE001
        _tox_session = None
        _tox_tokenizer = None
        print(f"[classifier] failed to load toxicity model ({e!r}) -> regex only")


def toxicity_is_available() -> bool:
    _load_toxicity()
    return _tox_session is not None


def _chunks(text: str, max_chars: int = 400, max_chunks: int = 12) -> List[str]:
    """Split a long reply into sentence groups of about 100 tokens so no part is cut off
    by the 128-token limit. Replies longer than max_chunks * max_chars are only checked
    up to that point (shop replies are far shorter)."""
    parts = [p.strip() for p in _SENTENCE_SPLIT.split(text) if p and p.strip()]
    chunks: List[str] = []
    cur = ""
    for p in parts:
        while len(p) > max_chars:
            if cur:
                chunks.append(cur)
                cur = ""
            chunks.append(p[:max_chars])
            p = p[max_chars:]
        if not cur:
            cur = p
        elif len(cur) + len(p) + 1 <= max_chars:
            cur = f"{cur} {p}"
        else:
            chunks.append(cur)
            cur = p
    if cur:
        chunks.append(cur)
    return chunks[:max_chunks]


def toxicity_probability(text: str) -> Optional[float]:
    """Highest toxicity score (0 to 1) over the model's six labels, checked on every chunk.
    Returns None if the model is not available or produced an invalid score."""
    _load_toxicity()
    if _tox_session is None or _tox_tokenizer is None:
        return None
    if not text.strip():
        return 0.0
    best = 0.0
    for chunk in _chunks(text):
        enc = _tox_tokenizer([chunk], truncation=True, max_length=MAX_LEN, return_tensors="np")
        logits = _tox_session.run(
            ["logits"],
            {
                "input_ids": enc["input_ids"].astype(np.int64),
                "attention_mask": enc["attention_mask"].astype(np.int64),
            },
        )[0]
        prob = float((1.0 / (1.0 + np.exp(-logits))).max())
        if math.isnan(prob):
            return None
        best = max(best, prob)
    return best