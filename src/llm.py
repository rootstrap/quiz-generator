import os

from dotenv import load_dotenv
from langchain.chat_models import ChatOpenAI

load_dotenv()
MODEL = os.getenv("MODEL", "gpt-3.5-turbo")

llm = ChatOpenAI(temperature=0, model=MODEL)
