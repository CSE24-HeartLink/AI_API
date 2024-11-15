from dotenv import load_dotenv

print(load_dotenv())

from openai import OpenAI

client = OpenAI()

response = client.images.generate(
    model="dall-e-3",
    prompt="A detailed neoclassicism painting depicting the frustration of being put on hold during a phone call(iphone)",
    size="1024x1024",
    quality="standard",
    n=1,
)

# 생성된 이미지의 URL을 저장합니다.
image_url = response.data[0].url

print(image_url)