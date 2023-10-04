from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import TokenTextSplitter

from config.cfg import CONTENT_FILEPATH, MODEL


def load_and_split_doc() -> None:
    # Load document
    loader = PyPDFLoader(CONTENT_FILEPATH)
    documents = loader.load()
    # Split document by max tokens allowed
    doc_splitter = TokenTextSplitter(model_name=MODEL, chunk_size=3500, chunk_overlap=0)
    docs = doc_splitter.split_documents(documents)
    texts = list(map(lambda doc: doc.page_content, docs))
    return texts
