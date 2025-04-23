import json

input_path = "/content/drive/MyDrive/naver_news_embedded.jsonl"
output_path = "/content/drive/MyDrive/naver_news_bulk.json"

index_name = "naver_news_embedded"

with open(input_path, "r", encoding="utf-8") as infile, open(output_path, "w", encoding="utf-8") as outfile:
    # Prase each line(JSONL = one JSON object per line)
    # Use the url field from the document as its _id in Elasticsearch
    # _id prevents duplicates and allow document updates if the same ID is inserted again.
    for line in infile:
        doc = json.loads(line)
        doc_id = doc.get("url")

        # Prepares the metadata action line required by the Bulk API
        # index = Action type
        # _index : Action type (could also be "update", "delete", etc)
        meta = {
            "index": {
                "_index": index_name, # Target Elasticsearch index
                "_id": doc_id # Unique document ID
            }
        }

        # Immediately after the metadata line, writes the actual JSON document
        outfile.write(json.dumps(meta, ensure_ascii=False) + "\n")
        outfile.write(json.dumps(doc, ensure_ascii=False) + "\n")

print(f"DONE: {output_path}")



# Example output(bulk format)
# one metadata line(index action)
# one document line
# { "index": { "_index": "naver_news_embedded", "_id": "https://n.news.naver.com/mnews/article/311/0001575112?sid=103" } }
# { "title": "Some news title", "content": "Some news content", "title_with_content_vector": [0.123, 0.456, ...] }
