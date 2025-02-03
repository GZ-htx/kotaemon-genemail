import gradio as gr
import pandas as pd
from ktem.app import BasePage

from sqlmodel import Session, select
from ktem.db.models import Customer, engine


class CustomerManagement(BasePage):

    def __init__(self, app):
        self._app = app

        self.on_building_ui()

    def on_building_ui(self):
        with gr.Tab(label="Customer list"):
            self.state_customer_list = gr.State(value=None)
            self.customer_list = gr.DataFrame(
                headers=["id", "name", "description"],
                interactive=False,
            )

            with gr.Group(visible=False) as self._selected_panel:
                self.selected_customer_id = gr.Number(value=-1, visible=False)
                self.name_edit = gr.Textbox(label="Name")
                self.description_edit = gr.Textbox(label="Description", lines=3)

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

        with gr.Tab(label="Create customer"):
            self.name_new = gr.Textbox(label="Name", interactive=True)
            self.description_new = gr.Textbox(
                label="Description", lines=3, interactive=True
            )
            self.btn_new = gr.Button("Create customer")

    def on_subscribe_public_events(self):
        self._app.subscribe_event(
            name="onSignIn",
            definition={
                "fn": self.list_customers,
                "inputs": [],
                "outputs": [self.state_customer_list, self.customer_list],
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
                    self.state_customer_list,
                    self.customer_list,
                    self.selected_customer_id,
                ],
            },
        )

    def on_register_events(self):
        self.btn_new.click(
            self.create_customer,
            inputs=[self.name_new, self.description_new],
            outputs=[self.name_new, self.description_new]
        ).then(
            self.list_customers,
            outputs=[self.state_customer_list, self.customer_list],
        )

        self.customer_list.select(
            self.select_customer,
            inputs=self.customer_list,
            outputs=[self.selected_customer_id],
            show_progress="hidden",
        )

        self.selected_customer_id.change(
            self.on_selected_customer_change,
            inputs=[self.selected_customer_id],
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
            ],
            show_progress="hidden",
        )

        self.btn_delete.click(
            self.on_btn_delete_click,
            inputs=[self.selected_customer_id],
            outputs=[self.btn_delete, self.btn_delete_yes, self.btn_delete_no],
            show_progress="hidden",
        )

        self.btn_delete_yes.click(
            self.delete_customer,
            inputs=[self.selected_customer_id],
            outputs=[self.selected_customer_id],
            show_progress="hidden",
        ).then(
            self.list_customers,
            outputs=[self.state_customer_list, self.customer_list],
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
            self.save_customer,
            inputs=[
                self.selected_customer_id,
                self.name_edit,
                self.description_edit,
            ],
            outputs=[self.name_edit, self.description_edit],
            show_progress="hidden",
        ).then(
            self.list_customers,
            outputs=[self.state_customer_list, self.customer_list],
        )

        self.btn_close.click(
            lambda: -1,
            outputs=[self.selected_customer_id],
        )

    def list_customers(self):
        """ List the customers already existing in the database """
        with Session(engine) as session:
            statement = select(Customer)
            results = [
                {"id": customer.id, "name": customer.name, "description": customer.description}
                for customer in session.exec(statement).all()
            ]
            if results:
                customer_list = pd.DataFrame.from_records(results)
            else:
                customer_list = pd.DataFrame.from_records(
                    [{"id": "-", "name": "-", "description": "-"}]
                )

        return results, customer_list

    def create_customer(self, name, description):
        """ Create a new customer """
        with Session(engine) as session:
            customer = Customer(
                name=name,
                description=description
            )
            session.add(customer)
            session.commit()
            gr.Info(f"Customer {name} created successfully.")

        return "", ""

    def select_customer(self, customer_list, ev: gr.SelectData):
        if ev.value == "-" and ev.index[0] == 0:
            gr.Info("No customer is loaded. Please refresh the customer list")
            return -1

        if not ev.selected:
            return -1

        return int(customer_list["id"][ev.index[0]])

    def on_selected_customer_change(self, selected_customer_id):
        if selected_customer_id == -1:
            _selected_panel = gr.update(visible=False)
            _selected_panel_btn = gr.update(visible=False)
            btn_delete = gr.update(visible=True)
            btn_delete_yes = gr.update(visible=False)
            btn_delete_no = gr.update(visible=False)
            name_edit = gr.update(value="")
            description_edit = gr.update(value="")
        else:
            _selected_panel = gr.update(visible=True)
            _selected_panel_btn = gr.update(visible=True)
            btn_delete = gr.update(visible=True)
            btn_delete_yes = gr.update(visible=False)
            btn_delete_no = gr.update(visible=False)

            with Session(engine) as session:
                statement = select(Customer).where(Customer.id == int(selected_customer_id))
                customer = session.exec(statement).one()

            name_edit = gr.update(value=customer.name)
            description_edit = gr.update(value=customer.description)

        return (
            _selected_panel,
            _selected_panel_btn,
            btn_delete,
            btn_delete_yes,
            btn_delete_no,
            name_edit,
            description_edit,
        )

    def on_btn_delete_click(self, selected_user_id):
        if selected_user_id is None:
            gr.Warning("No user is selected")
            btn_delete = gr.update(visible=True)
            btn_delete_yes = gr.update(visible=False)
            btn_delete_no = gr.update(visible=False)
            return

        btn_delete = gr.update(visible=False)
        btn_delete_yes = gr.update(visible=True)
        btn_delete_no = gr.update(visible=True)

        return btn_delete, btn_delete_yes, btn_delete_no

    def save_customer(self, selected_customer_id, name, description):
        with Session(engine) as session:
            statement = select(Customer).where(Customer.id == int(selected_customer_id))
            customer = session.exec(statement).one()
            customer.name = name
            customer.description = description
            session.commit()
            gr.Info(f'Customer {customer.name} updated successfully')

        return "", ""

    def delete_customer(self, selected_customer_id):
        with Session(engine) as session:
            statement = select(Customer).where(Customer.id == int(selected_customer_id))
            customer = session.exec(statement).one()
            session.delete(customer)
            session.commit()
            gr.Info(f'Customer {customer.name} deleted successfully')
        return -1
