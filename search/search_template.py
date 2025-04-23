from search.config import es


def enroll_keyword_template():
    es.put_script(id='keyword_search_template', body={
        "script": {
            "lang": "mustache",
            "source": {
                "query": {
                    "bool": {
                        "must": [{ "match": { "title_with_content": "{{search_word}}" }}],
                        "filter": [
                            {
                                "range": {
                                    "date": {
                                        "gte": "{{start_date}}{{^start_date}}2023-01-01{{/start_date}}",
                                        "lte": "{{end_date}}{{^end_date}}2023-12-31{{/end_date}}"
                                    }
                                }
                            }
                        ]
                    }
                }
            }
        }
    })

if __name__ == "__main__":
    enroll_keyword_template()
    es.close()