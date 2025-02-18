from sqlmodel import Field, SQLModel
from typing import Optional


# HTX - Struttura tabella Customer
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
# HTX - Fine struttura tabella Customer