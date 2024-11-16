from openai import OpenAI

client = OpenAI()

# 답변을 JSON 형식으로 받는 예제
completion = client.chat.completions.create(
    model="gpt-3.5-turbo-1106",
    messages=[
        {
            "role": "system",
            # 답변 형식을 JSON 으로 받기 위해 프롬프트에 JSON 형식을 지정
            "content": "You are a helpful assistant designed to output JSON. You must answer in Korean.",
        },
        {
            "role": "user",
            "content": "대한민국의 수도는 어디인가요?",
        },
    ],
    response_format={"type": "json_object"},  # 답변 형식을 JSON 으로 지정
)

print(completion.choices[0].message.content)