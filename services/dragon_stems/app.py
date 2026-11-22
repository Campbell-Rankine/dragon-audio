import os

from src.gradio import ui

if __name__ == "__main__":
    app = ui()
    # Hugging Face Spaces sets SPACE_ID and serves the app itself, so a
    # gradio.live share tunnel is only useful when running elsewhere.
    on_spaces = "SPACE_ID" in os.environ
    app.queue(default_concurrency_limit=1).launch(
        server_name="0.0.0.0",
        server_port=int(os.environ.get("PORT", 7860)),
        share=not on_spaces,
    )
