import gradio as gr
import pandas as pd
from ktem.app import BasePage

from sqlmodel import Session, select
from ktem.db.models import TenderType, engine

from libs.htx.htx.service.tender_types import DEFAULT_ATTACHMENT_DESCRIPTION, \
    DEFAULT_CUSTOMER_DESCRIPTION, DEFAULT_TASK_DESCRIPTION, DEFAULT_TEMPLATE_DESCRIPTION


class TenderTypesManagement(BasePage):

    def __init__(self, app):
        self._app = app
        self.on_building_ui()

    def on_building_ui(self):
        with gr.Tab(label="Tender Types list"):
            self.state_tender_type_list = gr.State(value=None)
            self.tender_type_list = gr.DataFrame(
                headers=["id", "name", "description", "attachment description", "tender_type description", "task description", "template description"],
                interactive=False,
                column_widths=[50, 200, 200, 200, 200, 200, 200],
            )

            with gr.Group(visible=False) as self._selected_panel:
                self.selected_tender_type_id = gr.Number(value=-1, visible=False)
                self.name_edit = gr.Textbox(label="Name")
                self.description_edit = gr.Textbox(label="Description", lines=3)
                self.attachment_description_edit = gr.Textbox(label="Attachment Description", lines=3)
                self.customer_description_edit = gr.Textbox(label="Customer Description", lines=3)
                self.task_description_edit = gr.Textbox(label="Task Description", lines=3)
                self.template_description_edit = gr.Textbox(label="Template Description", lines=3)

            with gr.Row(visible=False) as self._selected_panel_btn:
                with gr.Column():
                    self.btn_edit_save = gr.Button("Save")
                with gr.Column():
                    self.btn_delete = gr.Button("Delete")
                    with gr.Row():
                        self.btn_delete_yes = gr.Button(
                            "Confirm delete", variant="primary", visible=False
                        )
                        self.btn_delete_no = gr.Button("Cancel", visible=False)
                with gr.Column():
                    self.btn_close = gr.Button("Close")

        with gr.Tab(label="Create Tender Type"):
            self.name_new = gr.Textbox(label="Name", interactive=True)
            self.description_new = gr.Textbox(
                label="Description", lines=3, interactive=True,
            )
            self.attachment_description_new = gr.Textbox(
                label="Attachment Description", lines=3, interactive=True,
                value=DEFAULT_ATTACHMENT_DESCRIPTION
            )
            self.customer_description_new = gr.Textbox(
                label="Customer Description", lines=3, interactive=True,
                value=DEFAULT_CUSTOMER_DESCRIPTION
            )
            self.task_description_new = gr.Textbox(
                label="Task Description", lines=3, interactive=True,
                value=DEFAULT_TASK_DESCRIPTION
            )
            self.template_description_new = gr.Textbox(
                label="Template Description", lines=3, interactive=True,
                value=DEFAULT_TEMPLATE_DESCRIPTION
            )
            self.btn_new = gr.Button("Create Tender Type")

    def on_subscribe_public_events(self):
        self._app.subscribe_event(
            name="onSignIn",
            definition={
                "fn": self.list_tender_types,
                "inputs": [],
                "outputs": [self.state_tender_type_list, self.tender_type_list],
                "show_progress": "hidden",
            }
        )
        self._app.subscribe_event(
            name="onSignOut",
            definition={
                "fn": lambda: ("", "", None, None, -1),
                "outputs": [
                    self.name_new,
                    self.description_new,
                    self.attachment_description_new,
                    self.customer_description_new,
                    self.task_description_new,
                    self.template_description_new,
                    self.state_tender_type_list,
                    self.tender_type_list,
                    self.selected_tender_type_id,
                ],
            },
        )

    def on_register_events(self):
        self.btn_new.click(
            self.create_tender_type,
            inputs=[self.name_new, self.description_new, self.attachment_description_new, self.customer_description_new, self.task_description_new, self.template_description_new],
            outputs=[self.name_new, self.description_new, self.attachment_description_new, self.customer_description_new, self.task_description_new, self.template_description_new]
        ).then(
            self.list_tender_types,
            outputs=[self.state_tender_type_list, self.tender_type_list],
        )

        self.tender_type_list.select(
            self.select_tender_type,
            inputs=self.tender_type_list,
            outputs=[self.selected_tender_type_id],
            show_progress="hidden",
        )

        self.selected_tender_type_id.change(
            self.on_selected_tender_type_change,
            inputs=[self.selected_tender_type_id],
            outputs=[
                self._selected_panel,
                self._selected_panel_btn,
                # delete section
                self.btn_delete,
                self.btn_delete_yes,
                self.btn_delete_no,
                # edit section
                self.name_edit,
                self.description_edit,
                self.attachment_description_edit,
                self.customer_description_edit,
                self.task_description_edit,
                self.template_description_edit,
            ],
            show_progress="hidden",
        )

        self.btn_delete.click(
            self.on_btn_delete_click,
            inputs=[self.selected_tender_type_id],
            outputs=[self.btn_delete, self.btn_delete_yes, self.btn_delete_no],
            show_progress="hidden",
        )

        self.btn_delete_yes.click(
            self.delete_tender_type,
            inputs=[self.selected_tender_type_id],
            outputs=[self.selected_tender_type_id],
            show_progress="hidden",
        ).then(
            self.list_tender_types,
            outputs=[self.state_tender_type_list, self.tender_type_list],
        )

        self.btn_delete_no.click(
            lambda: (
                gr.update(visible=True),
                gr.update(visible=False),
                gr.update(visible=False),
            ),
            inputs=[],
            outputs=[self.btn_delete, self.btn_delete_yes, self.btn_delete_no],
            show_progress="hidden",
        )

        self.btn_edit_save.click(
            self.save_tender_type,
            inputs=[
                self.selected_tender_type_id,
                self.name_edit,
                self.description_edit,
                self.attachment_description_edit,
                self.customer_description_edit,
                self.task_description_edit,
                self.template_description_edit,
            ],
            outputs=[self.name_edit, self.description_edit, self.attachment_description_edit, self.customer_description_edit, self.task_description_edit, self.template_description_edit],
            show_progress="hidden",
        ).then(
            self.list_tender_types,
            outputs=[self.state_tender_type_list, self.tender_type_list],
        )

        self.btn_close.click(
            lambda: -1,
            outputs=[self.selected_tender_type_id],
        )

    def list_tender_types(self):
        """ List the tender_types already existing in the database """
        with Session(engine) as session:
            statement = select(TenderType)
            results = [
                {"id": tender_type.id, "name": tender_type.name, "description": tender_type.description, "attachment description": tender_type.attachment_description, "customer description": tender_type.customer_description, "task description": tender_type.task_description, "template description": tender_type.template_description}
                for tender_type in session.exec(statement).all()
            ]
            if results:
                tender_type_list = pd.DataFrame.from_records(results)
            else:
                tender_type_list = pd.DataFrame.from_records(
                    [{"id": "-", "name": "-", "description": "-", "attachment description": "-", "customer description": "-", "task description": "-", "template description": "-"}]
                )

        return results, tender_type_list

    def create_tender_type(self, name, description, attachment_description, customer_description, task_description, template_description):
        """ Create a new tender_type """
        with Session(engine) as session:
            tender_type = TenderType(
                name=name,
                description=description,
                attachment_description=attachment_description,
                customer_description=customer_description,
                task_description=task_description,
                template_description=template_description
            )
            session.add(tender_type)
            session.commit()
            gr.Info(f"Tender type {name} created successfully.")

        return "", "", "", "", "", ""

    def select_tender_type(self, tender_type_list, ev: gr.SelectData):
        if ev.value == "-" and ev.index[0] == 0:
            gr.Info("No tender_type is loaded. Please refresh the tender_type list")
            return -1

        if not ev.selected:
            return -1

        return int(tender_type_list["id"][ev.index[0]])

    def on_selected_tender_type_change(self, selected_tender_type_id):
        if selected_tender_type_id == -1:
            _selected_panel = gr.update(visible=False)
            _selected_panel_btn = gr.update(visible=False)
            btn_delete = gr.update(visible=True)
            btn_delete_yes = gr.update(visible=False)
            btn_delete_no = gr.update(visible=False)
            name_edit = gr.update(value="")
            description_edit = gr.update(value="")
            attachment_description_edit = gr.update(value="")
            customer_description_edit = gr.update(value="")
            task_description_edit = gr.update(value="")
            template_description_edit = gr.update(value="")
        else:
            _selected_panel = gr.update(visible=True)
            _selected_panel_btn = gr.update(visible=True)
            btn_delete = gr.update(visible=True)
            btn_delete_yes = gr.update(visible=False)
            btn_delete_no = gr.update(visible=False)

            with Session(engine) as session:
                statement = select(TenderType).where(TenderType.id == int(selected_tender_type_id))
                tender_type = session.exec(statement).one()

            name_edit = gr.update(value=tender_type.name)
            description_edit = gr.update(value=tender_type.description)
            attachment_description_edit = gr.update(value=tender_type.attachment_description)
            customer_description_edit = gr.update(value=tender_type.customer_description)
            task_description_edit = gr.update(value=tender_type.task_description)
            template_description_edit = gr.update(value=tender_type.template_description)

        return (
            _selected_panel,
            _selected_panel_btn,
            btn_delete,
            btn_delete_yes,
            btn_delete_no,
            name_edit,
            description_edit,
            attachment_description_edit,
            customer_description_edit,
            task_description_edit,
            template_description_edit
        )

    def on_btn_delete_click(self, selected_tender_type_id):
        if selected_tender_type_id is None:
            gr.Warning("No tender type is selected")
            btn_delete = gr.update(visible=True)
            btn_delete_yes = gr.update(visible=False)
            btn_delete_no = gr.update(visible=False)
            return

        btn_delete = gr.update(visible=False)
        btn_delete_yes = gr.update(visible=True)
        btn_delete_no = gr.update(visible=True)

        return btn_delete, btn_delete_yes, btn_delete_no

    def save_tender_type(self, selected_tender_type_id, name, description, attachment_description, customer_description, task_description, template_description):
        with Session(engine) as session:
            statement = select(TenderType).where(TenderType.id == int(selected_tender_type_id))
            tender_type = session.exec(statement).one()
            tender_type.name = name
            tender_type.description = description
            tender_type.attachment_description = attachment_description
            tender_type.customer_description = customer_description
            tender_type.task_description = task_description
            tender_type.template_description = template_description
            session.commit()
            gr.Info(f'Tender type {tender_type.name} updated successfully')

        return "", ""

    def delete_tender_type(self, selected_tender_type_id):
        with Session(engine) as session:
            statement = select(TenderType).where(TenderType.id == int(selected_tender_type_id))
            tender_type = session.exec(statement).one()
            session.delete(tender_type)
            session.commit()
            gr.Info(f'Tender type {tender_type.name} deleted successfully')
        return -1

