from openai import OpenAI

client = OpenAI()

completion = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[
        {
            "role": "system",
            "content": "당신은 파이썬 프로그래머입니다.",
        },
        {
            "role": "user",
            "content": "피보나치 수열을 생성하는 파이썬 프로그램을 작성해주세요.",
        },
    ],
)
print(completion.choices[0].message.content)