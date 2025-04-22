# streamlit.py
import streamlit as st
import pandas as pd
from PIL import Image
from search.keyword_search import keyword_search
from search.vector_search import vector_search
from search.hybrid_search import hybrid_search


logo_image = Image.open("assets/logo.png")
st.set_page_config(
    page_title = "lloydk", 
    page_icon=logo_image,
    layout="centered"
)

st.image(logo_image, width=200, caption='LLOYDK Search Demo')


# Search area
search_word = st.text_input("검색어를 입력하세요")

# Data filter
col1, col2 = st.columns(2)
with col1:
    start_date = st.date_input("시작 날짜", pd.to_datetime("2023-01-01"))
with col2:
    end_date = st.date_input("종료 날짜", pd.to_datetime("2023-12-31"))

# 검색 버튼
if st.button("검색"):
    with st.spinner("🔎 검색 중입니다..."):
        # Text Search
        text_hits, text_took = keyword_search(search_word, start_date, end_date)
        # Vector Search
        vector_hits, vector_took = vector_search(search_word)
        # Hybrid Search
        hybrid_hits, hybrid_took = hybrid_search(search_word, start_date, end_date)

    # 결과 표시
    st.subheader("📄 검색 결과")
    col1, col2, col3 = st.columns(3)