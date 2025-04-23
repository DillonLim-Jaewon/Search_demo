# hybrid_search.py
from config import es, tokenizer, model, device
import torch
from torch.nn import functional as F
from search.query_embedding import embed_query


def hybrid_search(search_word: str, start_date: str = '2023-01-01', end_date: str = '2023-12-31') -> tuple:
    """
    Hybrid search: Keyword search + Vector search + RRF ranking.
    """
    query_vector = embed_query(search_word, normalize=True)
    res = es.search(
        index='naver_news_*',
        size=3,
        query={
            "bool": {
                "must": [{"match": {"title_with_content": search_word}}],
                "filter": [
                    {"range": {"date": {"gte": start_date, "lte": end_date}}}
                ]
            }
        },
        knn={
            "field": "title_with_content_vector",
            "k": 3,
            "num_candidates": 20,
            "query_vector": query_vector
        },
        rank={'rrf': {}},
        source_includes=["title_with_content"]
    )
    return res['hits']['hits'], res['took']