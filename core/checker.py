import difflib
import re
from typing import List, Tuple

def _clean_text(text: str) -> str:
    """
    문자열에서 소문자로 변환하고, 특수문자(물음표, 마침표 등)를 제거합니다.
    단, won't, can't 같은 경우를 위해 어퍼스트로피(')는 유지합니다.
    """
    # 1. 모든 문자를 소문자로 변환
    text = text.lower()
    # 2. 정규표현식을 사용하여 단어, 숫자, 공백, 어퍼스트로피(')를 제외한 모든 문자를 제거
    text = re.sub(r"[^\w\s']", "", text)
    # 3. 양쪽 끝의 공백 제거
    return text.strip()

def compare_answers(user_answer: str, correct_answers: List[str]) -> Tuple[float, str]:
    """사용자의 답변과 정답 목록을 비교하여 가장 높은 유사도와 그 정답 문장을 반환합니다."""
    # 비교 전에 사용자의 답변을 깨끗하게 만듦
    cleaned_user_answer = _clean_text(user_answer)
    max_sim, best_match = 0.0, ""

    for correct in correct_answers:
        # 비교 전에 각 정답 문장도 깨끗하게 만듦
        cleaned_correct_answer = _clean_text(correct)
        sim = difflib.SequenceMatcher(None, cleaned_user_answer, cleaned_correct_answer).ratio()
        if sim > max_sim:
            max_sim, best_match = sim, correct
            
    return max_sim, best_match

def get_highlighted_diff_html(user_answer: str, correct_answer: str) -> str:
    """
    사용자의 답변과 정답을 비교하여, 사용자의 답변 중 틀리거나 불필요한 부분을 밑줄로 표시하고,
    빠뜨린 단어는 단어 길이만큼 '@' 기호로 표시한 HTML을 생성합니다.
    즉, '사용자의 답변'을 기준으로 교정된 형태를 보여줍니다.
    """
    cleaned_user_words = _clean_text(user_answer).split()
    cleaned_correct_words = _clean_text(correct_answer).split()

    original_user_words_for_display = user_answer.strip().split()
    original_correct_words_for_display = correct_answer.strip().split() # 빠진 단어 길이 파악용

    matcher = difflib.SequenceMatcher(None, cleaned_user_words, cleaned_correct_words)
    
    highlighted_parts = []
    
    # 밑줄 스타일 정의 (빨간색)
    underline_red_style = "text-decoration: underline; text-decoration-color: red; font-weight: bold;"
    # 빠진 단어 스타일 정의 (회색 밑줄)
    missing_word_style = "text-decoration: underline; text-decoration-color: gray; color: gray; font-weight: bold;"

    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == 'equal':
            highlighted_parts.extend(original_user_words_for_display[i1:i2])
        elif tag == 'replace':
            # 사용자 답변의 단어가 정답과 다른 경우: 사용자 답변의 해당 단어들을 밑줄
            for word_idx in range(i1, i2):
                highlighted_parts.append(f"<span style='{underline_red_style}'>{original_user_words_for_display[word_idx]}</span>")
        elif tag == 'delete':
            # 사용자 답변에만 있고 정답에는 없는 경우 (불필요하게 추가된 단어): 사용자 답변의 해당 단어들을 밑줄
            for word_idx in range(i1, i2):
                highlighted_parts.append(f"<span style='{underline_red_style}'>{original_user_words_for_display[word_idx]}</span>")
        elif tag == 'insert':
            # 정답에만 있고 사용자 답변에는 없는 경우 (사용자가 빠뜨린 단어):
            # 빠뜨린 단어들을 단어 길이만큼 '@' 기호로 표시
            for word_idx in range(j1, j2): # correct_words의 인덱스를 사용하여 빠뜨린 단어를 가져옴
                if word_idx < len(original_correct_words_for_display):
                    missing_word_original = original_correct_words_for_display[word_idx]
                    # 단어 길이만큼 '❌' 기호 생성 (알파벳, 숫자만 고려, 구두점 무시)
                    placeholder = '❌' * len(re.sub(r"[^\w]", "", missing_word_original))
                    if not placeholder: # 단어가 구두점 등으로만 이루어진 경우 (예: "!") 빈 문자열 방지
                        placeholder = '❌' # 최소 1개는 표시
                    highlighted_parts.append(f"<span style='{missing_word_style}'>[{placeholder}]</span>")
                else: # 예외 처리
                    highlighted_parts.append(f"<span style='{missing_word_style}'>[❌]</span>") # 기본 플레이스홀더
    
    return " ".join(highlighted_parts)