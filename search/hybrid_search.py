from search.config import es, model, tokenizer, device
import torch
from torch.nn import functional as F


def encode_text(text: str) -> list:
    with torch.no_grad():
        encoded = tokenizer(text, return_tensors="pt", truncation=True, max_length=512, padding=True).to(device)
        output = model(**encoded)
        embedding = output.last_hidden_state.mean(dim=1)
        # embedding = F.normalize(embedding, p=2, dim=1)
        return embedding.squeeze().tolist()


def hybrid_search(query: str, start_date: str = "2023-01-01", end_date: str = "2023-12-31", k: int = 3) -> dict:
    query_vector = encode_text(query)
    res = es.search(
        index="naver_news_*",
        size=k,
        query={
            "bool": {
                "must": [
                    {"match": {"title_with_content": query}}
                ],
                "filter": [
                    {"range": {"date": {"gte": start_date, "lte": end_date}}}
                ]
            }
        },
        knn={
            "field": "title_with_content_vector",
            "k": k,
            "num_candidates": 100,
            "query_vector": query_vector
        },
        rank={"rrf": {}},
        source_includes=["title_with_content"]
    )
    return res