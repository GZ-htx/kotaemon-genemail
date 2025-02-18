from libs.htx.htx.db.base_models import BaseCustomer, BaseTenderType, BaseSchedaPrompt

_base_customer = (
    BaseCustomer
)

_base_tender_type = (
    BaseTenderType
)
_base_scheda_prompt = (
    BaseSchedaPrompt
)


class Customer(_base_customer, table=True):  # type: ignore
    """Customer table"""


class TenderType(_base_tender_type, table=True):  # type: ignore
    """TenderType table"""


class SchedaPrompt(_base_scheda_prompt, table=True):  # type: ignore
    """SchedaPrompt table"""
