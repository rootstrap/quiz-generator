import json
import math
import random
from typing import Dict, List

import numpy as np

from model.question import Question, QuestionType
from src.agent import complete_text
from src.loader import load_and_split_doc
from src.prompts import (open_questions_func_definition,
                         prepare_prompt_multiple_choice,
                         prepare_prompt_open_question,
                         prepare_prompt_variation_question)
from src.utils import sanitize_line


def _get_correct_answers(answers: List[str]) -> int:
    """
    Return the index of the correct answer
    :param answers: List of answers
    :return: Index of the correct answer if found, -1 otherwise
    """
    correct_answers = []
    for index, answer in enumerate(answers):
        if answer.count("Correct:") > 0:
            correct_answers.append(index)

    return correct_answers


def _response_to_mc_questions(response: str, count) -> List[Question]:
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
        correct_answers = _get_correct_answers(answers)

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


def _get_variations(question, number_of_variations) -> Question:
    prompt = prepare_prompt_variation_question(question, number_of_variations)
    response = complete_text(prompt, False)
    custom_functions = open_questions_func_definition()
    response = complete_text(response, True, custom_functions)
    variations = json.loads(response["arguments"])["questions"].split("#")
    return variations


def _build_questions(questions, number_of_variations: int) -> List[Question]:
    result_questions = []
    i = 0
    for question in questions:
        if number_of_variations:
            variations = _get_variations(question, number_of_variations)
        else:
            variations = []
        q = Question(i, question, QuestionType.OPEN, variations=variations)
        result_questions.append(q)
        i += 1
    return result_questions


def get_open_questions(
    number_of_open_questions, number_of_variations=0
) -> List[Question]:
    if number_of_open_questions == 0:
        return []
    texts = load_and_split_doc()
    questions_per_page = math.ceil(number_of_open_questions / len(texts))
    questions = []
    # Create questions from text with llm
    for content in texts:
        prompt = prepare_prompt_open_question(content, questions_per_page)
        custom_function = open_questions_func_definition()
        response = complete_text(prompt, True, custom_function)
        partial_questions = json.loads(response["arguments"])["questions"].split("#")
        questions += partial_questions

    # Build question objects
    result_questions = _build_questions(questions, number_of_variations)
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
        result = _response_to_mc_questions(response, count)
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


def generate_exams(
    open_questions: List[Question],
    number_of_open: int,
    number_of_exams: int,
) -> Dict[str, List[Question]]:
    open_q_split = []
    if len(open_questions) > 0:
        # assumption: number of questions small and exams small enough
        open_q = random.sample(open_questions, number_of_open * number_of_exams)
        open_q_split = np.array_split(open_q, number_of_exams)
    exams = {}
    for i in range(0, number_of_exams):
        title = f"exam_{i+1}"
        if len(open_q_split) > 0:
            exams[title] = open_q_split[i].tolist()
        else:
            exams[title] = []
    return exams
