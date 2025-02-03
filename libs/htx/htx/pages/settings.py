from ktem.app import BasePage


class TbSettingsPage(BasePage):

    def __init__(self, app):
        self._app = app
        self.on_building_ui()

    def on_building_ui(self):
        pass
