# vector_search.py
from config import es, tokenizer, model, device
import torch
from torch.nn import functional as F
from search.query_embedding import embed_query


# Vector search using KNN query on the embedded Elasticsearch index.
def vector_search(input_query: str) -> tuple:
    # normalize -> cosine similarity 기준
    query_vector = embed_query(input_query, normalize=True) 
    res = es.search(
        index='naver_news_*',
        size=3,
        knn={
            "field": "title_with_content_vector",
            "k": 3,
            "num_candidates": 100,
            "query_vector": query_vector
        },
        source_includes=['title_with_content']
    )
    return res['hits']['hits'], res['took']