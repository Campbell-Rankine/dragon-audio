import tensorflow as tf
import tensorflow_hub as hub

model = hub.load("https://tfhub.dev/google/film/1")


def interpolate_frame(frame1, frame2, t):
    """
    Interpolates between two frames using the Film model.

    Args:
        frame1: A tensor representing the first frame (shape: [height, width, channels]).
        frame2: A tensor representing the second frame (shape: [height, width, channels]).
        t: A float in the range [0, 1] representing the interpolation factor.

    Returns:
        A tensor representing the interpolated frame (shape: [height, width, channels]).
    """
    # Ensure that the input frames are in the correct shape
    if frame1.shape != frame2.shape:
        raise ValueError("Input frames must have the same shape.")

    # Add batch dimension to the frames
    frame1 = tf.expand_dims(frame1, axis=0)
    frame2 = tf.expand_dims(frame2, axis=0)

    # Interpolate using the Film model
    interpolated_frame = model.interpolate(frame1, frame2, t)

    # Remove batch dimension from the output
    interpolated_frame = tf.squeeze(interpolated_frame, axis=0)

    return interpolated_frame


def interpolate_frames(frame1: bytes, frame2: bytes, duration: float, frame_rate: float) -> list[bytes]:
    """
    Interpolates between two frames and returns a list of interpolated frames.

    Args:
        frame1: A byte string representing the first frame.
        frame2: A byte string representing the second frame.
        duration: The total duration of the interpolation.
        frame_rate: The frame rate of the video.
    Returns:
        A list of byte strings representing the interpolated frames.
    """
    # get timesteps
    dt = 1/(duration*frame_rate)
    _t = [i*dt for i in range(1, int(duration*frame_rate)-1)]
    print(f"Interpolating {len(_t)} frames between the two input frames.")

    # Convert byte strings to tensors
    frame1_tensor = tf.io.decode_image(frame1)
    frame2_tensor = tf.io.decode_image(frame2)

    # Generate interpolated frames at different t values
    interpolated_frames = []
    for t in _t:
        interpolated_frame = interpolate_frame(frame1_tensor, frame2_tensor, t)
        interpolated_frame_bytes = tf.io.encode_png(interpolated_frame).numpy()
        interpolated_frames.append(interpolated_frame_bytes)

    return interpolated_frames
