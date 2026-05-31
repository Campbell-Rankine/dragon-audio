from typing import Literal
from uuid import uuid4
from frame.generator import generate_image
from interp.model import interpolate_frames
from utils import save_video_with_audio

ImageQualityType = Literal["low", "medium", "high"]

image_quality_mapping = {
    'low': "1080p",
    'medium': "4K",
    'high': "8K"
}


class FrameQueue:
    def __init__(self):
        self.frames = []

    def add_frame(self, frame: bytes, duration: float = 1.0):
        self.frames.append((frame, duration))

    def get_pairs(self) -> list[tuple[bytes, bytes]]:
        return [(f1, f2) for f1, f2 in zip(self.frames[::2], self.frames[1::2])]


class DragonRenderPipeline:
    def __init__(self, image_quality: ImageQualityType = "medium", frame_rate: float = 24):
        self.prompts = []
        self.total_duration = 0
        self.image_quality = image_quality_mapping[image_quality]
        self.frame_rate = frame_rate
        self.queue = FrameQueue()

    def fmt_prompt(self, prompt: str):
        return f"system: User wants to generate a music video frame. Please make sure that the image you generate is more abstract, not realistic. \
            These images will be passed to another model to interpolate between frames, so fine detail is discouraged. \
            user prompt: '{prompt}'. Please generate in {self.image_quality} quality"

    def add_prompt(self, prompt: str, duration: float = 1.0, img_bytes: bytes = None):
        if img_bytes is not None:
            self.total_duration += duration/2
            self.prompts.append((self.fmt_prompt(prompt), duration/2))
            self.queue.add_frame(img_bytes, duration)
        else:
            self.request_frame(prompt, duration)

    def request_frame(self, prompt: str, duration: float = 1.0):
        # we will interpolate between frames, so we only need half the duration for each frame
        duration = duration/2
        self.total_duration += duration
        print(
            f"Received request for frame with prompt: '{prompt}' and duration: {duration} seconds. Total duration is now {self.total_duration} seconds.")
        self.prompts.append((self.fmt_prompt(prompt), duration))

    def generate_frames(self):
        for prompt, duration in self.prompts:
            frame = generate_image(prompt)
            self.queue.add_frame((frame, duration))

    def interpolate_frames(self):
        pairs = self.queue.get_pairs()
        all_interpolated_frames = []
        for (frame1, duration1), (frame2, duration2) in pairs:
            all_interpolated_frames.append(frame1)
            interpolated_frames = interpolate_frames(
                frame1, frame2, duration1 + duration2, self.frame_rate)
            all_interpolated_frames.extend(interpolated_frames)
            all_interpolated_frames.append(frame2)
        return all_interpolated_frames

    def save_video(self, frames: list[bytes], save_to: str, audio_path: str = None):
        if not audio_path is None:
            print(f"Saving video to {save_to} with audio from {audio_path}")
            save_video_with_audio(frames, audio_path, save_to)
        else:
            print(f"Saving video to {save_to} without audio")
            save_video_with_audio(frames, None, save_to)
