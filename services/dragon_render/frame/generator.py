import torch
from diffusers import DiffusionPipeline, FluxPipeline
from Lens.lens import LensPipeline
from dotenv import load_dotenv

load_dotenv('./.env')

# switch to "mps" for apple devices
# pipe = LensPipeline.from_pretrained(
#     "microsoft/Lens-Turbo", dtype=torch.bfloat16, device_map="cpu")
pipe = FluxPipeline.from_pretrained(
    "black-forest-labs/FLUX.1-schnell", torch_dtype=torch.bfloat16)
pipe.enable_model_cpu_offload()


def generate_image(prompt: str) -> bytes:
    image = pipe(prompt).images[0]
    image_bytes = image.tobytes()
    return image_bytes
