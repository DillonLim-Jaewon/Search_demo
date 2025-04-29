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

# Date filter
col1, col2 = st.columns(2)
with col1:
    start_date = st.date_input("시작 날짜", pd.to_datetime("2023-01-01"))
with col2:
    end_date = st.date_input("종료 날짜", pd.to_datetime("2023-12-31"))

# 검색 버튼
if st.button("검색"):
    if not search_word.strip():
        st.warning("검색어를 입력하세요.")
    else:
        with st.spinner("검색 중입니다."):
            text_hits, text_took = keyword_search(search_word, start_date, end_date)
            vector_hits, vector_took = vector_search(search_word)
            hybrid_hits, hybrid_took = hybrid_search(search_word, start_date, end_date)

        st.subheader("검색 결과")

        # Keyword Search
        st.markdown("###Keyword Search")
        st.markdown(f"검색 시간: `{text_took} ms`")
        if text_hits:
            for hit in text_hits:
                with st.container():
                    st.markdown(f"**제목:** {hit['_source'].get('title', 'No title')}")
                    st.caption(f"📰 {hit['_source'].get('press', 'Unknown Press')} | 📅 {hit['_source'].get('date', 'No date')}")
                    st.write(hit['_source'].get('title_with_content', '')[:300] + "...")
                    url = hit['_source'].get('url', None)
                    if url:
                        st.markdown(f"[기사 보기]({url})")
                    st.divider()
        else:
            st.markdown("_No results found._")

        # Vector Search
        st.markdown("###Vector Search")
        st.markdown(f"검색 시간: `{vector_took} ms`")
        if vector_hits:
            for hit in vector_hits:
                with st.container():
                    st.markdown(f"**제목:** {hit['_source'].get('title', 'No title')}")
                    st.caption(f"📰 {hit['_source'].get('press', 'Unknown Press')} | 📅 {hit['_source'].get('date', 'No date')}")
                    st.write(hit['_source'].get('title_with_content', '')[:300] + "...")
                    url = hit['_source'].get('url', None)
                    if url:
                        st.markdown(f"[기사 보기]({url})")
                    st.divider()
        else:
            st.markdown("_No results found._")

        # Hybrid Search
        st.markdown("### 🌀 Hybrid Search")
        st.markdown(f"검색 시간: `{hybrid_took} ms`")
        if hybrid_hits:
            for hit in hybrid_hits:
                with st.container():
                    st.markdown(f"**제목:** {hit['_source'].get('title', 'No title')}")
                    st.caption(f"{hit['_source'].get('press', 'Unknown Press')} | 📅 {hit['_source'].get('date', 'No date')}")
                    st.write(hit['_source'].get('title_with_content', '')[:300] + "...")
                    url = hit['_source'].get('url', None)
                    if url:
                        st.markdown(f"[기사 보기]({url})")
                    st.divider()
        else:
            st.markdown("_No results found._")