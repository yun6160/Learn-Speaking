# core/tts.py (여기에 아래 코드가 정확히 반영되어 있어야 해!)

import streamlit as st # Streamlit 임포트 추가 (에러 표시용)
from gtts import gTTS
import base64
from io import BytesIO

def autoplay_audio(text: str):
    """
    주어진 텍스트에 대해 자동 재생되는 오디오 HTML을 생성합니다.
    (오디오 컨트롤러는 숨겨진 상태로 자동 재생)
    """
    try:
        tts = gTTS(text=text, lang='ko', slow=False)
        mp3_fp = BytesIO()
        tts.write_to_fp(mp3_fp)
        mp3_fp.seek(0)
        b64_audio = base64.b64encode(mp3_fp.read()).decode('utf-8')
        audio_html = f"""
        <audio autoplay style="display:none;">
            <source src="data:audio/mp3;base64,{b64_audio}" type="audio/mp3">
            Your browser does not support the audio element.
        </audio>
        """
        return audio_html
    except Exception as e:
        st.error(f"음성 변환 중 오류가 발생했습니다: {e}") # 오류 발생 시 Streamlit에 에러 메시지 표시
        return None