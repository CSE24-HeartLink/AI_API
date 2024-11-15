from openai import OpenAI
client = OpenAI()

prompt = input("Prompt: ") # 프롬포트를 입력받음.

response = client.images.generate(
  model="dall-e-3",
  prompt=prompt,
  size="1024x1024",
  quality="hd",
  n=1,
)

image_url = response.data[0].url
print(image_url)

#주피터 노트북에서 이미지 바로 출력 가능
from IPython.display import Image
Image(url=image_url)

# 생성된 이미지를 URL로부터 다운로드하여 저장한다.
import urllib
urllib.request.unlretrieve(image_url, "generated_image.jpg")
