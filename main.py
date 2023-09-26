import os

import openai
import streamlit as st

from app.app import get_app

# Applying our API key and organization ID to OpenAI
OPENAI_ORG = os.getenv("ORGANIZATION_ID")
OPENAI_TOKEN = os.getenv("OPENAI_API_KEY")


def initial_config():
    """
    Initial configuration of OpenAI API and streamlit
    """
    openai.organization = OPENAI_ORG
    openai.api_key = OPENAI_TOKEN

    st.set_page_config(
        page_title="Exam generator",
        page_icon=":pencil2:",
    )


def main():
    initial_config()

    app = get_app()
    app.render()


if __name__ == "__main__":
    main()
