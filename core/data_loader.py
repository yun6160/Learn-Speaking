import requests
import streamlit as st
import json

# 이 함수는 이제 여러 JSON 파일을 불러와 하나로 합치는 역할을 합니다.
@st.cache_data(ttl=3600) 
def load_data_from_github():
    """
    비공개 GitHub 레포지토리의 특정 폴더에서 모든 .json 파일을 가져와
    하나의 리스트로 합친 후, id를 재정렬하여 반환합니다.
    """
    github_token = st.secrets["github"]["token"]

    repo_owner = "yun6160"
    repo_name = "Learn-Speaking-Json"

    api_url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/contents/"

    headers = {
        "Authorization": f"token {github_token}",
        "Accept": "application/vnd.github.v3+json"
    }

    try:
        # 1. 폴더 안의 파일 목록 가져오기
        response = requests.get(api_url, headers=headers)
        response.raise_for_status()
        files = response.json()

        all_sentences = []
        
        # 2. 각 파일의 내용을 순회하며 가져오기
        for file_info in files:
            # .json 파일만 대상으로 함
            if file_info['type'] == 'file' and file_info['name'].endswith('.json'):
                file_url = file_info['download_url']
                
                file_response = requests.get(file_url, headers=headers)
                file_response.raise_for_status()
                
                # UTF-8 인코딩을 명시하여 한글 깨짐 방지
                file_response.encoding = 'utf-8'
                
                try:
                    # 각 JSON 파일의 내용을 리스트에 추가
                    sentences_in_file = file_response.json()
                    if isinstance(sentences_in_file, list):
                        all_sentences.extend(sentences_in_file)
                    else:
                        st.warning(f"'{file_info['name']}' 파일이 리스트 형태가 아닙니다. 건너뜁니다.")
                except json.JSONDecodeError:
                    st.warning(f"'{file_info['name']}' 파일의 JSON 형식이 올바르지 않습니다. 건너뜁니다.")

        # 3. 모든 문장을 합친 후, ID를 1부터 순서대로 재할당
        for i, sentence in enumerate(all_sentences):
            sentence['id'] = i + 1
            
        if not all_sentences:
            st.error("GitHub에서 문장 데이터를 가져오지 못했거나, JSON 파일이 없습니다.")
            st.stop()
            
        return all_sentences

    except requests.exceptions.RequestException as e:
        st.error(f"비공개 GitHub에서 데이터를 로드하는 중 오류가 발생했습니다: {e}")
        st.stop()
    except Exception as e:
        st.error(f"데이터 처리 중 예기치 않은 오류가 발생했습니다: {e}")
        st.stop()

def load_data_from_jsonbin():
    return load_data_from_github()
