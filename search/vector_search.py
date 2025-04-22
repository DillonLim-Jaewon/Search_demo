from search.config import es, model, tokenizer, device
import torch


def encode_text(text: str) -> list:
    with torch.no_grad():
        encoded = tokenizer(text, return_tensors="pt", truncation=True, max_length=512, padding=True).to(device)
        output = model(**encoded)
        embedding = output.last_hidden_state.mean(dim=1)
        # embedding = F.normalize(embedding, p=2, dim=1)  # Optional normalization
        return embedding.squeeze().tolist()


def vector_search(query: str, k: int = 3) -> dict:
    query_vector = encode_text(query)
    res = es.search(
        index="naver_news_*",
        size=k,
        knn={
            "field": "title_with_content_vector",
            "k": k,
            "num_candidates": 100,
            "query_vector": query_vector
        },
        source_includes=["title_with_content"]
    )
    return res