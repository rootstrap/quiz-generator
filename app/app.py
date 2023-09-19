import streamlit as st

from app.page import UploadFile, GenerateExamPage, PageEnum


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
            PageEnum.GENERATE_EXAM: GenerateExamPage(),
        }

        self.current_page = self.pages[PageEnum.UPLOAD_FILE]

        self._questions = []

    def render(self):
        """
        Render the app
        """
        self.current_page.render(self)

    @property
    def questions(self):
        return self._questions

    @questions.setter
    def questions(self, value):
        self._questions = value

    def set_response(self, question_index: int, response):
        self._questions[question_index].set_response(response)

    def get_answer(self, question_index: int):
        """
        Get the answer for a question
        :param question_index: index of the question
        :return: index of the answer if it exists, None otherwise
        """
        return self._questions[question_index].get_response()

    def change_page(self, page: PageEnum):
        """
        Change the current page and rerun the app
        :param page: Page to change to
        """
        self.current_page = self.pages[page]
        st.experimental_rerun()

    def reset(self):
        """
        Reset the app
        """
        self._questions = None
        self._answers = {}
        self.current_page = self.pages[PageEnum.GENERATE_EXAM]

        st.experimental_rerun()
