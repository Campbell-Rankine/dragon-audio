import torch
import os
from diffusers import DiffusionPipeline, FluxPipeline
from dotenv import load_dotenv
from accelerate import Accelerator

load_dotenv('./.env')

# switch to "mps" for apple devices
# pipe = LensPipeline.from_pretrained(
#     "microsoft/Lens-Turbo", dtype=torch.bfloat16, device_map="cpu")

accelerator = Accelerator()
pipe = FluxPipeline.from_pretrained(
    "black-forest-labs/FLUX.1-schnell",
    cache_dir=f'./{os.getenv('MODEL_DOWNLOAD_DIR')}',
    torch_dtype=torch.bfloat16, device_map='cpu'
)

# pipe = accelerator.prepare(pipe)
# pipe.enable_model_cpu_offload()


def generate_image(prompt: str) -> bytes:
    image = pipe(prompt).images[0]
    image_bytes = image.tobytes()
    return image_bytes
