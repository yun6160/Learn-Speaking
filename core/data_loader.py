# core/data_loader.py
import requests
import streamlit as st

@st.cache_data(ttl=3600) 
def load_data_from_private_github():
    github_token = st.secrets["github"]["token"]

    # 이 URL을 사용하면 돼!
    raw_url = "https://raw.githubusercontent.com/yun6160/Learn-Speaking-Json/refs/heads/main/sentences.json" 

    headers = {
        "Authorization": f"token {github_token}",
        "Accept": "application/vnd.github.v3.raw"
    }

    try:
        response = requests.get(raw_url, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"비공개 GitHub에서 데이터를 로드하는 중 오류가 발생했습니다: {e}")
        st.stop()