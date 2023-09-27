from langchain.schema import HumanMessage

from utils.llm import llm


def complete_text(prompt: str, function_calling=False, custom_functions=[]) -> str:
    """
    Complete text using GPT-3.5 Turbo
    """
    messages = [HumanMessage(content=prompt)]
    if function_calling:
        response = llm(messages, functions=custom_functions).additional_kwargs[
            "function_call"
        ]
    else:
        response = llm(messages).content
    return response
