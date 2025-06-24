import streamlit as st
import json
from gtts import gTTS
import base64
from io import BytesIO
import speech_recognition as sr

@st.cache_data
def load_sentences(file_path):
    """지정된 경로의 JSON 파일을 로드합니다."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        st.error(f"'{file_path}' 파일을 찾을 수 없습니다. 파일이 정확한 위치에 있는지 확인하세요.")
        return []
    except json.JSONDecodeError:
        st.error(f"'{file_path}' 파일의 형식이 올바르지 않습니다. JSON 구조를 확인하세요.")
        return []
# TTS 텍스트 음성 출력
def autoplay_audio(text: str):
    """주어진 텍스트에 대해 자동 재생되는 오디오 HTML을 생성합니다."""
    try:
        # gTTS를 사용하여 텍스트를 mp3 오디오 데이터로 변환
        tts = gTTS(text=text, lang='ko')
        
        # 오디오 데이터를 메모리 내의 바이트 객체로 저장
        mp3_fp = BytesIO()
        tts.write_to_fp(mp3_fp)
        mp3_fp.seek(0)
        
        # Base64로 인코딩하여 HTML에 삽입할 수 있는 형태로 만듦
        b64_audio = base64.b64encode(mp3_fp.read()).decode('utf-8')
        
        # 자동 재생(autoplay) 속성을 가진 HTML <audio> 태그 생성
        audio_html = f"""
        <audio autoplay>
            <source src="data:audio/mp3;base64,{b64_audio}" type="audio/mp3">
        </audio>
        """
        return audio_html
    except Exception as e:
        st.error(f"음성 변환 중 오류가 발생했습니다: {e}")
        return None

# STT 텍스트 인식
def recognize_speech_from_mic():
    """마이크로부터 음성을 인식하여 텍스트로 변환합니다."""
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        # 사용자가 말할 준비를 할 수 있도록 안내
        st.info("주변 소음을 측정합니다. 잠시만 기다려 주세요...")
        recognizer.adjust_for_ambient_noise(source, duration=1)
        st.info("마이크 준비 완료! 말씀해주세요...")
        
        try:
            # 음성 입력을 기다림
            audio_data = recognizer.listen(source, timeout=5, phrase_time_limit=5)
            st.info("음성 인식 중...")
            
            # Google Web Speech API를 사용하여 영어로 음성 인식
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