# Whisper API가 지원하는 25MB 미만의 파일보다 긴 오디오 파일에 대한 처리
# pydub을 사용하여 오디오를 분할

#정해진 시간에 따라 오디오 파일을 분절하여 별도의 파일로 저장
from pydub import AudioSegment
filename = "data/채용면접_샘플_02.wav"
myaudio = AudioSegment.from_mp3(filename)

# PyDub 는 밀리초 단위로 시간을 계산합니다.
thirty_seconds = 1 * 30 * 1000  # (1초 * 30) * 1000
total_milliseconds = myaudio.duration_seconds * 1000  # 전체 길이를 밀리초로 변환

# 전체 길이를 30초로 나누어서 반복할 횟수를 계산합니다.
total_iterations = int(total_milliseconds // thirty_seconds + 1)
print(total_iterations)

# 생성된 파일명을 저장할 리스트
output_filenames = []

for i in range(total_iterations):
    if i < total_iterations - 1:
        # 30초 단위로 오디오를 분할합니다.
        part_of_audio = myaudio[thirty_seconds * i: thirty_seconds * (i + 1)]
    else:
        # 마지막은 나머지 전체를 분할합니다.
        part_of_audio = myaudio[thirty_seconds * i:]

    output_filename = (
        # 예시: 채용면접_샘플_02-(1).mp3, 채용면접_샘플_02-(2).mp3 ...
        f"{filename[:-4]}-({i+1}).mp3"
    )

    # 분할된 오디오를 저장합니다.
    part_of_audio.export(output_filename, format="mp3")
    output_filenames.append(output_filename)

# 결과물(파일명) 출력
print(output_filenames)

# 분할된 오디오 파일을 텍스트로 변환환
transcripts = []

for audio_filename in output_filenames:
    audio_file = open(audio_filename, "rb")  # audio file 을 읽어옵니다.

    # transcript 를 생성합니다.
    transcript = client.audio.transcriptions.create(
        file=audio_file,
        model="whisper-1",  # 모델은 whisper-1 을 사용
        language="ko",  # 한국어를 사용
        response_format="text",  # 결과물은 text 로 출력
        temperature=0.0,
    )

    # 생성된 transcript 를 리스트에 추가합니다.
    transcripts.append(transcript)

# 전체 transcript 출력(리스트를 문자열로 변환)
final_output = "---- 분할 ---- \n".join(transcripts)
print(final_output)