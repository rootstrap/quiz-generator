from abc import abstractmethod
from typing import Optional

import streamlit as st
import pandas as pd
from io import StringIO
from model.question import QuestionType


from model.question import Question
from utils.api import get_questions
from utils.generate_document import generate_exams
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
        for q in [q for q in QuestionType]: 
            checkbox = st.checkbox(q.value)
            if checkbox: 
                question_types.append(q)

        question_args = {}
        question_args['number_of_mc_questions'] = 0
        question_args['number_of_answers'] = 0
        question_args['number_of_mc_questions_exam'] = 0
        question_args['number_of_open_questions'] = 0 
        question_args['number_of_open_questions'] = 0
        if QuestionType.MULTIPLE_CHOICE in question_types:
            question_args['number_of_mc_questions'] = st.number_input(
                "Number of questions",
                min_value=5,
                max_value=30,
                value=10,
                help="Number of questions that will be generated", 
                key="number_of_mc_questions",
            )
            question_args['number_of_answers'] = st.number_input(
                "Number of answers for multiple choice questions",
                min_value=3,
                value=4,
                help="Number of possible answers that will be generated for each multiple choice question",
                key="number_of_answers"
            )
            question_args['number_of_mc_questions_exam'] = st.number_input(
                "Number of Multiple choice questions in an exam",
                min_value=0,
                value=5,
                help="Number of Multiple choice questions that an exam should include", 
                key="number_of_mc_questions_exam",
            )
        
        if QuestionType.OPEN in question_types:
            question_args['number_of_open_questions'] = st.number_input(
                "Number of questions",
                min_value=0,
                value=10,
                help="Number of questions that will be generated",
                key="number_of_open_questions"
            )
            question_args['number_of_variations'] = 0
            # question_args['number_of_variations'] = st.number_input(
            #     "Number of variations for open questions",
            #     min_value=0,
            #     max_value=8,
            #     value=4,
            #     help="Number of possible answers that will be generated for each open question",
            #     key="number_of_variations"
            # )
            question_args['number_of_open_questions_exam'] = st.number_input(
                "Number of Open questions in an exam",
                min_value=0,
                value=4,
                help="Number of Open questions that an exam should include", 
                key="number_of_open_questions_exam",
            )

        message = ''
        if st.button("Generate", help="Generate the questions according to the parameters"):
            
            with st.spinner('Generating questions. This may take a while...'):
                try:
                    app.questions = get_questions(question_types, question_args)
                except Exception as ex:
                    print(ex)
                    st.error("An error occurred while generating the questions. Please try again")
                    
            if app.questions is not None:
                st.success('The exams have been generated. You can download the questions as a PDF')
                left, center, right = st.columns(3)

                with left:

                    generate_exams(open_questions = app.questions[1], 
                                mc_questions =app.questions[0],
                                number_of_mc = question_args["number_of_mc_questions"],
                                number_of_open= question_args["number_of_open_questions"],
                                number_of_exams=2,
                                output_file="exams.pdf")
                
                    st.download_button(
                        "Download",
                        data=open("exams.pdf", "rb").read(),
                        file_name="exams.pdf",
                        mime="application/pdf",
                        help="Download the exams as a PDF file"
                    )

           