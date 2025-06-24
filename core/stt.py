import speech_recognition as sr
from io import BytesIO

# 이 함수는 더 이상 마이크를 직접 사용하지 않고,
# 오디오 파일의 바이트 데이터를 직접 받아서 처리합니다.
def process_audio_for_stt(audio_bytes: bytes) -> str:
    """
    st.audio_input을 통해 받은 오디오 바이트를 STT 처리합니다.
    """
    # 데이터가 없는 경우를 위한 방어 코드
    if not audio_bytes:
        print("STT_PROCESS: No audio bytes received.")
        return ""

    r = sr.Recognizer()

    # 받은 바이트 데이터를 speech_recognition이 이해할 수 있는 AudioData 형태로 변환
    try:
        # BytesIO를 사용해 바이트 데이터를 메모리 상의 파일처럼 다룸
        audio_data_as_file = BytesIO(audio_bytes)

        # sr.AudioFile을 사용해 오디오 데이터를 로드.
        # 이 방법은 라이브러리가 오디오 포맷을 스스로 파악하게 하므로 더 안정적임.
        with sr.AudioFile(audio_data_as_file) as source:
            # record() 메서드로 전체 오디오 데이터를 읽음
            audio_data = r.record(source)

        print("STT_PROCESS: Audio data loaded successfully. Recognizing...")
        # 이제 이 AudioData를 가지고 구글 음성 인식을 수행
        recognized_text = r.recognize_google(audio_data, language="en-US")
        return recognized_text
        
    except sr.UnknownValueError:
        # 소리가 녹음됐지만 아무 말도 인식되지 않은 경우
        print("STT_PROCESS: Google Speech Recognition could not understand audio")
        return ""
    except sr.RequestError as e:
        # 구글 API 요청에 실패한 경우 (네트워크 문제, API 키 문제 등)
        print(f"STT_PROCESS: Could not request results from Google service; {e}")
        return "API Error"
    except Exception as e:
        # 그 외 예상치 못한 에러 (예: 오디오 포맷 문제)
        print(f"STT_PROCESS: An unexpected error occurred: {e}")
        return "Processing Error"
