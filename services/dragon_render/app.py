from pathlib import Path
import tempfile
import gradio as gr
from pipeline import DragonRenderPipeline
from frame.generator import generate_image
from interp.model import interpolate_frames
from utils import save_video_with_audio

### - Webhooks / handlers - ###


def render_video(
    pipeline: DragonRenderPipeline,
    audio_file_path: str
):
    print("Generating frames...")
    pipeline.generate_frames()

    print("Interpolating frames...")
    all_frames = pipeline.interpolate_frames()

    print("Saving video...")
    output_video_path = str(Path(tempfile.mktemp(suffix=".mp4")))
    save_video_with_audio(all_frames, audio_file_path, output_video_path)

    return output_video_path


def create_pipeline(
    quality: str,
    fps: float,
):
    pipe = DragonRenderPipeline(
        image_quality=quality,
        frame_rate=fps
    )

    return pipe


def add_prompt(
    pipeline: DragonRenderPipeline,
    prompt: str,
    duration: float,
):
    pipeline.add_prompt(
        prompt,
        duration
    )

    rows = [
        [p[:100], d]
        for p, d in pipeline.prompts
    ]

    return (
        pipeline,
        rows,
        pipeline.total_duration
    )


def save_image(frame_bytes: bytes):
    path = Path(tempfile.mktemp(suffix=".png"))

    with open(path, "wb") as f:
        f.write(frame_bytes)

    return str(path)


def generate_frames_stream(
    pipeline: DragonRenderPipeline
):
    gallery = []

    for prompt, duration in pipeline.prompts:

        frame = generate_image(prompt)

        pipeline.queue.add_frame(
            frame,
            duration
        )

        gallery.append(
            save_image(frame)
        )

        yield (
            pipeline,
            gallery
        )


with gr.Blocks() as demo:

    pipeline_state = gr.State()

    gr.Markdown("# Dragon Render")

    with gr.Row():

        quality = gr.Dropdown(
            ["low", "medium", "high"],
            value="medium",
            label="Quality"
        )

        fps = gr.Number(
            value=24,
            label="FPS"
        )

    create_btn = gr.Button(
        "Create Pipeline"
    )

    prompt = gr.Textbox(
        label="Prompt"
    )

    duration = gr.Number(
        value=1.0,
        label="Duration (sec)"
    )

    add_btn = gr.Button(
        "Add Prompt"
    )

    prompt_table = gr.Dataframe(
        headers=[
            "Prompt",
            "Duration"
        ]
    )

    total_duration = gr.Number(
        label="Total Duration"
    )

    generate_btn = gr.Button(
        "Generate Frames"
    )

    gallery = gr.Gallery(
        label="Generated Frames",
        columns=4
    )

    audio_file = gr.File(
        label="Audio Track",
        type="filepath"
    )

    render_btn = gr.Button(
        "Interpolate + Save Video"
    )

    output_video = gr.Video(
        label="Output Video"
    )

    create_btn.click(
        create_pipeline,
        inputs=[
            quality,
            fps
        ],
        outputs=[
            pipeline_state
        ]
    )

    add_btn.click(
        add_prompt,
        inputs=[
            pipeline_state,
            prompt,
            duration
        ],
        outputs=[
            pipeline_state,
            prompt_table,
            total_duration
        ]
    )

    generate_btn.click(
        generate_frames_stream,
        inputs=[
            pipeline_state
        ],
        outputs=[
            pipeline_state,
            gallery
        ]
    )

    render_btn.click(
        render_video,
        inputs=[
            pipeline_state,
            audio_file
        ],
        outputs=[
            output_video
        ]
    )

if __name__ == "__main__":
    demo.queue(
        max_size=100,
        default_concurrency_limit=2
    ).launch(
        server_name="0.0.0.0",
        server_port=7860,
        show_error=True
    )
