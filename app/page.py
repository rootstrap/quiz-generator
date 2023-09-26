from abc import abstractmethod
from typing import Optional

import numpy as np
import streamlit as st

from utils.api import get_open_questions
from utils.generate_document import generate_exams


class PageEnum:
    """
    Enum for pages
    """

    UPLOAD_FILE = 0
    CONFIGURE_EXAM = 1
    CONFIGURE_MULTIPLE_CHOICE = 2


class Page:
    @abstractmethod
    def render(self, app):
        """
        Render the page (must be implemented by subclasses)
        """


class UploadFile(Page):
    def render(self, app):
        st.title("Generate questions")
        st.markdown(
            """Generate a quiz automatically from the content of your the course"""
        )
        uploaded_file = st.file_uploader("Upload text file")
        if uploaded_file is not None:
            f = open("data/content.txt", "w")
            f.write(uploaded_file.getvalue().decode("utf-8"))
            f.close()

        if st.button("Configure Exam"):
            app.reset()
            app.change_page(PageEnum.CONFIGURE_EXAM)
            st.rerun()


class ConfigureExam(Page):
    def render(self, app):
        st.title("Configure Open questions")
        app.set_question_args(
            "number_of_open_questions",
            st.number_input(
                "Number of questions",
                min_value=0,
                value=30,
                help="Number of questions that will be generated",
                key="number_of_open_questions",
            ),
        )

        # question_args('number_of_variations', st.number_input(
        #     "Number of variations for open questions",
        #     min_value=0,
        #     max_value=8,
        #     value=4,
        #     help="Number of possible answers that will be generated for each open question",
        #     key="number_of_variations"
        # ))
        app.set_question_args(
            "number_of_open_questions_exam",
            st.number_input(
                "Number of Open questions in an exam",
                min_value=0,
                value=6,
                help="Number of Open questions that an exam should include",
                key="number_of_open_questions_exam",
            ),
        )

        app.set_question_args(
            "number_of_exams",
            st.number_input(
                "Number of exams to generate",
                min_value=1,
                value=3,
                help="Total number of exams",
                key="number_of_exams",
            ),
        )

        col1, col2 = st.columns(2)
        with col1:
            if st.button(
                "Generate", help="Generate the questions according to the parameters"
            ):
                if (
                    not app.question_args["number_of_open_questions_exam"]
                    * app.question_args["number_of_exams"]
                    <= app.question_args["number_of_open_questions"]
                ):
                    st.error(
                        "The number of total questions shoud be bigger than number of questions per exam * number of exams"
                    )
                else:
                    with st.spinner("Generating questions. This may take a while..."):
                        try:
                            f = open("data/content.txt", "r")
                            content = f.read()
                            # app.mc_questions = get_mc_questions(content,
                            #            app.question_args['number_of_mc_questions'],
                            #            app.question_args['number_of_answers'])
                            app.open_questions = get_open_questions(
                                content,
                                app.question_args["number_of_open_questions"],
                                app.question_args["number_of_variations"],
                            )
                        except Exception as ex:
                            print(ex)
                            st.error(
                                "An error occurred while generating the questions. Please try again"
                            )

                    if len(app.open_questions) > 0:
                        st.success(
                            "The exams have been generated. You can download the questions as a PDF"
                        )

                        generate_exams(
                            open_questions=app.open_questions,
                            number_of_open=app.question_args[
                                "number_of_open_questions_exam"
                            ],
                            number_of_exams=app.question_args["number_of_exams"],
                            output_file="exams.pdf",
                        )

                        st.download_button(
                            "Download",
                            data=open("exams.pdf", "rb").read(),
                            file_name="exams.pdf",
                            mime="application/pdf",
                            help="Download the exams as a PDF file",
                        )

        with col2:
            if st.button("Configure another exam"):
                app.reset()
                app.change_page(PageEnum.UPLOAD_FILE)
                st.rerun()


class ConfigureMultipleChoice(Page):
    def render(self, app):
        st.title("Configure Multiple choice questions")
        app.set_question_args(
            "number_of_mc_questions",
            st.number_input(
                "Number of questions",
                min_value=0,
                max_value=30,
                value=5,
                help="Number of questions that will be generated",
                key="number_of_mc_questions",
            ),
        )
        app.set_question_args(
            "number_of_answers",
            st.number_input(
                "Number of answers for multiple choice questions",
                min_value=0,
                max_value=6,
                value=4,
                help="Number of possible answers that will be generated for each multiple choice question",
                key="number_of_answers",
            ),
        )
        app.set_question_args(
            "number_of_mc_questions_exam",
            st.number_input(
                "Number of Multiple choice questions in an exam",
                min_value=0,
                value=2,
                help="Number of Multiple choice questions that an exam should include",
                key="number_of_mc_questions_exam",
            ),
        )
