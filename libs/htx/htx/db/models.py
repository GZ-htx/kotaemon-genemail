from libs.htx.htx.db.base_models import BaseCustomer

_base_customer = (
    BaseCustomer
)


class Customer(_base_customer, table=True):  # type: ignore
    """Customer table"""
