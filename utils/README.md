utils folder is used for embedding vectors and converting bulk format in Google Colab. This folder is not used in Streamlit project. 


[ Company Elasticsearch ]
        |
        |  Scroll API → JSONL (naver_news.jsonl)
        v
[ Google Colab (GPU) ]
        |
        |  SentenceTransformer Embedding
        v
[ Embedded JSONL (naver_news_embedded.jsonl) ]
        |
        |  Bulk Format 변환 (naver_news_bulk.json)
        v
[ My Server Elasticsearch (192.xxx.xxx.159) ]
        |
        |  Dense Vector Mapping → Bulk Insert
        v
[ Vector Search / Hybrid Search / Keyword Search ]
        |
        v
[ Streamlit Web App ]


Bulk format is important because
1. Efficiently insert large volumes of data into Elasticsearch
2. Allows batch processing
3. Ensures deduplication if using consistent _id
