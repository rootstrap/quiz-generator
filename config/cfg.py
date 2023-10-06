import os

from dotenv import load_dotenv

load_dotenv()

MODEL = os.getenv("MODEL", "gpt-3.5-turbo")

OPENAI_ORG = os.getenv("ORGANIZATION_ID")
OPENAI_TOKEN = os.getenv("OPENAI_API_KEY")

DATA_FOLDER = "data"
CONTENT_FILENAME = "content.pdf"
CONTENT_FILEPATH = os.path.join(DATA_FOLDER, CONTENT_FILENAME)
OUTPUT_FOLDER = "output"
