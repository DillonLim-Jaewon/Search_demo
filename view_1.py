import pandas as pd
from torch import Tensor
import torch
import streamlit as st
from elasticsearch8 import Elasticsearch
from transformers import AutoTokenizer, AutoModel
from torch.nn import functional as F

# Elastic search connection
es = Elasticsearch(
    "https://192.168.219.159:9200",   # Fixme: 각자 endpoint에 맞게 수정
    ca_certs='../certs/mine_http_ca.crt',
    basic_auth=('elastic', 'elastic'),
    verify_certs=False
)
# multilingual-e5-base 모델과 토크나이저 로드
tokenizer = AutoTokenizer.from_pretrained('intfloat/multilingual-e5-base')
model = AutoModel.from_pretrained('intfloat/multilingual-e5-base')
model = model.to("cpu")
model.eval()

# ----------------   Embedding   ------------------- #
#  평균 풀링(average pooling)을 이용하여 문장의 벡터 임베딩을 생성하는 함수
def average_pool(last_hidden_states: Tensor, attention_mask: Tensor) -> Tensor:
    # attention mask를 이용해 패딩된 토큰에 대한 값들을 0으로 채워줍니다.
    last_hidden = last_hidden_states.masked_fill(~attention_mask[..., None].bool(), 0.0)
    # 패딩된 토큰들을 제외하고 나머지 값들의 평균을 구합니다.
    return last_hidden.sum(dim=1) / attention_mask.sum(dim=1)[..., None]

# 입력된 텍스트를 임베딩으로 변환하는 함수
def text_embedding(text):
    batch_dict = tokenizer(text, max_length=512, padding=True, truncation=True, return_tensors='pt')
    outputs = model(**batch_dict)
    embeddings = average_pool(outputs.last_hidden_state, batch_dict['attention_mask'])
    # embeddings = F.normalize(embeddings, p=2, dim=1) # Fixme: normalize 필요하면 주석 제거
    return embeddings[0].tolist()

def text_embedding_v2(text:str) -> list:
    with torch.no_grad():
        encoded = tokenizer(text, return_tensors="pt", truncation=True, max_length=512, padding=True)
        output = model(**encoded)
        embedding = output.last_hidden_state.mean(dim=1)
        # embedding = F.normalize(embedding, p=2, dim=1) # Fixme: norm
        return embedding.squeeze().tolist()
    
# ----------------   Search   ------------------- #
# put search template
def enroll_search_template() -> None:   
    es.put_script(id='keyword_search_template', body={
        "script": {
		    "size": "{{size}}{{^size}}3{{/size}}",
		    "lang": "mustache",
		    "source": {
                "query" : {
                    "bool": {
                        "must": [{ "match": { "title_with_content": "{{search_word}}" }}],
                        "filter": [
                            {
                                "range": {
                                    "date": {
                                        "gte": "{{start_date}}{{^start_date}}2023-01-01{{/start_date}}",
                                        "lte": "{{end_date}}{{^end_date}}2023-12-31{{/end_date}}"
                                    }
                                }
                            }
                        ]
                    }
                }
		    }
	    }
    })
    es.put_script(id='journalist_search_template', body={
        "script": {
            "lang": "mustache",
            "source": {
                "query": {
                    "term": { "journalists.keyword": "{{name}}" }
                },
                "size": "{{size}}{{^size}}3{{/size}}"
            }
        }
    })
    return

# text search
def text_search(**params) -> tuple:
    res = es.search_template(
        id="keyword_search_template",
        index="naver_news_*",
        params=params,
        filter_path=['took', 'hits.hits._id', 'hits.hits._score', 'hits.hits._source.date', 'hits.hits._source.title_with_content'],
        pretty=True
    )
    return res

# keyword_search (journalist)
def keyword_search(**params) -> tuple:
    res = es.search_template(
        id='journalist_search_template',
        index='naver_news_*',
        params=params,
        filter_path= ['took', 'hits.hits._id', 'hits.hits._score', 'hits.hits._source.journalists', 'hits.hits._source.title_with_content'],
        pretty=True
    )
    return res

# vector search
def vector_search(input_query:str) -> tuple:
    script_query = {
        "script_score": {
            "query": {"match_all": {}},
            "script": {
                "source": "cosineSimilarity(params.query_vector, 'title_with_content_vector') + 1.0",
                "params": {"query_vector": text_embedding(input_query)}
            }
        }
    }
    # cs = F.cosine_similarity(text_embedding(input_query), text_embedding_v2(input_query))
    # st.title(f'{cs}') # -> 1.0
    res = es.search(
        index='naver_news_*',
        size=3,
        source_includes=['title_with_content'],
        # explain=True,
        knn={
            "field":"title_with_content_vector",
            "k": 3,
            "num_candidates":100,
            "query_vector": text_embedding_v2(input_query)
            # "query_vector_builder": {
            #     "text_embedding": {
            #         "model_id": "multilingual-e5-base",
            #         "model_text": input_query
            #     }
            # }
        }
        # query=script_query
    )
    return res['hits']['hits'], res['took']

# hybrid search
def hybird_search(
        search_word:str, start_date:str='2023-01-01', end_date:str="2023-12-31") -> tuple:
    res = es.search(
        index='naver_news_*',
        size=3,
        query={
            "bool": {
                "must": [{"match": {"title_with_content": search_word}}],
                "filter": [
                    {
                        "range":{
                            "date": {
                                "gte": start_date,
                                "lte": end_date
                            }
                        }
                    }
                ]
            }
        },
        knn={
            "field": "title_with_content_vector",
            "k": 3,
            "num_candidates": 20,
            "query_vector": text_embedding(search_word)
        },
        rank={'rrf': {}},
        source_includes=["title_with_content"]
    )
    return res['hits']['hits'], res['took']

def hybrid_script_score_search(
    search_word: str,
    start_date: str = '2023-01-01',
    end_date: str = '2023-12-31'
) -> tuple:
    query_vector = text_embedding(search_word)
    res = es.search(
        index='naver_news_*',
        size=3,
        query={
            "script_score": {
                "query": {
                    "bool": {
                        "filter": [
                            {"range": {
                                "date": {"gte": start_date, "lte": end_date}
                            }},
                            {"exists": {"field": "title_with_content_vector"}}
                        ]
                    }
                },
                "script": {
                    "source": "cosineSimilarity(params.query_vector, 'title_with_content_vector') + 1.0",
                    "params": {
                        "query_vector": query_vector
                    }
                }
            }
        },
        _source=["title_with_content"]
    )
    return res["hits"]["hits"], res['took']

# main
def main() -> None:
    st.title(" Vector Search Demo ")
    # 검색어 입력 받기
    input_query = st.text_input("검색어를 입력하세요.", value = "네이버")
    # 날짜 입력 받기
    start_date = st.date_input("시작 날짜", value=pd.to_datetime("2023-01-01"))
    end_date = st.date_input("끝 날짜", value=pd.to_datetime("2023-12-31"))

    if st.button("검색"):
        col1, col2, col3 = st.columns(spec=3, border=True)
        with col1:
            st.header('text')
            res = text_search(
                search_word=input_query, 
                start_date=start_date.strftime('%Y-%m-%d'),  # 날짜 형식 맞추기
                end_date=end_date.strftime('%Y-%m-%d')
            )
            st.subheader(f'took: {res['took']}ms')
            for doc in res['hits']['hits'][:3]:
                st.markdown(f'id : {doc["_id"][-3:]}')
                st.markdown(f'score: {doc["_score"]}')
                st.markdown(f'date: {doc["_source"]["date"]}')
                st.markdown(f'title_with_content: {doc["_source"]["title_with_content"][:50]}')
                st.divider()


        with col2:
            st.header('vector')
            results, took = vector_search(input_query)
            st.subheader(f'took: {took}ms')
            for doc in res['hits']['hits'][:3]:
                st.markdown(f'id : {doc["_id"][-3:]}')
                st.markdown(f'score: {doc["_score"]}')
                st.markdown(f'date: {doc["_source"]["date"]}')
                st.markdown(f'title_with_content: {doc["_source"]["title_with_content"][:50]}')
                st.divider()
            
        with col3:
            st.header('hybrid')
            results, took = hybrid_script_score_search(input_query)
            st.subheader(f'took: {took}ms')
            for doc in res['hits']['hits'][:3]:
                st.markdown(f'id : {doc["_id"][-3:]}')
                st.markdown(f'score: {doc["_score"]}')
                st.markdown(f'date: {doc["_source"]["date"]}')
                st.markdown(f'title_with_content: {doc["_source"]["title_with_content"][:50]}')
                st.divider()

    #sidebar keyword search
    st.sidebar.header("keyword search")
    input_name = st.sidebar.text_input("기자의 이름을 입력해주세요.", value="김한준")
    res = keyword_search(name=input_name)
    st.sidebar.subheader(f"took: {res['took']}ms")
    for doc in res['hits']['hits']:
        st.sidebar.write(f'id: {doc["_id"][-3:]}')
        st.sidebar.write(f'score: {doc["_score"]}')
        st.sidebar.write(f'journalists: {doc["_source"]["journalists"]}')
        st.sidebar.write(f'news: {doc["_source"]["title_with_content"][:50]}')
        st.sidebar.divider()

if __name__ == "__main__":
    enroll_search_template()
    main()
    es.close()