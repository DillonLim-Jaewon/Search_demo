from config.config import es

def keyword_search(search_word, start_date, end_date):
    params = {
        "search_word": search_word,
        "start_date": str(start_date),
        "end_date": str(end_date),
        "size": 3
    }
    res = es.search_template(
        id="keyword_search_template",
        index="naver_news_*",
        params=params,
        filter_path=['took', 'hits.hits._id', 'hits.hits._score', 'hits.hits._source'],
        pretty=True
    )
    return res['hits']['hits'], res['took']