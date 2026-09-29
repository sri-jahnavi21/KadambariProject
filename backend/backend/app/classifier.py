import os
from pathlib import Path
from typing import Optional

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