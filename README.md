# Search_demo
This is Naver News Vector Search with Streamlit. 

# Overview

This project enables efficient search on Naver News data using Elasticsearch with support for:
	•	Keyword Search (Text-based)
	•	Vector Search (Embedding-based KNN search)
	•	Hybrid Search (Keyword + Vector + RRF ranking)

The pipeline includes embedding news content using SentenceTransformers, storing embeddings as dense vectors in Elasticsearch, and visualizing search results via a Streamlit web application.

# Project Directory Structure
```plaintext
Search_project
├── embedding_utils.py        # Utilities for embedding, normalization, and batch processing
├── bulk_converter.py         # Convert JSONL to Elasticsearch Bulk format
├── streamlit.py              # Main Streamlit app
├── search/
│   ├── keyword_search.py     # Keyword-based search logic
│   ├── vector_search.py      # Vector-based search logic
│   └── hybrid_search.py      # Hybrid search logic
├── config/
│   └── search_config.py      # Configuration for Elasticsearch and embedding models
├── .env                      # Environment variables for sensitive configs
├── requirements.txt          # Python package dependencies
└── README.md                 # Project documentation
```


#Features
Keyword Search
- Text-based search using Elasticsearch’s match query.
Vector Search
- Dense vector search (KNN) using pre-trained SentenceTransformer embeddings.
Hybrid Search
- Combines keyword and vector search results with Reciprocal Rank Fusion (RRF).
