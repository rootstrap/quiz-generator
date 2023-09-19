from abc import abstractmethod
from typing import Optional

import streamlit as st
import pandas as pd
from io import StringIO
from model.question import QuestionType


from model.question import Question
from utils.api import get_questions, clarify_question
from utils.generate_document import questions_to_pdf
import numpy as np 


class PageEnum:
    """
    Enum for pages
    """
    UPLOAD_FILE = 0
    GENERATE_EXAM = 1



class Page:

    @abstractmethod
    def render(self, app):
        """
        Render the page (must be implemented by subclasses)
        """

class UploadFile(Page):
    def render(self, app):
        description = """App for generate a quiz automatically from the content of the course"""
        st.title("Generate questions")
        st.markdown(description)
        uploaded_file = st.file_uploader("Upload text file")
        if uploaded_file is not None:
            f = open("data/content.txt", "w")
            f.write(uploaded_file.getvalue().decode("utf-8"))
            f.close()
        
        _, right = st.columns(2)

        with right:
            if st.button("Configure Exam"):
                app.reset()
                app.change_page(PageEnum.GENERATE_EXAM)


class GenerateExamPage(Page):
    def render(self, app):
        st.write('What type of questions do you want to generate?:')
        question_types = []
        for name in [e.name for e in QuestionType]: 
            checkbox = st.checkbox(name)
            if checkbox: 
                question_types.append(QuestionType[name])

        question_args = {}
        if QuestionType.MULTIPLE_CHOICE in question_types:
            question_args['number_of_mc_questions'] = st.number_input(
                "Number of questions",
                min_value=5,
                max_value=30,
                value=10,
                help="Number of questions that will be generated", 
                key="number_of_mc_questions"
            )
            question_args['number_of_answers'] = st.number_input(
            "Number of answers for multiple choice questions",
            min_value=3,
            max_value=5,
            value=4,
            help="Number of possible answers that will be generated for each multiple choice question",
            key="number_of_answers"
        )
        
        if QuestionType.OPEN in question_types:
            question_args['number_of_open_questions'] = st.number_input(
                "Number of questions",
                min_value=1,
                max_value=30,
                value=5,
                help="Number of questions that will be generated",
                key="number_of_open_questions"
            )
            question_args['number_of_variations'] = st.number_input(
                "Number of variations for open questions",
                min_value=0,
                max_value=8,
                value=4,
                help="Number of possible answers that will be generated for each open question",
                key="number_of_variations"
            )

        if st.button("Generate", help="Generate the questions according to the parameters"):

            st.warning("Generating questions. This may take a while...")
            try:
                app.questions = get_questions(question_types, question_args)
            except Exception as ex:
                print(ex)
                st.error("An error occurred while generating the questions. Please try again")

        if app.questions is not None:

            st.info(
                f"An exam with {len(app.questions)} questions has been generated. You "
                f"can download the questions as a PDF file or take the exam in the app."
            )

            left, center, right = st.columns(3)

            with left:

                questions_to_pdf(app.questions, "questions.pdf")
                st.download_button(
                    "Download",
                    data=open("questions.pdf", "rb").read(),
                    file_name="questions.pdf",
                    mime="application/pdf",
                    help="Download the questions as a PDF file"
                )

           