import gradio as gr

from htx.explanations import GENEMAIL_EXPLANATION, GENSCHEDA_EXPLANATION, CUSTOMER_EXPLANATION, TENDER_TYPES_EXPLANATION, PROMPTS_EXPLANATION
from libs.htx.htx.pages.tender_types import TenderTypesManagement
from libs.htx.htx.pages.customer import CustomerManagement
from libs.htx.htx.pages.scheda_prompt import SchedaPromptManagement
from ktem.app import BasePage


class TbPage(BasePage):

    def __init__(self, app):
        self._app = app
        self.on_building_ui()

    def on_building_ui(self):
        with gr.Tab("Generazione Email", visible=True) as self.gen_email_tab:
            gr.HTML(
                GENEMAIL_EXPLANATION
            )
            with gr.Tab("Clienti", visible=True) as self.customer_management_tab:
                gr.HTML(
                    CUSTOMER_EXPLANATION
                )
                self.customer_management = CustomerManagement(self._app)

            with gr.Tab("Tipologie Documenti", visible=True) as self.tb_settings_tab:
                gr.HTML(
                    TENDER_TYPES_EXPLANATION
                )
                self.tb_settings = TenderTypesManagement(self._app)

        with gr.Tab("Generazione Scheda", visible=True) as self.gen_scheda_tab:
            gr.HTML(
                GENSCHEDA_EXPLANATION
            )
            with gr.Tab("Tipologie Documenti", visible=True) as self.prompts_tab:
                gr.HTML(
                    PROMPTS_EXPLANATION
                )
                self.scheda_prompt_management = SchedaPromptManagement(self._app)
