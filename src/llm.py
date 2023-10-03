from langchain.chat_models import ChatOpenAI

from config.cfg import MODEL

llm = ChatOpenAI(temperature=0, model=MODEL)
