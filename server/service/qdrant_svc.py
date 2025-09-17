import os
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
from qdrant_client import QdrantClient
from dotenv import load_dotenv
load_dotenv()


qdran_url = os.environ.get("QDRANT_URL")
qdran_api = os.environ.get("QDRANT_API_KEY")


qdrant_client = QdrantClient(
    url=qdran_url, 
    api_key=qdran_api
)

