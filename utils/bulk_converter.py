import json

input_path = "/content/drive/MyDrive/naver_news_embedded.jsonl"
output_path = "/content/drive/MyDrive/naver_news_bulk.json"

index_name = "naver_news_embedded"

with open(input_path, "r", encoding="utf-8") as infile, open(output_path, "w", encoding="utf-8") as outfile:
    for line in infile:
        doc = json.loads(line)
        doc_id = doc.get("url")  # URL을 ID로 사용할 수 있음 (중복 방지)

        meta = {
            "index": {
                "_index": index_name,
                "_id": doc_id
            }
        }

        outfile.write(json.dumps(meta, ensure_ascii=False) + "\n")
        outfile.write(json.dumps(doc, ensure_ascii=False) + "\n")

print(f"DONE: {output_path}")
