from transformers import AudioFlamingo3ForConditionalGeneration, AutoProcessor

model_id = "nvidia/music-flamingo-hf"
processor = AutoProcessor.from_pretrained(model_id)
model = AudioFlamingo3ForConditionalGeneration.from_pretrained(
    model_id, device_map="auto")

conversation = [
    {
        "role": "user",
        "content": [
            {"type": "text", "text": "Describe this track in full detail - tell me the genre, tempo, and key, then dive into the instruments, production style, and overall mood it creates."},
            {"type": "audio", "path": "https://huggingface.co/datasets/nvidia/MF-Skills/resolve/main/assets/song_1.mp3"},
        ],
    }
]

inputs = processor.apply_chat_template(
    conversation,
    tokenize=True,
    add_generation_prompt=True,
    return_dict=True,
).to(model.device)

outputs = model.generate(**inputs, max_new_tokens=1024)

decoded_outputs = processor.batch_decode(
    outputs[:, inputs.input_ids.shape[1]:], skip_special_tokens=True)
print(decoded_outputs)
