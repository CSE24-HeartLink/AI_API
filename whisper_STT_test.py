from openai import OpenAI

client = OpenAI()

audio_file = open("data/채용면접_샘플_01.wav", "rb")
transcript = client.audio.transcriptions.create(
    file=audio_file,
    model="whisper-1",
    language="ko",
    response_format="text",
    temperature=0.0,
)

print(transcript)

