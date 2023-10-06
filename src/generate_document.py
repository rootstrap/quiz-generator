import copy
import json
import os
import subprocess
from typing import Dict, List

from config.cfg import OUTPUT_FOLDER
from model.question import Question

TEMP_MD_FILE = "__temp.md"
TEMP_PDF_FILE = "__temp.pdf"


def _markdown_to_pdf(markdown: str, output_file: str):
    """
    Convert Markdown to PDF
    :param markdown: Markdown string
    :param output_file: Output file
    """
    with open(TEMP_MD_FILE, "w") as f:
        f.write(markdown)
    output_filepath = OUTPUT_FOLDER + "/" + output_file
    subprocess.run(
        ["mdpdf", TEMP_MD_FILE, "--output", output_filepath, "--paper", "A4"]
    )

    os.remove(TEMP_MD_FILE)


def _generate_markdown(questions: List[Question]) -> str:
    markdown = ""
    index = 1
    for question in questions:
        markdown += f"Question {index}: "
        markdown += question.get_markdown()
        markdown += "\n"
        index += 1
    return markdown


def exams2pdf(exams: Dict[str, List[Question]], output_file: str):
    content = ""
    for i, exam in enumerate(exams):
        content += f"# Exam {i+1}\n\n"
        questions = exams[exam]
        if len(questions) > 0:
            content += _generate_markdown(questions)
            content += "\n"
    _markdown_to_pdf(content, output_file)


def exams2json(exams: Dict[str, List[Question]], output_file: str):
    # Open the file in write mode and use json.dump() to write the dictionary to the file
    exams_copy = copy.deepcopy(exams)
    for exam in exams_copy:
        exams_copy[exam] = list(map(lambda q: q.to_serializable(), exams_copy[exam]))
    output_filepath = OUTPUT_FOLDER + "/" + output_file
    with open(output_filepath, "w") as json_file:
        json.dump(exams_copy, json_file)
    print(f"Exams saved to {output_filepath}")
