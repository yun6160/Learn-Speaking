import streamlit as st
import streamlit.components.v1 as components
import random
import uuid # 위젯 키를 위한 고유 ID 생성

# --- core 폴더의 함수들 임포트 ---
from core.data_loader import load_data_from_private_github
from core.tts import autoplay_audio
from core.stt import process_audio_for_stt
from core.checker import compare_answers, get_highlighted_diff_html

# --- 1. 설정 및 세션 상태 초기화 ---

st.set_page_config(
    page_title="Learn-Speaking",
    page_icon="./.streamlit/static/512x512.png",
    layout="centered"
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
    """현재 선택된 카테고리에서 랜덤한 새 문장을 설정하는 함수"""
    category = st.session_state.selected_category
    sentences = st.session_state.sentences
    possible_indices = [i for i, s in enumerate(sentences) if s.get('category') == category]
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
    st.session_state.sentences = load_data_from_private_github()
if 'selected_category' not in st.session_state:
    # load_data_from_private_github()가 빈 리스트를 반환할 경우를 대비하여 조건부로 설정
    if st.session_state.sentences and len(st.session_state.sentences) > 0:
        # JSON 데이터에서 사용 가능한 모든 카테고리 중 첫 번째 카테고리을 기본값으로 설정
        all_categorys_in_data = sorted(list(set(s['category'] for s in st.session_state.sentences if 'category' in s)))
        if all_categorys_in_data:
            st.session_state.selected_category = all_categorys_in_data[0]
        else: # 데이터는 있지만 카테고리 키가 없는 경우
            st.session_state.selected_category = None # 또는 기본 카테고리 "기초 회화 & 미드"
            st.warning("경고: sentences.json에 'category' 키가 있는 문장이 없습니다. 기본 카테고리을 설정할 수 없습니다.")
    else:
        st.session_state.selected_category = None # 문장 데이터 자체가 없는 경우
        st.warning("경고: sentences.json 파일에서 문장 데이터를 로드하지 못했습니다.")
        
if 'current_index' not in st.session_state:
    # selected_category이 설정된 후에 set_new_random_sentence 호출
    if st.session_state.selected_category is not None:
        set_new_random_sentence()
    else:
        st.session_state.current_index = -1 # 카테고리이 없으면 -1로 초기화
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

# ★★★★★ 여기부터 CSS 파일 로드하는 코드 ★★★★★
# CSS 파일 읽기 함수
def load_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# styles/style.css 파일 로드
load_css("styles/style.css") # 파일 경로를 정확히 지정해야 해!
# ★★★★★ CSS 파일 로드 코드 끝 ★★★★★


st.header("Learn-Speaking 🗣️")
st.write("한국어 문장을 듣고 영어로 말하는 연습을 해보세요.")
st.divider()

# 카테고리 선택 UI
categorys = sorted(list(set(s['category'] for s in st.session_state.sentences if 'category' in s)))
if not categorys:
    st.warning("연습할 문장이 없습니다. sentences.json 파일을 확인해주세요.")
else:
    cols = st.columns(len(categorys))
    for i, category in enumerate(categorys):
        if cols[i].button(f"{category}", use_container_width=True, type=("primary" if st.session_state.selected_category == category else "secondary")):
            if st.session_state.selected_category != category:
                st.session_state.selected_category = category
                set_new_random_sentence()
                st.rerun() 

st.divider()

if st.session_state.current_index == -1:
    st.warning(f"카테고리 {st.session_state.selected_category}에 해당하는 문장이 없습니다.")
elif st.session_state.sentences:
    current_sentence_data = st.session_state.sentences[st.session_state.current_index]
    sentence_id = current_sentence_data["id"]
    korean_sentence = current_sentence_data["korean"]
    correct_answers = current_sentence_data["english"]

    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"**문장 ID: {sentence_id}** ({st.session_state.selected_category})")
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
                # 이 아래에 Corrected Answer를 추가
                st.markdown("##### ✏️ Corrected Answer")
            elif similarity_percentage >= 70: # 70% 이상 90% 미만일 때
                st.info("👍 아쉽네요! 그래도 계속 도전해보세요.")
                st.markdown("##### ✏️ Corrected Answer")
                highlighted_answer = get_highlighted_diff_html(st.session_state.user_answer, best_match)
                st.markdown(f"<div class='highlighted-diff'>{highlighted_answer}</div>", unsafe_allow_html=True)
            else: # 70% 미만일 때
                st.warning("🤔 조금 아쉬워요. 다시 한번 도전해보세요!")

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