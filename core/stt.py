import streamlit as st
import speech_recognition as sr

def recognize_speech_from_mic():
    """마이크로부터 음성을 인식하여 텍스트로 변환합니다."""
    recognizer = sr.Recognizer()

    # --- 침묵 감지 시간 설정 ---
    # 사용자가 말을 멈춘 후, 구문이 끝났다고 간주하기까지 기다리는 시간 (초).
    # 기본값은 0.8초. 1.5초 정도로 늘려서 생각할 시간을 확보.
    recognizer.pause_threshold = 3

    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source, duration=1)
        st.info("마이크 준비 완료! 말씀해주세요...")
        
        try:
            audio_data = recognizer.listen(source, timeout=10, phrase_time_limit=15)
            st.info("음성 인식 중...")
            text = recognizer.recognize_google(audio_data, language='en-US')
            return text
        except sr.WaitTimeoutError:
            st.warning("음성 입력 시간이 초과되었습니다. 다시 시도해주세요.")
            return None
        except sr.UnknownValueError:
            st.warning("음성을 이해할 수 없습니다. 더 명확하게 말씀해주세요.")
            return None
        except sr.RequestError as e:
            st.error(f"Google 음성 인식 서비스에 연결할 수 없습니다: {e}")
            return None
