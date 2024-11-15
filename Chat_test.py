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

#스트리밍: 실시간으로 데이터를 전송하고 수신하는 프로세스
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
    stream=True,  # 스트림 모드 활성화
)

final_answer = [] #전체 답변을 저장할 리스트

# 스트림 모드에서는 completion.choices 를 반복문으로 순회
for chunk in completion:
    # chunk 를 저장
    chunk_content = chunk.choices[0].delta.content
    # chunk 가 문자열이면 final_answer 에 추가
    if isinstance(chunk_content, str):
        final_answer.append(chunk_content)
        # 토큰 단위로 실시간 답변 출력
        print(chunk_content, end="")

final_answer = "".join(final_answer)
print(final_answer)

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
message_history = ask("대한민국의 수도는 어디인가요?", message_history=[])
# 최초 답변
print(message_history[-1])

# 두 번째 질문
message_history = ask("이전의 내용을 영어로 답변해 주세요", message_history=message_history)
# 두 번째 답변
print(message_history[-1])

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

