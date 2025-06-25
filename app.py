import streamlit as st
import streamlit.components.v1 as components
import random
from io import BytesIO
import uuid # 위젯 키를 위한 고유 ID 생성

# --- core 폴더의 함수들 임포트 ---
from core.data_loader import load_data_from_jsonbin
from core.tts import autoplay_audio
from core.stt import process_audio_for_stt
from core.checker import compare_answers, get_highlighted_diff_html

# --- 1. 설정 및 세션 상태 초기화 ---

st.set_page_config(
    page_title="Learn-Speaking",
    page_icon="./.streamlit/static/192x192.png",
    layout="centered"
)

# --- PWA 설정을 위한 매니페스트 링크 주입 ---
st.markdown(
    '<link rel="manifest" href="/static/manifest.json">',
    unsafe_allow_html=True,
)

def reset_state_for_new_sentence():
    """새로운 문장이 선택될 때마다 관련 세션 상태를 초기화하는 함수"""
    st.session_state.user_answer = ""
    st.session_state.check_result = None
    st.session_state.show_all_correct_options = False
    st.session_state.auto_play_audio_html = None
    st.session_state.manual_audio_html = None
    
    # 오디오 위젯의 키를 변경하여 이전 녹음 기록을 초기화
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
if 'manual_audio_html' not in st.session_state: 
    st.session_state.manual_audio_html = None
if 'audio_key' not in st.session_state:
    st.session_state.audio_key = 'initial_key'

# --- 2. UI 렌더링 ---
# --- ★★★★★ 핵심 수정 사항: 빠졌던 CSS 코드 복원 ★★★★★ ---
st.markdown("""
    <style>
        /* Streamlit 앱의 메인 콘텐츠 컨테이너 패딩 및 최대 너비 조절 */
        .stMainBlockContainer {
            width: 100%;
            padding-top: 3rem;
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
            margin-top: 1px;
            margin-bottom: 1px;
        }
        
        /* st.write, st.markdown 등의 기본 p 태그 여백 줄이기 */
        .stMarkdown p {
            margin-top: 0.5rem !important;
            margin-bottom: 0.5rem !important;
        }
        /* st.info, st.success, st.warning 등 알림 위젯의 간격 조정 */
        .stAlert {
            padding-top: 5px;
            padding-bottom: 5px;
            margin-top: 5px !important;
            margin-bottom: 5px !important;
        }
            
        .sentence-container {
            display: flex;
            align-items: center;
            justify-content: flex-start;
            min-height: 80px;  /* 컨테이너의 최소 높이 지정 */
            padding: 1rem;
            border: 1px solid rgba(49, 51, 63, 0.2);
            border-radius: 0.5rem;
            margin-bottom: 12px;
        }
        .sentence-container h5 { /* h4 대신 h5로 변경된 것 같아서 수정 */
             margin: 0; /* 내부 h5 태그의 기본 마진 제거하여 정렬 개선 */
        }
            
        [data-testid="stVerticalBlock"] {
            gap: 0.5rem;
        }
        
        .stMarkdown h5 {
            padding: 0.375rem 0px 0.5rem;
        }

        .info-list-container {
            background-color: #e6f7ff; /* st.info와 유사한 연한 파란색 배경 */
            border-left: 5px solid #00bfff; /* 왼쪽 테두리 강조 (st.info 느낌) */
            padding: 10px 15px !important; /* 내부 여백 (좌우 패딩 15px로 복원) */
            border-radius: 5px; /* 살짝 둥근 모서리 */
            margin-top: 10px !important; /* 위쪽 여백 */
            margin-bottom: 20px !important; /* 아래쪽 여백 */
            color: #333; /* 텍스트 색상 (선택 사항) */
            font-size: 18px; /* 폰트 크기 (선택 사항) */
        }

        .info-list-container ul { /* ul 태그 자체의 기본 스타일 제거 */
            list-style: none !important; /* 목록 마커 제거 */
            margin: 0 !important;       /* 외부 여백 제거 */
            padding: 0 !important;      /* 내부 여백 제거 */
        }

        .info-list-container li { /* li 항목별 스타일 */
            padding-left: 0 !important; /* 필요하다면 들여쓰기를 조절 (여기서는 없앰) */
            margin-left: 0 !important; /* 혹시 모를 왼쪽 마진도 0 */
            margin-bottom: 5px; /* 각 리스트 아이템 아래 여백 */
        }

        /* 마지막 li 항목에는 margin-bottom 제거 (깔끔하게) */
        .info-list-container li:last-child {
            margin-bottom: 0;
            font-weight: bold;
        }
        
        /* get_highlighted_diff_html에서 반환하는 하이라이트 텍스트를 감싸는 div 스타일 */
        .highlighted-diff {
            font-size: 18px;
            font-weight: bold;
            margin-top: 5px !important;   /* 위쪽 마진 더 줄임 */
            margin-bottom: 15px !important; /* 아래쪽 마진도 줄임 */
        }
        .highlight-green {
            color: green;
        }
        .highlight-red {
            color: red;
            text-decoration: underline;
        }


    </style>
    """, unsafe_allow_html=True)


st.header("Learn-Speaking 🗣️")
st.write("한국어 문장을 듣고 영어로 말하는 연습을 해보세요.")
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

    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"**문장 ID: {sentence_id}** (레벨 {st.session_state.selected_level})")
    with col2:
        # 오른쪽 컬럼 안에 또 컬럼을 만들어 버튼을 오른쪽으로 밀어내는 트릭
        spacer, button_col = st.columns([2, 1]) # [여백, 버튼] 비율
        with button_col:
            if st.button("🔄 다른 문장"):
                set_new_random_sentence()
                st.rerun()

    st.markdown(
        f'<div class="sentence-container"><h5>🇰🇷 {korean_sentence}</h5></div>',
        unsafe_allow_html=True
    )
    
    audio_to_play = st.session_state.auto_play_audio_html or st.session_state.manual_audio_html
    if audio_to_play:
        components.html(audio_to_play, height=0, scrolling=False)
        st.session_state.auto_play_audio_html = None
        st.session_state.manual_audio_html = None

    if st.button("🔂 다시 듣기", use_container_width=True):
        st.session_state.manual_audio_html = autoplay_audio(korean_sentence)
        st.rerun()

    st.markdown("##### 🎤 말하기")
    
    audio_uploader = st.audio_input(
        "마이크 아이콘을 누르고 말한 뒤, 정지 버튼을 누르세요:", 
        key=st.session_state.audio_key
    )

    if audio_uploader:
        st.info("음성 분석 중...")
        
        audio_bytes_data = audio_uploader.getvalue()
        
        recognized_text = process_audio_for_stt(audio_bytes_data)

        if recognized_text and "Error" not in recognized_text:
            st.session_state.user_answer = recognized_text
            st.session_state.check_result = compare_answers(recognized_text, correct_answers)
        else:
            st.warning("음성을 인식하지 못했거나 처리 중 오류가 발생했습니다.")
            st.session_state.user_answer = "" 
            st.session_state.check_result = None
        
        st.session_state.audio_key = str(uuid.uuid4())
        st.rerun() 

    if st.session_state.user_answer:
        st.markdown("---")
        st.markdown("##### 💬 Your Answer")
        st.write(f"##### **“{st.session_state.user_answer}”**")

        if st.session_state.check_result:
            similarity, best_match = st.session_state.check_result
            similarity_percentage = similarity * 100
            st.markdown(f"> **유사도: {similarity_percentage:.1f}%**")

            if similarity_percentage >= 90:
                st.success("🎉 거의 완벽해요!")
            else: # 90% 미만일 경우에만 Corrected Answer 또는 Warning 표시
                if similarity_percentage >= 80:
                    st.info("👍 아쉽네요! 그래도 계속 도전해보세요.")
                else:
                    st.warning("🤔 조금 아쉬워요. 다시 한번 도전해보세요!")
                
                st.markdown("##### ✏️ Corrected Answer")
                highlighted_answer = get_highlighted_diff_html(st.session_state.user_answer, best_match)
                st.markdown(f"<div class='highlighted-diff'>{highlighted_answer}</div>", unsafe_allow_html=True)

    # '모든 답안 보기/숨기기' 버튼은 사용자 답변 평가 후에 위치
    button_text = "🙈 답안 숨기기" if st.session_state.show_all_correct_options else "📝 모든 답안 보기"
    if st.button(button_text, key="toggle_all_answers", use_container_width=True):
        st.session_state.show_all_correct_options = not st.session_state.show_all_correct_options
        st.rerun()

    if st.session_state.show_all_correct_options:
        st.markdown("##### 📝 Correct Answer(s) ")
        answer_html = "".join([f"<li>🇬🇧 {ans}</li>" for ans in correct_answers])
        st.markdown(f"<div class='info-list-container'><ul>{answer_html}</ul></div>", unsafe_allow_html=True)

else:
    st.warning("연습할 문장이 없습니다. 'sentences.json' 파일을 확인해주세요.")