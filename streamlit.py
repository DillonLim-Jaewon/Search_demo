# streamlit.py
import streamlit as st
import pandas as pd
from search.keyword_search import keyword_search
from search.vector_search import vector_search
from search.hybrid_search import hybrid_search

st.title("🔍 뉴스 통합 검색 데모")

# 검색어 입력
search_word = st.text_input("검색어를 입력하세요", value="네이버")

# 날짜 필터
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

    with col1:
        st.markdown(f"### 🔤 텍스트 검색
⏱ {text_took}ms")
        for doc in text_hits:
            st.markdown(f"- {doc['_source']['title_with_content'][:100]}...")

    with col2:
        st.markdown(f"### 📐 벡터 검색
⏱ {vector_took}ms")
        for doc in vector_hits:
            st.markdown(f"- {doc['_source']['title_with_content'][:100]}...")

    with col3:
        st.markdown(f"### 🤝 하이브리드 검색
⏱ {hybrid_took}ms")
        for doc in hybrid_hits:
            st.markdown(f"- {doc['_source']['title_with_content'][:100]}...")
