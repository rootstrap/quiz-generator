import os
import random
import subprocess
from typing import List

import numpy as np

from model.question import Question

TEMP_MD_FILE = "__temp.md"
TEMP_PDF_FILE = "__temp.pdf"


def markdown_to_pdf(markdown: str, output_file: str):
    """
    Convert Markdown to PDF
    :param markdown: Markdown string
    :param output_file: Output file
    """
    with open(TEMP_MD_FILE, "w") as f:
        f.write(markdown)

    subprocess.run(["mdpdf", TEMP_MD_FILE, "--output", output_file, "--paper", "A4"])

    os.remove(TEMP_MD_FILE)


def generate_markdown(questions: List[Question]) -> str:
    markdown = ""
    index = 1
    for question in questions:
        markdown += f"Question {index}: "
        markdown += question.get_markdown()
        markdown += "\n"
        index += 1
    return markdown


def generate_exams(
    open_questions: List[Question],
    number_of_open: int,
    number_of_exams: int,
    output_file,
):
    open_q_split = []
    if len(open_questions) > 0:
        # assumption: number of questions small and exams small enough
        open_q = random.sample(open_questions, number_of_open * number_of_exams)
        open_q_split = np.array_split(open_q, number_of_exams)
    content = ""
    for i in range(0, number_of_exams):
        content += f"# Exam {i+1}\n\n"
        if len(open_q_split) > 0:
            content += generate_markdown(open_q_split[i].tolist())
            content += "\n"

    markdown_to_pdf(content, output_file)
