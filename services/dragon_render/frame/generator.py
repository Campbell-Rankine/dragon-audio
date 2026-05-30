import torch
from diffusers import DiffusionPipeline

# switch to "mps" for apple devices
pipe = DiffusionPipeline.from_pretrained(
    "microsoft/Lens", dtype=torch.bfloat16, device_map="cpu")


def generate_image(prompt: str) -> bytes:
    image = pipe(prompt).images[0]
    image_bytes = image.tobytes()
    return image_bytes
