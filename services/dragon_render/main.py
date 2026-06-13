from pathlib import Path
import tempfile
import gradio as gr
from pipeline import DragonRenderPipeline
from frame.generator import generate_image
from interp.model import interpolate_frames
from utils import save_video_with_audio

DO_INTERP = False

if __name__ == "__main__":
    ### generate example image ###
    pipeline = DragonRenderPipeline(
        image_quality="medium",
        frame_rate=24.0
    )

    test_prompt = "A majestic dragon soaring through the sky, with vibrant scales and fiery breath, set against a dramatic sunset backdrop."
    image_bytes = generate_image(pipeline.fmt_prompt(test_prompt))
    # add first prompt 2 seconds duration
    pipeline.add_prompt(test_prompt, duration=2.0, img_bytes=image_bytes)
    with open("./output/test_image0.png", "wb") as f:
        f.write(image_bytes)

    test_prompt2 = "A serene landscape with a calm lake reflecting the surrounding mountains, under a clear blue sky."
    image_bytes2 = generate_image(pipeline.fmt_prompt(test_prompt2))
    pipeline.add_prompt(test_prompt2, duration=2.0, img_bytes=image_bytes2)
    with open("./output/test_image1.png", "wb") as f:
        f.write(image_bytes)

    if DO_INTERP:
        interpolated_frames = pipeline.interpolate_frames()
        for idx, frame in enumerate(interpolated_frames):
            with open(f"./output/test_image{idx+1}.png", "wb") as f:
                f.write(image_bytes)

        with open(f"./output/test_image{len(interpolated_frames)+1}.png", "wb") as f:
            f.write(image_bytes2)
