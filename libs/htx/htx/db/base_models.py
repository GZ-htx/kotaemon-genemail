from sqlmodel import Field, SQLModel
from typing import Optional


class BaseCustomer(SQLModel):
    """Store the customer information
    Attributes:
        id: id to identify the customer
        name: the name of the customer
        description: the description of what the customer does
    """
    __table_args__ = {"extend_existing": True}
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    description: str


class BaseTenderType(SQLModel):
    """Store the tender type information
    Attributes:
        id: id to identify the tender type
        name: the name of the tender type
        description: the description of what the tender type does
    """
    __table_args__ = {"extend_existing": True}
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    description: str
    attachment_description: str
    customer_description: str
    task_description: str
    template_description: str


class BaseSchedaPrompt(SQLModel):
    """Store the prompt information
    Attributes:
        id: id to identify the prompt
        name: the name of the prompt
        description: the description of what the prompt does
    """
    __table_args__ = {"extend_existing": True}
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    task: str