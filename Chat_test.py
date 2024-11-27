from openai import OpenAI
import os

client = OpenAI()

# 이전 대화 내용의 기억
#대화의 각 부분을 message_history 리스트에 순차적으로 추가한다.

def ask(question, message_history=[], model="gpt-3.5-turbo"):
    if len(message_history) == 0:
        # 최초 질문
        message_history.append(
            {
                "role": "system",
                "content": "You are a helpful assistant. You must answer in Korean.",
            }
        )

    # 사용자 질문 추가
    message_history.append(
        {
            "role": "user",
            "content": question,
        },
    )

    # GPT에 질문을 전달하여 답변을 생성
    completion = client.chat.completions.create(
        model=model,
        messages=message_history,
    )

    # 사용자 질문에 대한 답변을 추가
    message_history.append(
        {"role": "assistant", "content": completion.choices[0].message.content}
    )

    return message_history


# 최초 질문
message_history = ask("오늘의 날씨는 어때?", message_history=[])
# 최초 답변
print(message_history[-1])

# 두 번째 질문
message_history = ask("그럼 오늘 날씨에 맞는 옷차림을 추천해줘.", message_history=message_history)
# 두 번째 답변
print(message_history[-1])

print("Current API Key:", os.environ.get('OPENAI_API_KEY'))