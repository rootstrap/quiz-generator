from dataclasses import dataclass
from typing import List
from enum import Enum

# class syntax
class QuestionType(Enum):
    OPEN = 'Open question'
    MULTIPLE_CHOICE = 'Multiple choice'


@dataclass
class Question:
    """
    Class representing a question

    Attributes:
    - id: Question ID
    - question: Question text
    - answers: List of answers
    - correct_answers: List of correct answers 
    """

    def __init__(self, 
                 id:int, 
                 question: str, 
                 question_type: QuestionType, 
                 variations:List[str] = [], 
                 answers: List[str]=[], 
                 correct_answers: List[int]=[]):
        self.id = id
        self.question = question
        self.question_type = question_type
        self.variations = variations
        self.answers = answers
        self.correct_answers = correct_answers
        self.response = []

    def set_response(self, response):
        self.response = response

    def get_response(self):
        return self.response
    
    def get_markdown(self):
        markdown = f"{self.question}\n\n " 
        if self.question_type == QuestionType.MULTIPLE_CHOICE:
            for answer in self.answers:
                markdown += f"[ ] {answer}\n\n"      
        return markdown

    def check_response(self):
        if self.question_type==QuestionType.MULTIPLE_CHOICE:
            if len(self.response)==len(self.correct_answers):
                for r in self.response:
                    if r not in self.correct_answers:
                        return False
                return True
            else:
                return False
        else:
            return False    
