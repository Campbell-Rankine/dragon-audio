import gradio as gr
import os
import soundfile as sf

from src.utils.io import get_song_name

STEM_ORDER = ["vocals", "drums", "bass", "other"]


def upload_output_root(file: str) -> str:
    """Per-upload output folder. Gradio stores each upload in its own folder
    named by a hash of the file, so reusing that name keeps two users who
    upload different songs with the same filename from overwriting each
    other's stems."""
    return f"./output/{os.path.basename(os.path.dirname(file))}"


def ui():
    with gr.Blocks() as demo:
        gr.Markdown("### 🎶 Audio Stem Splitter")

        audio_input = gr.File(label="Upload Audio", file_types=[".wav", ".mp3"])

        # Fixed slots for 4 stems
        with gr.Row():
            vocals_audio = gr.Audio(label="Vocals", type="filepath")

        with gr.Row():
            drums_audio = gr.Audio(label="Drums", type="filepath")

        with gr.Row():
            bass_audio = gr.Audio(label="Bass", type="filepath")

        with gr.Row():
            other_audio = gr.Audio(label="Other", type="filepath")

        stem_selector = gr.CheckboxGroup(
            ["vocals", "drums", "bass", "other"], label="Select stems to combine"
        )
        combine_button = gr.Button("Combine Selected")
        combined_output = gr.File(label="Download Combined Stems")



        # ---- Stem splitting ----
        def on_submit(file):
            if file is None:  # upload was cleared
                return [None, None, None, None]

            from src.stems import StemSplitter

            splitter = StemSplitter(load_on_init=True)

            labels, audios, files = splitter(file, output_path=upload_output_root(file))
            print(files, audios)
            del splitter

            # Map results back into fixed slots
            mapping = {
                "vocals": vocals_audio,
                "drums": drums_audio,
                "bass": bass_audio,
                "other": other_audio,
            }

            audio_vals = [None, None, None, None]

            for lbl, audio, _ in zip(labels, audios, files):
                if lbl in mapping:
                    idx = ["vocals", "drums", "bass", "other"].index(lbl)
                    audio_vals[idx] = audio

            return audio_vals

        audio_input.change(
            fn=on_submit,
            inputs=audio_input,
            outputs=[
                vocals_audio,
                drums_audio,
                bass_audio,
                other_audio,
            ],
        )

        # ---- Stem combining ----
        def combine_stems(file, selected):
            if file is None:
                raise gr.Error("Upload and split a song before combining stems.")
            if not selected:
                raise gr.Error("Select at least one stem to combine.")

            # Stems are saved by StemSplitter under <upload root>/<song_name>/<stem>.wav
            song_dir = f"{upload_output_root(file)}/{get_song_name(file)}"
            missing = [s for s in selected if not os.path.exists(f"{song_dir}/{s}.wav")]
            if missing:
                raise gr.Error(
                    f"Stems not found ({', '.join(missing)}). Split the song first, then combine."
                )

            # Stems share length and sample rate, so mixing is a plain sum
            combined, samplerate = None, None
            for stem_name in selected:
                audio, samplerate = sf.read(f"{song_dir}/{stem_name}.wav", dtype="float32")
                combined = audio if combined is None else combined + audio

            # Named per selection so different combinations don't overwrite each other
            name = "-".join(s for s in STEM_ORDER if s in selected)
            output_path = f"{song_dir}/combined-{name}.wav"
            # float WAV so summed peaks above 1.0 aren't clipped
            sf.write(output_path, combined, samplerate, subtype="FLOAT")
            return output_path

        combine_button.click(
            combine_stems, inputs=[audio_input, stem_selector], outputs=combined_output
        )

    return demo