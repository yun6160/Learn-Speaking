import streamlit as st
import streamlit.components.v1 as components
import random
from io import BytesIO
import uuid

# --- core 폴더의 함수들 임포트 ---
from core.data_loader import load_data_from_jsonbin
from core.tts import autoplay_audio
from core.stt import process_audio_for_stt
from core.checker import compare_answers, get_highlighted_diff_html

# --- 1. 설정 및 세션 상태 초기화 ---

st.set_page_config(
    page_title="Learn-Speaking",
    layout="centered"
)

def reset_state_for_new_sentence():
    """새로운 문장이 선택될 때마다 관련 세션 상태를 초기화하는 함수"""
    st.session_state.user_answer = ""
    st.session_state.check_result = None
    st.session_state.show_all_correct_options = False
    st.session_state.auto_play_audio_html = None
    
    # --- ★★★★★ 핵심 수정 사항 1: 오디오 위젯의 키를 변경하여 초기화 ★★★★★ ---
    # 새로운 고유 키를 생성하여 audio_input 위젯이 리셋되도록 함
    st.session_state.audio_key = str(uuid.uuid4())


def set_new_random_sentence():
    """현재 선택된 레벨에서 랜덤한 새 문장을 설정하는 함수"""
    level = st.session_state.selected_level
    sentences = st.session_state.sentences
    possible_indices = [i for i, s in enumerate(sentences) if s.get('level') == level]
    if not possible_indices:
        st.session_state.current_index = -1; return
    
    current_idx = st.session_state.get('current_index', -1)
    new_idx = random.choice(possible_indices)
    if len(possible_indices) > 1 and current_idx in possible_indices:
        while new_idx == current_idx: new_idx = random.choice(possible_indices)
    
    st.session_state.current_index = new_idx
    reset_state_for_new_sentence()

    if st.session_state.current_index != -1:
        korean_text_to_play = st.session_state.sentences[st.session_state.current_index]["korean"]
        audio_html = autoplay_audio(korean_text_to_play)
        if audio_html:
            st.session_state.auto_play_audio_html = audio_html

# --- 세션 상태 변수들 초기화 ---
if 'sentences' not in st.session_state:
    st.session_state.sentences = load_data_from_jsonbin()
if 'selected_level' not in st.session_state:
    st.session_state.selected_level = 1
if 'current_index' not in st.session_state:
    set_new_random_sentence()
if 'user_answer' not in st.session_state:
    st.session_state.user_answer = ""
if 'check_result' not in st.session_state:
    st.session_state.check_result = None
if 'show_all_correct_options' not in st.session_state:
    st.session_state.show_all_correct_options = False
if 'auto_play_audio_html' not in st.session_state:
    st.session_state.auto_play_audio_html = None
if 'audio_key' not in st.session_state:
    st.session_state.audio_key = 'initial_key' # 초기 키 설정

    # CSS를 주입하여 UI를 더 컴팩트하게 만듭니다.
st.markdown("""
    <style>
        /* Streamlit 앱의 메인 콘텐츠 컨테이너 패딩 및 최대 너비 조절 */
        .stMainBlockContainer {
            width: 100%;
            padding-top: 1rem;
            padding-bottom: 5rem;
            padding-left: 1rem;
            padding-right: 1rem;
            max-width: 736px;
        }

        /* 구분선(st.divider)의 상하 여백을 줄입니다. */
        hr {
            margin-top: 5px !important;
            margin-bottom: 5px !important;
        }
        /* 모든 버튼 위젯의 상하 여백을 줄입니다. */
        .stButton>button {
            margin-top: 3px;
            margin-bottom: 3px;
        }
        /* 정답 리스트의 여백을 조절합니다 */
        ul {
            padding-left: 20px;
            margin-top: 5px;
            margin-bottom: 5px;
        }
        /* st.write, st.markdown 등의 기본 p 태그 여백 줄이기 */
        .stMarkdown p {
            margin-top: 0.5rem !important;
            margin-bottom: 0.5rem !important;
        }
        /* 모든 Streamlit 위젯 컨테이너의 상하 여백 줄이기 */
        .stBlock {
            margin-bottom: 10px !important; /* 기본 위젯 블록 간 간격 */
        }
        /* st.info, st.success, st.warning 등 알림 위젯의 간격 조정 */
        .stAlert {
            padding-top: 5px;
            padding-bottom: 5px;
            margin-top: 5px !important;
            margin-bottom: 5px !important;
        }
        /* st.container 안의 여백을 줄임 */
        .stContainer {
            padding-top: 10px !important;
            padding-bottom: 10px !important;
            margin-bottom: 5px !important;
        }

        .stMarkdown div[data-testid^="stMarkdownContainer"] div {
            margin-bottom: 10px !important; /* 충분히 넓은 간격 (조절 가능) */
        }
            
        h5 {
            margin-top: 5px !important;    /* h5 위쪽 여백 */
            margin-bottom: 5px !important; /* h5 아래쪽 여백을 5px로 줄임 */
            padding-top: 0px !important;   /* h5 내부 상단 패딩 제거 */
            padding-bottom: 0px !important; /* h5 내부 하단 패딩 제거 */
            padding-left: 0px !important;  /* h5 내부 좌측 패딩 제거 */
            padding-right: 0px !important; /* h5 내부 우측 패딩 제거 */
        }

        /* (나머지 기존 CSS 코드들...) */
        /* 이전에 h1-h6를 한꺼번에 묶어뒀던 부분도 h5에 대한 설정이 더 구체적이면 오버라이드될 것임 */
        /* .stMarkdown h1, .stMarkdown h2, .stMarkdown h3,
        .stMarkdown h4, .stMarkdown h5, .stMarkdown h6 {
            margin-top: 10px !important;
            margin-bottom: 5px !important;
            padding-top: 0px !important;
            padding-bottom: 0px !important;
            padding-left: 0px !important;
            padding-right: 0px !important;
        } */

    </style>
    """, unsafe_allow_html=True)

# --- 2. UI 렌더링 ---
st.header("Learn-Speaking 🗣️")
st.write("레벨을 선택하고, 한국어 문장을 듣고 영어로 말하는 연습을 해보세요.")
st.divider()

# 레벨 선택 UI
st.write("##### **레벨 선택**")
levels = sorted(list(set(s['level'] for s in st.session_state.sentences if 'level' in s)))
if not levels:
    st.warning("연습할 문장이 없습니다. sentences.json 파일을 확인해주세요.")
else:
    cols = st.columns(len(levels))
    for i, level in enumerate(levels):
        if cols[i].button(f"Level {level}", use_container_width=True, type=("primary" if st.session_state.selected_level == level else "secondary")):
            if st.session_state.selected_level != level:
                st.session_state.selected_level = level
                set_new_random_sentence()
                st.rerun() 

st.divider()

if st.session_state.current_index == -1:
    st.warning(f"레벨 {st.session_state.selected_level}에 해당하는 문장이 없습니다.")
elif st.session_state.sentences:
    current_sentence_data = st.session_state.sentences[st.session_state.current_index]
    sentence_id = current_sentence_data["id"]
    korean_sentence = current_sentence_data["korean"]
    correct_answers = current_sentence_data["english"]

    st.markdown(f"**문장 ID: {sentence_id}** (레벨 {st.session_state.selected_level})")

    with st.container(border=True):
        st.markdown(f"#### 🇰🇷 {korean_sentence}")
    
    if st.session_state.auto_play_audio_html:
        components.html(st.session_state.auto_play_audio_html, height=0, scrolling=False)
        st.session_state.auto_play_audio_html = None

    if st.button("🎧 다시 듣기", use_container_width=True):
        audio_html = autoplay_audio(korean_sentence)
        if audio_html:
            components.html(audio_html, height=0)

    st.divider()
    
    st.markdown("##### 🎤 말하기 (마이크 아이콘을 누르고 말한 뒤, 정지 버튼을 누르세요)")
    
    audio_uploader = st.audio_input(
        "여기에 녹음하세요:", 
        key=st.session_state.audio_key # 세션 상태에 저장된 키를 사용
    )

    # 오디오 데이터가 업로드되면 (녹음이 끝나면)
    if audio_uploader:
        # 이전에 분석한 결과가 있다면, 다시 분석하지 않도록 함
        if st.session_state.user_answer == "":
            st.info("음성 분석 중...")
            
            # --- ★★★★★ 핵심 수정 사항 ★★★★★ ---
            # UploadedFile 객체에서 .getvalue()를 호출하여 실제 오디오 바이트 데이터를 추출합니다.
            audio_bytes_data = audio_uploader.getvalue()
            
            # STT 처리 함수 호출
            recognized_text = process_audio_for_stt(audio_bytes_data)

            if recognized_text and "Error" not in recognized_text:
                st.session_state.user_answer = recognized_text
                st.session_state.check_result = compare_answers(recognized_text, correct_answers)
            else:
                st.warning("음성을 인식하지 못했거나 처리 중 오류가 발생했습니다.")
                st.session_state.user_answer = "" 
                st.session_state.check_result = None
            
            # 결과 처리가 끝나면 새로고침하여 결과를 표시
            st.rerun()

    # --- 사용자 답변 및 피드백 표시 ---
    if st.session_state.user_answer:
        st.markdown("---")
        st.markdown("##### 💬 Your Answer")
        st.write(f"##### **“{st.session_state.user_answer}”**")

        if st.session_state.check_result:
            similarity, best_match = st.session_state.check_result
            similarity_percentage = similarity * 100
            st.markdown(f"> **유사도: {similarity_percentage:.1f}%**")
            if similarity_percentage >= 90: st.success("🎉 거의 완벽해요!")
            elif similarity_percentage >= 80:
                st.info("👍 아쉽네요! 그래도 계속 도전해보세요.")
                st.markdown("##### ✏️ Corrected Answer")
                highlighted_answer = get_highlighted_diff_html(st.session_state.user_answer, best_match)
                st.markdown(f"<div>{highlighted_answer}</div>", unsafe_allow_html=True)
            else:
                st.warning("🤔 조금 아쉬워요. 다시 한번 도전해보세요!")

    # --- '모든 답안 보기' 및 '다른 문장' 버튼 ---
    button_text = "🙈 답안 숨기기" if st.session_state.show_all_correct_options else "📝 모든 답안 보기"
    if st.button(button_text, key="toggle_all_answers", use_container_width=True):
        st.session_state.show_all_correct_options = not st.session_state.show_all_correct_options
        st.rerun()

    if st.session_state.show_all_correct_options:
        st.markdown("##### 📝 All Correct Answer(s) ")
        answer_html = "".join([f"<li>{ans}</li>" for ans in correct_answers])
        st.markdown(f"<ul>{answer_html}</ul>", unsafe_allow_html=True)

    st.divider()

    if st.button("🔄 다른 랜덤 문장", use_container_width=True):
        set_new_random_sentence()
        st.rerun()
else:
    st.warning("연습할 문장이 없습니다. 'sentences.json' 파일을 확인해주세요.")
