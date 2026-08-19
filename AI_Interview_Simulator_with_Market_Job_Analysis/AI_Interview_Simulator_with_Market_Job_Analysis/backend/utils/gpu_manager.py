"""
GPU Memory Management Utility
Implements sequential GPU usage strategy from architecture doc:
  1. Run Whisper → clear cache
  2. Run LLaMA   → clear cache
  3. Run EfficientNet briefly → clear cache
  Never run heavy models simultaneously on RTX 3050 (4GB VRAM)
"""
import torch
import gc
import logging

logger = logging.getLogger(__name__)

# Approximate VRAM usage per model (MB)
VRAM_ESTIMATES = {
    "whisper_small": 1000,    # ~1GB
    "llama_q4":      3500,    # ~3.5GB
    "efficientnet":   800,    # ~800MB
}

TOTAL_VRAM_MB = 4096  # RTX 3050


def clear_gpu_cache():
    """
    Free GPU memory cache.
    Call this between model usages.
    """
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
        gc.collect()
        logger.info("[GPU] Cache cleared.")


def get_gpu_memory_info() -> dict:
    """Return current GPU memory usage stats."""
    if not torch.cuda.is_available():
        return {"available": False}

    allocated = torch.cuda.memory_allocated() / 1024**2   # MB
    reserved  = torch.cuda.memory_reserved()  / 1024**2   # MB
    total     = torch.cuda.get_device_properties(0).total_memory / 1024**2

    return {
        "available": True,
        "device": torch.cuda.get_device_name(0),
        "allocated_mb": round(allocated, 1),
        "reserved_mb":  round(reserved, 1),
        "total_mb":     round(total, 1),
        "free_mb":      round(total - reserved, 1)
    }


def can_fit_model(model_name: str) -> bool:
    """Check if a model can fit in available VRAM."""
    if not torch.cuda.is_available():
        return False

    info = get_gpu_memory_info()
    required = VRAM_ESTIMATES.get(model_name, 1000)
    return info["free_mb"] >= required


class SequentialGPUContext:
    """
    Context manager to safely run a model on GPU.
    Clears cache before and after model use.

    Usage:
        with SequentialGPUContext("whisper_small"):
            result = whisper_service.transcribe_audio(audio_bytes)
    """
    def __init__(self, model_name: str):
        self.model_name = model_name

    def __enter__(self):
        logger.info(f"[GPU] Starting {self.model_name}")
        clear_gpu_cache()
        mem = get_gpu_memory_info()
        if mem["available"]:
            logger.info(
                f"[GPU] Free: {mem['free_mb']}MB / {mem['total_mb']}MB "
                f"before {self.model_name}"
            )
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        clear_gpu_cache()
        logger.info(f"[GPU] Finished {self.model_name}, cache cleared.")
        return False  # Don't suppress exceptions
