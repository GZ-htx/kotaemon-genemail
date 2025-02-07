import gradio as gr
import pandas as pd
from ktem.app import BasePage

from sqlmodel import Session, select
from ktem.db.models import SchedaPrompt, engine


class SchedaPromptManagement(BasePage):

    def __init__(self, app):
        self._app = app

        self.on_building_ui()

    def on_building_ui(self):
        with gr.Tab(label="Prompts list"):
            self.state_prompt_list = gr.State(value=None)
            self.prompt_list = gr.DataFrame(
                headers=["id", "name", "task"],
                interactive=False,
            )
            
            with gr.Group(visible=False) as self._selected_panel:
                self.selected_prompt_id = gr.Number(value=-1, visible=False)
                self.name_edit = gr.Textbox(label="Name")
                self.task_edit = gr.Textbox(label="Task", lines=3)

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
                    
        with gr.Tab(label="Create prompt"):
            self.name_new = gr.Textbox(label="Name", interactive=True)
            self.task_new = gr.Textbox(
                label="Task", lines=3, interactive=True
            )
            self.btn_new = gr.Button("Create prompt")
            
    def on_subscribe_public_events(self):
        self._app.subscribe_event(
            name="onSignIn",
            definition={
                "fn": self.list_prompts,
                "inputs": [],
                "outputs": [self.state_prompt_list, self.prompt_list],
                "show_progress": "hidden",
            }
        )
        self._app.subscribe_event(
            name="onSignOut",
            definition={
                "fn": lambda: ("", "", None, None, -1),
                "outputs": [
                    self.name_new,
                    self.task_new,
                    self.state_prompt_list,
                    self.prompt_list,
                    self.selected_prompt_id,
                ],
            },
        )

    def on_register_events(self):
        self.btn_new.click(
            self.create_prompt,
            inputs=[self.name_new, self.task_new],
            outputs=[self.name_new, self.task_new]
        ).then(
            self.list_prompts,
            outputs=[self.state_prompt_list, self.prompt_list],
        )

        self.prompt_list.select(
            self.select_prompt,
            inputs=self.prompt_list,
            outputs=[self.selected_prompt_id],
            show_progress="hidden",
        )

        self.selected_prompt_id.change(
            self.on_selected_prompt_change,
            inputs=[self.selected_prompt_id],
            outputs=[
                self._selected_panel,
                self._selected_panel_btn,
                # delete section
                self.btn_delete,
                self.btn_delete_yes,
                self.btn_delete_no,
                # edit section
                self.name_edit,
                self.task_edit,
            ],
            show_progress="hidden",
        )

        self.btn_delete.click(
            self.on_btn_delete_click,
            inputs=[self.selected_prompt_id],
            outputs=[self.btn_delete, self.btn_delete_yes, self.btn_delete_no],
            show_progress="hidden",
        )

        self.btn_delete_yes.click(
            self.delete_prompt,
            inputs=[self.selected_prompt_id],
            outputs=[self.selected_prompt_id],
            show_progress="hidden",
        ).then(
            self.list_prompts,
            outputs=[self.state_prompt_list, self.prompt_list],
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
            self.save_prompt,
            inputs=[
                self.selected_prompt_id,
                self.name_edit,
                self.task_edit,
            ],
            outputs=[self.name_edit, self.task_edit],
            show_progress="hidden",
        ).then(
            self.list_prompts,
            outputs=[self.state_prompt_list, self.prompt_list],
        )

        self.btn_close.click(
            lambda: -1,
            outputs=[self.selected_prompt_id],
        )

    def list_prompts(self):
        """ List the prompts already existing in the database """
        with Session(engine) as session:
            statement = select(SchedaPrompt)
            results = [
                {"id": prompt.id, "name": prompt.name, "task": prompt.task}
                for prompt in session.exec(statement).all()
            ]
            if results:
                prompt_list = pd.DataFrame.from_records(results)
            else:
                prompt_list = pd.DataFrame.from_records(
                    [{"id": "-", "name": "-", "task": "-"}]
                )

        return results, prompt_list

    def create_prompt(self, name, task):
        """ Create a new prompt """
        with Session(engine) as session:
            prompt = SchedaPrompt(
                name=name,
                task=task
            )
            session.add(prompt)
            session.commit()
            gr.Info(f"Prompt {name} created successfully.")

        return "", ""

    def select_prompt(self, prompt_list, ev: gr.SelectData):
        if ev.value == "-" and ev.index[0] == 0:
            gr.Info("No prompt is loaded. Please refresh the prompt list")
            return -1

        if not ev.selected:
            return -1

        return int(prompt_list["id"][ev.index[0]])

    def on_selected_prompt_change(self, selected_prompt_id):
        if selected_prompt_id == -1:
            _selected_panel = gr.update(visible=False)
            _selected_panel_btn = gr.update(visible=False)
            btn_delete = gr.update(visible=True)
            btn_delete_yes = gr.update(visible=False)
            btn_delete_no = gr.update(visible=False)
            name_edit = gr.update(value="")
            task_edit = gr.update(value="")
        else:
            _selected_panel = gr.update(visible=True)
            _selected_panel_btn = gr.update(visible=True)
            btn_delete = gr.update(visible=True)
            btn_delete_yes = gr.update(visible=False)
            btn_delete_no = gr.update(visible=False)

            with Session(engine) as session:
                statement = select(SchedaPrompt).where(SchedaPrompt.id == int(selected_prompt_id))
                prompt = session.exec(statement).one()

            name_edit = gr.update(value=prompt.name)
            task_edit = gr.update(value=prompt.task)

        return (
            _selected_panel,
            _selected_panel_btn,
            btn_delete,
            btn_delete_yes,
            btn_delete_no,
            name_edit,
            task_edit,
        )

    def on_btn_delete_click(self, selected_user_id):
        if selected_user_id is None:
            gr.Warning("No prompt is selected")
            btn_delete = gr.update(visible=True)
            btn_delete_yes = gr.update(visible=False)
            btn_delete_no = gr.update(visible=False)
            return

        btn_delete = gr.update(visible=False)
        btn_delete_yes = gr.update(visible=True)
        btn_delete_no = gr.update(visible=True)

        return btn_delete, btn_delete_yes, btn_delete_no

    def save_prompt(self, selected_prompt_id, name, task):
        with Session(engine) as session:
            statement = select(SchedaPrompt).where(SchedaPrompt.id == int(selected_prompt_id))
            prompt = session.exec(statement).one()
            prompt.name = name
            prompt.task = task
            session.commit()
            gr.Info(f'Prompt {prompt.name} updated successfully')

        return "", ""

    def delete_prompt(self, selected_prompt_id):
        with Session(engine) as session:
            statement = select(SchedaPrompt).where(SchedaPrompt.id == int(selected_prompt_id))
            prompt = session.exec(statement).one()
            session.delete(prompt)
            session.commit()
            gr.Info(f'Prompt {prompt.name} deleted successfully')
        return -1