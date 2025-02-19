import gradio as gr

from libs.htx.htx.pages.tender_types import TenderTypesManagement
from libs.htx.htx.pages.customer import CustomerManagement
from libs.htx.htx.pages.scheda_prompt import SchedaPromptManagement
from ktem.app import BasePage


class TbPage(BasePage):

    def __init__(self, app):
        self._app = app
        self.on_building_ui()

    def on_building_ui(self):
        with gr.Tab("Email Generation", visible=True) as self.gen_email_tab:
            with gr.Tab("Customers", visible=True) as self.customer_management_tab:
                self.customer_management = CustomerManagement(self._app)

            with gr.Tab("Tender Types", visible=True) as self.tb_settings_tab:
                self.tb_settings = TenderTypesManagement(self._app)

        with gr.Tab("Scheda Generation", visible=True) as self.gen_scheda_tab:
            with gr.Tab("Prompts", visible=True) as self.prompts_tab:
                self.scheda_prompt_management = SchedaPromptManagement(self._app)
