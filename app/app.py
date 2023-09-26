import streamlit as st

from app.page import (ConfigureExam, ConfigureMultipleChoice, PageEnum,
                      UploadFile)


@st.cache_resource(ttl=60 * 60 * 24)
def get_app():
    """
    Create a new app instance if it doesn't exist yet
    :return: App instance
    """
    return App()


class App:
    """
    App class that models all the app functionality
    """

    def __init__(self):
        self.pages = {
            PageEnum.UPLOAD_FILE: UploadFile(),
            PageEnum.CONFIGURE_EXAM: ConfigureExam(),
            PageEnum.CONFIGURE_MULTIPLE_CHOICE: ConfigureMultipleChoice(),
        }

        self.current_page = self.pages[PageEnum.UPLOAD_FILE]
        self.reset()

    def render(self):
        """
        Render the app
        """
        self.current_page.render(self)

    @property
    def open_questions(self):
        return self._open_questions

    @property
    def mc_questions(self):
        return self._mc_questions

    @property
    def question_args(self):
        return self._question_args

    @open_questions.setter
    def open_questions(self, value):
        self._open_questions = value

    @mc_questions.setter
    def mc_questions(self, value):
        self._mc_questions = value

    def set_question_args(self, key, value):
        self._question_args[key] = value

    def set_response(self, question_index: int, response):
        self._mc_questions[question_index].set_response(response)

    def get_answer(self, question_index: int):
        """
        Get the answer for a question
        :param question_index: index of the question
        :return: index of the answer if it exists, None otherwise
        """
        return self._mc_questions[question_index].get_response()

    def change_page(self, page: PageEnum):
        """
        Change the current page and rerun the app
        :param page: Page to change to
        """
        self.current_page = self.pages[page]

    def reset(self):
        """
        Reset the app
        """
        self._open_questions = []
        self._mc_questions = []
        self._question_args = {
            "number_of_open_questions": 0,
            "number_of_variations": 0,
            "number_of_open_questions_exam": 0,
            "number_of_mc_questions": 0,
            "number_of_mc_questions_exam": 0,
            "number_of_answers": 0,
        }
