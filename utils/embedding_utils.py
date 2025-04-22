from sentence_transformers import SentenceTransformer
import torch
import json
from tqdm import tqdm

model = SentenceTransformer("intfloat/multilingual-e5-base")
device = "cuda" if torch.cuda.is_available() else "cpu"
model = model.to(device)


input_path = "/content/drive/MyDrive/naver_news.jsonl"
output_path = "/content/drive/MyDrive/naver_news_embedded.jsonl"

batch_size = 1024
batch = []
total_processed = 0


with open(input_path, "r", encoding="utf-8") as infile, open(output_path, "w", encoding="utf-8") as outfile:
    for line in tqdm(infile, desc="Reading"):
        doc = json.loads(line)
        text = doc.get("title_with_content")

        if text:
            batch.append((doc, text))

        if len(batch) == batch_size:
            texts = [t for _, t in batch]
            vectors = model.encode(texts, convert_to_tensor=True, device=device).cpu().tolist()

            for (doc, _), vec in zip(batch, vectors):
                doc["title_with_content_vector"] = vec
                outfile.write(json.dumps(doc, ensure_ascii=False) + "\n")

            total_processed += len(batch)
            tqdm.write(f"✅ Total processed: {total_processed}")
            batch = []

    # 남은 배치 처리
    if batch:
        texts = [t for _, t in batch]
        vectors = model.encode(texts, convert_to_tensor=True, device=device).cpu().tolist()

        for (doc, _), vec in zip(batch, vectors):
            doc["title_with_content_vector"] = vec
            outfile.write(json.dumps(doc, ensure_ascii=False) + "\n")

        total_processed += len(batch)
        tqdm.write(f"✅ Final batch done. Total processed: {total_processed}")

print(f"🎉 All saved: {output_path}")
