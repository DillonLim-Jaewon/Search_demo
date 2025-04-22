# 모듈 간 공유 설정 값을 저장하고, 모든 .py파일에서 불러오는 방식
import os
from elasticsearch8 import Elasticsearch
from transformers import AutoTokenizer, AutoModel
import torch
from dotenv import load_dotenv


# .env 로드
load_dotenv()

# 환경 변수 불러오기
ES_HOST = os.getenv("ES_HOST")
ES_USERNAME = os.getenv("ES_USERNAME")
ES_PASSWORD = os.getenv("ES_PASSWORD")
CA_CERT_PATH = os.getenv("CA_CERT_PATH")

# Elasticsearch 클라이언트 생성
es = Elasticsearch(
    ES_HOST,
    basic_auth=(ES_USERNAME, ES_PASSWORD),
    ca_certs=CA_CERT_PATH,
    verify_certs=False
)

# 모델 설정
MODEL_NAME = "intfloat/multilingual-e5-base"
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModel.from_pretrained(MODEL_NAME)
device = "cuda" if torch.cuda.is_available() else "cpu"
model = model.to(device)
model.eval()