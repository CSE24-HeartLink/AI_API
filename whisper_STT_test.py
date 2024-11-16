from openai import OpenAI

client = OpenAI()

with open(r"C:\Users\user\Desktop\CSE2024\AI_API\audio_test_1116.m4a", "rb") as audio_file:
    transcript = client.audio.transcriptions.create(
        file=audio_file,
        model="whisper-1",
        language="ko",
        response_format="text",
        temperature=0.0,
)

print(transcript)

