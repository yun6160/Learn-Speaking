import streamlit as st
import streamlit.components.v1 as components
import random
from core.data_loader import load_data_from_jsonbin
from core.tts import autoplay_audio # 이 함수를 사용할 거임
from core.stt import recognize_speech_from_mic
from core.checker import compare_answers, get_highlighted_diff_html

# --- 1. 설정 및 세션 상태 초기화 ---

st.set_page_config(
    page_title="Learn-Speaking",
    layout="centered"
)

def reset_state_for_new_sentence():
    st.session_state.user_answer = ""
    st.session_state.check_result = None
    st.session_state.show_all_correct_options = False # '모든 답안 보기'를 눌렀을 때 모든 정답을 보여줄지 여부
    st.session_state.auto_play_audio_html = None # 새로운 문장 로드 시 자동 재생될 오디오 HTML 초기화

def set_new_random_sentence():
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
    reset_state_for_new_sentence() # 상태 초기화 후 오디오 HTML 생성
    
    # --- 새로운 문장이 설정될 때 TTS 자동 재생 HTML 생성 및 저장 ---
    if st.session_state.current_index != -1:
        korean_text_to_play = st.session_state.sentences[st.session_state.current_index]["korean"]
        audio_html = autoplay_audio(korean_text_to_play)
        if audio_html:
            st.session_state.auto_play_audio_html = audio_html # HTML을 세션 상태에 저장하여 다음 렌더링 시 재생되도록 함
    else:
        st.session_state.auto_play_audio_html = None


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
if 'show_all_correct_options' not in st.session_state: # 모든 정답 옵션 보기 토글
    st.session_state.show_all_correct_options = False
if 'auto_play_audio_html' not in st.session_state: # 자동 재생 오디오 HTML 저장용 세션 상태 추가
    st.session_state.auto_play_audio_html = None


# --- 2. UI 렌더링 ---

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


st.header("Learn-Speaking 🗣️")
st.write("레벨을 선택하고, 한국어 문장을 듣고 영어로 말하는 연습을 해보세요.")
st.write("🙏 첫 실행 시, 다시 듣기를 눌러야 음성이 나옵니다. 다른 랜덤 문장 버튼을 누르면 자동 재생됩니다.")
st.divider()

# 레벨 선택 버튼
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
    st.warning(f"레벨 {st.session_state.selected_level}에 해당하는 문장이 없습니다. sentences.json 파일을 확인해주세요.")
elif st.session_state.sentences:
    current_sentence_data = st.session_state.sentences[st.session_state.current_index]
    sentence_id = current_sentence_data["id"]
    korean_sentence = current_sentence_data["korean"]
    correct_answers = current_sentence_data["english"] # 이건 모든 정답 옵션들

    st.markdown(f"**문장 ID: {sentence_id}** (레벨 {st.session_state.selected_level})")

    with st.container(border=True):
        st.markdown(f"#### 🇰🇷 {korean_sentence}")
    
    # --- 자동 재생 오디오 삽입 (새로운 문장이 로드될 때마다) ---
    # 세션 상태에 오디오 HTML이 있으면 삽입하고 바로 초기화하여 한 번만 재생되도록 함
    if st.session_state.auto_play_audio_html:
        components.html(st.session_state.auto_play_audio_html, height=0, scrolling=False)
        st.session_state.auto_play_audio_html = None # 재생 후 HTML 초기화하여 다음 렌더링 시 다시 재생되지 않도록 함

    # --- 기존 "🎧 듣기" 버튼은 이제 수동 재청취 기능으로 변경 ---
    if st.button("🎧 다시 듣기", use_container_width=True): # 버튼 이름 변경
        audio_html = autoplay_audio(korean_sentence) # autoplay 속성 때문에 이 함수 호출 시 바로 재생됨
        if audio_html:
            components.html(audio_html, height=0)


    if st.button("🎤 말하기", use_container_width=True):
        recognized_text = recognize_speech_from_mic() # core/stt.py 파일의 recognize_speech_from_mic 함수 사용
        if recognized_text:
            st.session_state.user_answer = recognized_text
            st.session_state.check_result = compare_answers(recognized_text, correct_answers) # core/checker.py 사용
            st.session_state.show_all_correct_options = False # 말하기 버튼 누르면 '모든 답안 보기' 상태 초기화
        else:
            st.session_state.user_answer = ""
            st.session_state.check_result = None
            st.session_state.show_all_correct_options = False
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

            # 점수에 따른 메시지만 표시
            if similarity_percentage >= 90:
                st.success("🎉 거의 완벽해요!")
            elif similarity_percentage >= 85:
                st.info("👍 아쉽네요! 그래도 계속 도전해보세요.")
                
            # --- 80% 이상일 때만 '틀린 부분 밑줄' 보여주기 (여기서 80%로 기준 변경됨) ---
            if similarity_percentage >= 80: # 기존 85%에서 80%로 기준 변경 (이전 대화에서 변경된 것으로 보임)
                st.markdown("##### ✏️ Corrected Answer")
                highlighted_answer = get_highlighted_diff_html(st.session_state.user_answer, best_match)
                st.markdown(f"<div>{highlighted_answer}</div>", unsafe_allow_html=True)
            else:
                # 80% 미만이면 밑줄 친 답안도 안 보여줌
                st.warning("🤔 조금 아쉬워요. 다시 한번 도전해보세요!")


     # --- '모든 답안 보기' 토글 버튼 및 모든 정답 목록 표시 ---
    # 사용자 답변 유무와 관계없이 항상 버튼이 보이도록 조건 제거
    button_text = "🙈 답안 숨기기" if st.session_state.show_all_correct_options else "📝 모든 답안 보기"
    if st.button(button_text, key="toggle_all_answers", use_container_width=True):
        st.session_state.show_all_correct_options = not st.session_state.show_all_correct_options
        st.rerun()

    # '모든 답안 보기' 상태가 True이면 정답 목록을 표시
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