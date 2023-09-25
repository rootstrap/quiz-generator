import os
from typing import List
from model.question import QuestionType
import openai
import re
from dotenv import load_dotenv
import json

from model.question import Question

load_dotenv()
MODEL = os.getenv("MODEL", "gpt-3.5-turbo")


def complete_text(prompt: str, function_calling=False, custom_functions=[]) -> str:
    """
    Complete text using GPT-3.5 Turbo
    """
    if function_calling:
        response = openai.ChatCompletion.create(
            model = MODEL,
            messages = [{'role': 'user', 'content': prompt}],
            functions = custom_functions,
            function_call = 'auto'
        )
        return json.loads(response['choices'][0]['message']['function_call']['arguments'])
    else:
        messages = [{"role": "user", "content": prompt}]
        response = openai.ChatCompletion.create(model=MODEL, messages=messages)
        return response["choices"][0]["message"]["content"]

    

def prepare_prompt_multiple_choice(text: str, current_questions: list, number_of_questions: int, number_of_answers: int) -> str:
    """
    Prepare prompt to complete
    """
    prompt = (f"Create an exam of multiple choice questions with {number_of_questions} "
        f"questions and {number_of_answers} different choices for each question. "
        f"DO NOT duplicate choices within a questions."
        f"Insert the word 'Correct:' before the correct answer in its original spot. "
        f"ONLY generate the questions and choices, not the exam itself."
        f"DO NOT use all capital letters unless unless it's an acronym."
        )
        
    if len(current_questions)>0:
        prompt += f"The questions should NOT BE in {current_questions}"

    prompt +=  f"The exam should be about the following text {text}."
    return prompt

def prepare_prompt_open_question(text: str, number_of_questions: int) -> str:
    """
    Prepare prompt to complete
    """
    return (
        f"Create {number_of_questions} different questions for an exam."
        f"Only generate the questions, not the exam itself."
        f"Separate de questions with \n."
        f"The exam should be about the following text {text}."
    )

def prepare_prompt_variation_question(question: str, number_of_variations: int):
    """
    Prepare prompt to complete
    :param question: Question that we want to create variations for 
    :param number_of_variations: Number of variations for the question 
    :return: Prompt to complete
    """
    return (
        f"Create {number_of_variations} variations for the following question,"
        f"keeping the same meaning in the question, only rephrase it: {question}."
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


def get_correct_answers(answers: List[str]) -> int:
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
        answers = list(map(lambda line: sanitize_line(line, is_question=False), question_lines[1:]))
        correct_answers = get_correct_answers(answers)
        
        if len(correct_answers)>0:
            for c in correct_answers:
                answers[c] = answers[c].replace("Correct:", "")
            
            answers = list(map(lambda answer: answer.strip(), answers))
            #if len(set(answers)) != len(answers):
            #    print(f'duplicated options for question {question}')
            #    print(answers)
            #    continue
            questions.append(Question(count, 
                                    question, 
                                    QuestionType.MULTIPLE_CHOICE, 
                                    answers=answers, 
                                    correct_answers=correct_answers)
                            )

            count += 1

    return questions

def get_variations(question_number, question, number_of_variatons) -> Question:
    prompt = prepare_prompt_variation_question(question, number_of_variatons)
    response = complete_text(prompt, False)
    custom_functions = [
        {
            'name': 'extract_questions',
            'description': 'Get the questions as a array (without the question number) from the body of the input text',
            'parameters': {
                'type': 'object',
                "properties": {
                    "questions": {
                        "type": "string",
                        "description": "The list of questions WITHOUT the question number, WITHOUT newline, SEPARATED by #",
                    }
                },
                "required": ["questions"],
            }
        }
    ]
    response = complete_text(response, True, custom_functions)
    variations = response['questions'].split('#')
    return Question(question_number, question, QuestionType.OPEN, variations=variations)


def get_open_questions(content, number_of_open_questions, number_of_variatons=0) -> List[Question]:
    if (number_of_open_questions==0):
        return []
    prompt = prepare_prompt_open_question(content, number_of_open_questions)
    response = complete_text(prompt)
    custom_functions = [
        {
            'name': 'extract_questions',
            'description': 'Get the questions as a array (without the question number) from the body of the input text',
            'parameters': {
                'type': 'object',
                "properties": {
                    "questions": {
                        "type": "string",
                        "description": "The list of questions WITHOUT the question number, WITHOUT newline, SEPARATED by #",
                    }
                },
                "required": ["questions"],
            }
        }
    ]
    response = complete_text(response, True, custom_functions)
    questions = response['questions'].split('#')
    result_questions = []
    i = 0
    if number_of_variatons>0:
        print(f'Getting {number_of_variatons} variations')
        for question in questions: 
            print(f'Getting variation for question {question}')
            result_questions.append(get_variations(i, question, number_of_variatons))
            i += 1 
    else: 
        for question in questions:
            result_questions.append(Question(i, question, QuestionType.OPEN))
            i += 1 
    return result_questions

def get_mc_questions(content, number_of_mc_questions, number_of_answers) -> List[Question]:
    questions = []
    count = 0
    current_questions = []
    if (number_of_mc_questions==0):
        return []
    while count<number_of_mc_questions:
        number_of_questions = number_of_mc_questions-count
        prompt = prepare_prompt_multiple_choice(content, current_questions, number_of_questions, number_of_answers)
        response = complete_text(prompt)
        result = response_to_mc_questions(response, count)
        if len(result)==0:
            continue
        questions.extend(result)
        current_questions = list(map(lambda x:x.question, result))
        count = len(questions)
    
    questions = questions[:number_of_mc_questions]

    #put at the end 
    for question in questions:
        if 'None of the above' in question.answers:
            print('None of the above')
            question.answers.remove('None of the above')
            question.answers.append('None of the above')

        if 'All of the above' in question.answers:
            print('All of the above')
            question.answers.remove('All of the above')
            question.answers.append('All of the above')
      

    return questions



def clarify_question(question: Question) -> str:
    """
    Clarify a question using GPT-3.5 Turbo
    :param question: Question to clarify
    :return: Text clarifying the question
    """
    join_questions = "\n".join([f"{chr(ord('a') + i)}. {answer}" for i, answer in enumerate(question.answers)])

    prompt = f"Given this question: {question.question}\n"
    prompt += f" and these answers: {join_questions}\n\n"
    prompt += f"Why the correct answer is {chr(ord('a') + question.correct_answers)}?\n\n"

    return complete_text(prompt)
