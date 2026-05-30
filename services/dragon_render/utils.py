import io
from moviepy.video.io.VideoFileClip import VideoFileClip
from moviepy.audio.io.AudioFileClip import AudioFileClip


def save_video_with_audio(video_bytes, audio_file_path, output_file_path):
    # 1. Load the video from the byte array using an in-memory buffer
    video_buffer = io.BytesIO(video_bytes)
    video_clip = VideoFileClip(video_buffer)

    # 2. Load the audio file
    audio_clip = AudioFileClip(audio_file_path)

    # 3. Trim or loop audio to match video duration (optional but recommended)
    if audio_clip.duration > video_clip.duration:
        audio_clip = audio_clip.subclip(0, video_clip.duration)

    # 4. Attach the audio to the video clip
    final_clip = video_clip.set_audio(audio_clip)

    # 5. Write the final result to a file
    final_clip.write_videofile(
        output_file_path, codec="libx264", audio_codec="aac")

    # 6. Close clips to release resources
    video_clip.close()
    audio_clip.close()
    final_clip.close()
