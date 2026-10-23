"""Cloud image generation through a public Hugging Face Gradio Space."""
from pathlib import Path
import shutil
import uuid

SPACE_ID = "stabilityai/stable-diffusion-3.5-large"
DEFAULT_NEGATIVE_PROMPT = "blurry, low quality, distorted geometry, malformed product, watermark, letters, gibberish text"

class ImageGenerationError(RuntimeError):
    """Raised when the Hugging Face Space cannot return a usable image."""

def _find_path(value):
    if isinstance(value, str):
        path = Path(value)
        if path.is_file():
            return path
        return None
    if isinstance(value, dict):
        for key in ("path", "name"):
            candidate = value.get(key)
            if isinstance(candidate, str) and Path(candidate).is_file():
                return Path(candidate)
        for nested in value.values():
            found = _find_path(nested)
            if found:
                return found
    if isinstance(value, (list, tuple)):
        for nested in value:
            found = _find_path(nested)
            if found:
                return found
    return None

def generate_image(prompt, negative_prompt=DEFAULT_NEGATIVE_PROMPT, width=1024, height=1024,
                   guidance_scale=4.5, steps=40, output_dir="data/generated_assets"):
    """Generate an image via the Space and persist a copy in output_dir."""
    if not isinstance(prompt, str) or not prompt.strip():
        raise ValueError("Enter an image prompt before generating.")
    if width not in (512, 768, 1024) or height not in (512, 768, 1024):
        raise ValueError("Width and height must be 512, 768, or 1024.")
    try:
        from gradio_client import Client
    except ImportError as exc:
        raise ImageGenerationError("Missing dependency. Install it with: python -m pip install gradio_client") from exc
    try:
        client = Client(SPACE_ID)
        result = client.predict(
            prompt=prompt.strip(),
            negative_prompt=(negative_prompt or DEFAULT_NEGATIVE_PROMPT).strip(),
            seed=0,
            randomize_seed=True,
            width=int(width),
            height=int(height),
            guidance_scale=float(guidance_scale),
            num_inference_steps=int(steps),
            api_name="/infer",
        )
    except Exception as exc:
        message = str(exc).strip().splitlines()[0][:350] or type(exc).__name__
        raise ImageGenerationError(
            f"Hugging Face Space request failed ({type(exc).__name__}): {message}. "
            "The Space may be busy, sleeping, rate-limited, or temporarily unavailable. Retry later."
        ) from exc
    source = _find_path(result)
    if source is None:
        raise ImageGenerationError(f"The Space returned an unexpected result format: {type(result).__name__}. Check the Space API docs.")
    target_dir = Path(output_dir)
    target_dir.mkdir(parents=True, exist_ok=True)
    target = target_dir / f"hf_image_{uuid.uuid4().hex[:12]}{source.suffix or '.png'}"
    shutil.copy2(source, target)
    return target
