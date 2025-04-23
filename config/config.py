# Purpose: Centralized setup for Elasticsearch connection and embedding model loading
#          Shared across keyword, vector, and hybrid search modules

import os
from elasticsearch8 import Elasticsearch
from transformers import AutoTokenizer, AutoModel
import torch
import asyncio
from dotenv import load_dotenv

try:
    asyncio.get_running_loop()
except RuntimeError:
    asyncio.set_event_loop(asyncio.new_event_loop())

#  Load environment variables from .env
load_dotenv()

#  Elasticsearch connection settings (from .env)
ES_HOST = os.getenv("ES_HOST")                      
ES_USERNAME = os.getenv("ES_USERNAME")              
ES_PASSWORD = os.getenv("ES_PASSWORD")              
CA_CERT_PATH = os.getenv("CA_CERT_PATH")            

#  Initialize Elasticsearch client
es = Elasticsearch(
    ES_HOST,
    basic_auth=(ES_USERNAME, ES_PASSWORD),
    ca_certs=CA_CERT_PATH,
    verify_certs=False                              
)


#  Embedding model settings
MODEL_NAME = "intfloat/multilingual-e5-base"        

# Load tokenizer and model
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModel.from_pretrained(MODEL_NAME)

#  Device setup (GPU if available, otherwise CPU)
device = "cuda" if torch.cuda.is_available() else "cpu"
model = model.to(device)
model.eval()                                    
