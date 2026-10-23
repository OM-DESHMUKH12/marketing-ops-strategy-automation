"""Manual online smoke test; run explicitly, not with pytest."""

from gradio_client import Client
from pathlib import Path
import shutil

SPACE = "stabilityai/stable-diffusion-3.5-large"

prompt = (
    "Professional industrial product advertising photograph, "
    "circular TCT metal cutting saw blade on a dark charcoal surface, "
    "realistic steel teeth, premium studio lighting, "
    "clean B2B manufacturing campaign, landscape composition, "
    "photorealistic, no text, no watermark"
)

print("Connecting to Hugging Face Space...")
client = Client(SPACE)

print("Generating image. The Space may have a queue...")
result = client.predict(
    prompt=prompt,
    negative_prompt="blurry, distorted blade, deformed teeth, watermark, text",
    seed=0,
    randomize_seed=True,
    width=1024,
    height=1024,
    guidance_scale=4.5,
    num_inference_steps=40,
    api_name="/infer",
)

print("API result:", result)

def find_image_path(value):
    if isinstance(value, str):
        path = Path(value)
        if path.is_file():
            return path
    if isinstance(value, dict):
        for key in ("path", "name"):
            item = value.get(key)
            if isinstance(item, str) and Path(item).is_file():
                return Path(item)
    if isinstance(value, (list, tuple)):
        for item in value:
            found = find_image_path(item)
            if found:
                return found
    return None

image_path = find_image_path(result)

if image_path:
    output = Path("generated_marketing_image.png")
    shutil.copy2(image_path, output)
    print(f"Image saved to: {output.resolve()}")
else:
    print(
        "No local image path detected. Inspect the API result above "
        "to identify its returned image format."
    )
