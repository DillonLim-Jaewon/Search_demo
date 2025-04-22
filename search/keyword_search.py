from search.config import es

def keyword_search(search_word, start_date, end_date):
    res = es.search(
        index="naver_news_*",
        query={
            "bool": {
                "must": [
                    { "match": { "title_with_content": search_word } }
                ],
                "filter": [
                    {
                        "range": {
                            "date": {
                                "gte": start_date.strftime("%Y-%m-%d"),
                                "lte": end_date.strftime("%Y-%m-%d")
                            }
                        }
                    }
                ]
            }
        },
        size=3,
        _source=["title_with_content"]
    )
    return res["hits"]["hits"], res["took"]