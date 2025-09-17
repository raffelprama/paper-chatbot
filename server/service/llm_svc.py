import os
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
load_dotenv()


model_name = os.environ.get("MODEL")
api_key = os.environ.get("API_KEY")
base_url = os.environ.get("BASE_URL")

llm = ChatOpenAI(
    model=model_name,
    temperature=0.8,
    max_tokens=None,
    timeout=None,
    max_retries=2,
    api_key=api_key,
    base_url=base_url,
)

