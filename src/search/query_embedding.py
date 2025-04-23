import torch
from config.config import tokenizer, model, device
from torch.nn import functional as F

def embed_query(text: str, normalize: bool = False) -> list:
    """
    Generate embedding for user query text.

    Args:
        text (str): The input query text.
        normalize (bool): Whether to apply L2 normalization.

    Returns:
        list: Embedded vector for the input text.
    """
    with torch.no_grad():
        encoded = tokenizer(text, return_tensors="pt", truncation=True, max_length=512, padding=True)
        encoded = {k: v.to(device) for k, v in encoded.items()}
        output = model(**encoded)
        embedding = output.last_hidden_state.mean(dim=1)
        if normalize:
            embedding = F.normalize(embedding, p=2, dim=1)
        return embedding.squeeze().tolist()