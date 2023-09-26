"""
    Prompts collection and retrieval
"""

prompt_multiple_choice = (
    "Create an exam of multiple choice questions with {number_of_questions} "
    "questions and {number_of_answers} different choices for each question. "
    "DO NOT duplicate choices within a questions."
    "Insert the word 'Correct:' before the correct answer in its original spot. "
    "ONLY generate the questions and choices, not the exam itself."
    "DO NOT use all capital letters unless unless it's an acronym."
    "{not_repeated_questions_prompt}"
    "The exam should be about the following text {text}."
)

prompt_open_question = (
    "Create {number_of_questions} different questions for an exam."
    "Only generate the questions, not the exam itself."
    "Separate de questions with '\n'"
    "The exam should be about the following text: {text}."
)

prompt_variation_question = (
    "Create {number_of_variations} variations for the following question,"
    "keeping the same meaning in the question, only rephrase it: {question}."
)


def prepare_prompt_multiple_choice(
    text: str, current_questions: list, number_of_questions: int, number_of_answers: int
) -> str:
    """
    Prepare multiple_choice question generation prompt
    :param text: context from which we want to generate questions
    :param current_questions: questions already generated to not generate repetitions
    :param number_of_questions: number of open questions we want
    :param number_of_answers: number of answer options that the questions should have
    :return: Prompt
    """
    if len(current_questions) > 0:
        not_repeated_questions_prompt = (
            f"The questions should NOT BE in {current_questions}"
        )
    else:
        not_repeated_questions_prompt = ""

    return prompt_multiple_choice.format(
        number_of_questions, number_of_answers, not_repeated_questions_prompt, text
    )


def prepare_prompt_open_question(text: str, number_of_questions: int) -> str:
    """
    Prepare open question generation prompt
    :param text: context from which we want to generate questions
    :param number_of_questions: number of open questions we want
    :return: Prompt
    """
    return prompt_open_question.format(number_of_questions, text)


def prepare_prompt_variation_question(question: str, number_of_variations: int):
    """
    Prepare question variants generation prompt
    :param question: Question that we want to create variations for
    :param number_of_variations: Number of variations for the question
    :return: Prompt
    """
    return prompt_variation_question.format(number_of_variations, question)
