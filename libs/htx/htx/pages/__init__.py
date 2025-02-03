import gradio as gr

from libs.htx.htx.pages.settings import TbSettingsPage
from libs.htx.htx.pages.customer import CustomerManagement
from ktem.app import BasePage


class TbPage(BasePage):

    def __init__(self, app):
        self._app = app
        self.on_building_ui()

    def on_building_ui(self):
        with gr.Tab("Customers", visible=True) as self.customer_management_tab:
            self.customer_management = CustomerManagement(self._app)

        with gr.Tab("Settings", visible=True) as self.tb_settings_tab:
            self.tb_settings = TbSettingsPage(self._app)
