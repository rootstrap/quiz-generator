import json
from typing import List

from model.question import Question, QuestionType
from src.agent import complete_text
from src.prompts import (open_questions_func_definition,
                         prepare_prompt_multiple_choice,
                         prepare_prompt_open_question,
                         prepare_prompt_variation_question)
from src.utils import get_correct_answers, sanitize_line


def response_to_mc_questions(response: str, count) -> List[Question]:
    """
    Convert the response from the API to a list of questions
    :param response: Response to convert
    :return: List of questions
    """
    questions = []

    for question_text in response.split("\n\n"):
        question_text = question_text.strip()

        if not question_text:
            continue

        question_lines = question_text.splitlines()

        question = sanitize_line(question_lines[0], is_question=True)
        answers = list(
            map(lambda line: sanitize_line(line, is_question=False), question_lines[1:])
        )
        correct_answers = get_correct_answers(answers)

        if len(correct_answers) > 0:
            for c in correct_answers:
                answers[c] = answers[c].replace("Correct:", "")

            answers = list(map(lambda answer: answer.strip(), answers))
            # if len(set(answers)) != len(answers):
            #    print(f'duplicated options for question {question}')
            #    print(answers)
            #    continue
            questions.append(
                Question(
                    count,
                    question,
                    QuestionType.MULTIPLE_CHOICE,
                    answers=answers,
                    correct_answers=correct_answers,
                )
            )

            count += 1

    return questions


def get_variations(question_number, question, number_of_variatons) -> Question:
    prompt = prepare_prompt_variation_question(question, number_of_variatons)
    response = complete_text(prompt, False)
    custom_functions = open_questions_func_definition()
    response = complete_text(response, True, custom_functions)
    variations = json.loads(response["arguments"])["questions"].split("#")
    return Question(question_number, question, QuestionType.OPEN, variations=variations)


def get_open_questions(
    content, number_of_open_questions, number_of_variatons=0
) -> List[Question]:
    if number_of_open_questions == 0:
        return []
    prompt = prepare_prompt_open_question(content, number_of_open_questions)
    custom_functions = open_questions_func_definition()
    response = complete_text(prompt, True, custom_functions)
    questions = json.loads(response["arguments"])["questions"].split("#")
    result_questions = []
    i = 0
    if number_of_variatons > 0:
        print(f"Getting {number_of_variatons} variations")
        for question in questions:
            print(f"Getting variation for question {question}")
            result_questions.append(get_variations(i, question, number_of_variatons))
            i += 1
    else:
        for question in questions:
            result_questions.append(Question(i, question, QuestionType.OPEN))
            i += 1
    return result_questions


def get_mc_questions(
    content, number_of_mc_questions, number_of_answers
) -> List[Question]:
    questions = []
    count = 0
    current_questions = []
    if number_of_mc_questions == 0:
        return []
    while count < number_of_mc_questions:
        number_of_questions = number_of_mc_questions - count
        prompt = prepare_prompt_multiple_choice(
            content, current_questions, number_of_questions, number_of_answers
        )
        response = complete_text(prompt)
        result = response_to_mc_questions(response, count)
        if len(result) == 0:
            continue
        questions.extend(result)
        current_questions = list(map(lambda x: x.question, result))
        count = len(questions)

    questions = questions[:number_of_mc_questions]

    # put at the end
    for question in questions:
        if "None of the above" in question.answers:
            print("None of the above")
            question.answers.remove("None of the above")
            question.answers.append("None of the above")

        if "All of the above" in question.answers:
            print("All of the above")
            question.answers.remove("All of the above")
            question.answers.append("All of the above")

    return questions


def clarify_question(question: Question) -> str:
    """
    Clarify a question using GPT-3.5 Turbo
    :param question: Question to clarify
    :return: Text clarifying the question
    """
    join_questions = "\n".join(
        [f"{chr(ord('a') + i)}. {answer}" for i, answer in enumerate(question.answers)]
    )

    prompt = f"Given this question: {question.question}\n"
    prompt += f" and these answers: {join_questions}\n\n"
    prompt += (
        f"Why the correct answer is {chr(ord('a') + question.correct_answers)}?\n\n"
    )

    return complete_text(prompt)
