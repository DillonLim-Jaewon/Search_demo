import json
import os

import requests
from dotenv import load_dotenv
from requests.auth import HTTPBasicAuth

load_dotenv()

def clean_doc(doc, remove_fields=None):
    if remove_fields is None:
        remove_fields = ["title_vector", "content_vector", "title_with_content_vector"]
    source = doc.get("_source", {})
    for field in remove_fields:
        source.pop(field, None)
    return source

def scroll_export(
    es_host,
    index_pattern,
    username,
    password,
    output_path,
    query={"size": 500, "query": {"match_all": {}}},
    cert_path=None,
    use_cert=False,
    remove_fields=None
):
    headers = {"Content-Type": "application/json"}
    verify = cert_path if use_cert else False

    res = requests.post(
        f"{es_host}/{index_pattern}/_search?scroll=2m",
        headers=headers,
        auth=HTTPBasicAuth(username, password),
        verify=verify,
        json=query
    )

    res_json = res.json()
    scroll_id = res_json.get("_scroll_id")
    hits = res_json.get("hits", {}).get("hits", [])

    total = 0
    with open(output_path, "w", encoding="utf-8") as f:
        for doc in hits:
            cleaned = clean_doc(doc, remove_fields)
            f.write(json.dumps(cleaned, ensure_ascii=False) + "\n")
        total += len(hits)
        print(f"▶ Initial retrieved: {total}")

        while True:
            scroll_res = requests.post(
                f"{es_host}/_search/scroll",
                headers=headers,
                auth=HTTPBasicAuth(username, password),
                verify=verify,
                json={"scroll": "2m", "scroll_id": scroll_id}
            )
            scroll_json = scroll_res.json()
            hits = scroll_json.get("hits", {}).get("hits", [])
            if not hits:
                break
            for doc in hits:
                cleaned = clean_doc(doc, remove_fields)
                f.write(json.dumps(cleaned, ensure_ascii=False) + "\n")
            total += len(hits)
            print(f"▶ Retrieved {total} documents so far...")

    print(f"✅ Export completed: {output_path}")

if __name__ == "__main__":

    COMPANY_ES_HOST = os.getenv("COMPANY_ES_HOST")
    COMPANY_ES_USERNAME = os.getenv("COMPANY_ES_USERNAME")
    COMPANY_ES_PASSWORD = os.getenv("COMPANY_ES_PASSWORD")
    COMPANY_ES_CERT_PATH = os.getenv("COMPANY_ES_CERT_PATH")

    scroll_export(
        es_host=COMPANY_ES_HOST,
        index_pattern="naver_news_*",
        username=COMPANY_ES_USERNAME,
        password=COMPANY_ES_PASSWORD,
        output_path="naver_news_cleaned_full.jsonl",
        cert_path=COMPANY_ES_CERT_PATH,
        use_cert=False 
    )