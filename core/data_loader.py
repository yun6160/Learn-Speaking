import streamlit as st
import requests

@st.cache_data
def load_data_from_jsonbin():
    """JSONBin.io에서 데이터를 로드합니다."""
    try:
        bin_id = st.secrets["JSONBIN_ID"]
        api_key = st.secrets["JSONBIN_API_KEY"]
        headers = {'X-Master-Key': api_key, 'X-Bin-Meta': 'false'}
        url = f'https://api.jsonbin.io/v3/b/{bin_id}/latest'
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status() # HTTP 에러가 있을 경우 예외 발생
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"데이터를 불러오는 데 실패했습니다: {e}")
    except KeyError:
        st.error("Streamlit Secrets에 JSONBIN_ID 또는 JSONBIN_API_KEY가 설정되지 않았습니다.")
    except Exception as e:
        st.error(f"알 수 없는 오류 발생: {e}")
    return []
