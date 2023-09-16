from typing import List
from utils.question_type import QuestionType
import openai
import re

from model.question import Question

MODEL = "gpt-3.5-turbo"


def complete_text(prompt: str) -> str:
    """
    Complete text using GPT-3.5 Turbo
    :param prompt: Prompt to complete
    :return: Completed text
    """

    messages = [{"role": "user", "content": prompt}]
    print('prompt:', prompt)

    return openai.ChatCompletion.create(model=MODEL, messages=messages)["choices"][0]["message"]["content"]


def prepare_prompt_multiple_choice(text: str, number_of_questions: int, number_of_answers: int) -> str:
    """
    Prepare prompt to complete
    :param topics: Topics to include in the exam
    :param number_of_questions: Number of questions
    :param number_of_answers: Number of answers
    :return: Prompt to complete
    """
    return (
        f"Create an exam of multiple choice questions with {number_of_questions} "
        f"questions and {number_of_answers} of possible answers in each question. "
        f"Put the correct answer in bold (surrounded by **) in its original spot. "
        f"Only generate the questions and answers, not the exam itself."
         f"The exam should be about the following text {text}."
    )

def prepare_prompt_open_question(text: str, number_of_questions: int) -> str:
    """
    Prepare prompt to complete
    :param topics: Topics to include in the exam
    :param number_of_questions: Number of questions
    :return: Prompt to complete
    """
    return (
        f"Create {number_of_questions} questions for an exam."
        f"Only generate the questions, not the exam itself."
        f"Separate de questions with \n."
        f"The exam should be about the following text {text}."
    )

def prepare_promt_variation_question(question: str, number_of_variations: int):
    """
    Prepare prompt to complete
    :param question: Question that we want to create variations for 
    :param number_of_variations: Number of variations for the question 
    :return: Prompt to complete
    """
    return (
        f"Create {number_of_variations} for the following question: {question}.",
    )



def sanitize_line(line: str, is_question: bool) -> str:
    """
    Sanitize a line from the response
    :param line: Line to sanitize
    :param is_question: Whether the line is a question or an answer
    :return: Sanitized line
    """
    if is_question:
        new_line = re.sub(r"[0-9]+.", " ", line, count=1)
    else:
        new_line = re.sub(r"[a-eA-E][).]", " ", line, count=1)

    return new_line


def get_correct_answer(answers: List[str]) -> int:
    """
    Return the index of the correct answer
    :param answers: List of answers
    :return: Index of the correct answer if found, -1 otherwise
    """
    for index, answer in enumerate(answers):
        if answer.count("**") > 0:
            return index

    return -1


def response_to_questions(response: str) -> List[Question]:
    """
    Convert the response from the API to a list of questions
    :param response: Response to convert
    :return: List of questions
    """
    questions = []
    count = 1

    for question_text in response.split("\n\n"):

        question_text = question_text.strip()

        if not question_text:
            continue

        question_lines = question_text.splitlines()

        question = sanitize_line(question_lines[0], is_question=True)
        answers = list(map(lambda line: sanitize_line(line, is_question=False), question_lines[1:]))

        correct_answer = get_correct_answer(answers)
        answers[correct_answer] = answers[correct_answer].replace("**", "")

        answers = list(map(lambda answer: answer.strip(), answers))

        questions.append(Question(count, question, answers, correct_answer))

        count += 1

    return questions


def get_questions(question_types, question_args) -> List[Question]:
    """
    Get questions from OpenAI API
    :param topics: Topics to include in the exam
    :param number_of_questions: Number of questions
    :param number_of_answers: Number of answers
    :return: List of questions
    """
    f = open("data/content.txt", "r")
    content = f.read()
    questions = {}
    if QuestionType.MULTIPLE_CHOICE in question_types: 
        prompt = prepare_prompt_multiple_choice(content, question_args['number_of_mc_questions'], question_args['number_of_answers'])
        response = complete_text(prompt)
        print(response)
    if QuestionType.OPEN in question_types: 
        print('question_args:', question_args)
        prompt = prepare_prompt_open_question(content, question_args['number_of_open_questions'])
        response = complete_text(prompt)
        print(response)
        


def clarify_question(question: Question) -> str:
    """
    Clarify a question using GPT-3.5 Turbo
    :param question: Question to clarify
    :return: Text clarifying the question
    """
    join_questions = "\n".join([f"{chr(ord('a') + i)}. {answer}" for i, answer in enumerate(question.answers)])

    prompt = f"Given this question: {question.question}\n"
    prompt += f" and these answers: {join_questions}\n\n"
    prompt += f"Why the correct answer is {chr(ord('a') + question.correct_answer)}?\n\n"

    return complete_text(prompt)
