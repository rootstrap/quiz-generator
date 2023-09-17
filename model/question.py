from dataclasses import dataclass
from typing import List
from enum import Enum

# class syntax
class QuestionType(Enum):
    OPEN = 0
    MULTIPLE_CHOICE = 1


@dataclass
class Question:
    """
    Class representing a question

    Attributes:
    - id: Question ID
    - question: Question text
    - answers: List of answers
    - correct_answer: Index of the correct answer
    """

    def __init__(self, id:int, 
                 question: str, 
                 question_type: QuestionType, 
                 variations:List[str] = [], 
                 answers: List[str]=[], 
                 correct_answer: int=-1):
        self.id = id
        self.question = question
        self.question_type = question_type
        self.variations = variations
        self.answers = answers
        self.correct_anser = correct_answer