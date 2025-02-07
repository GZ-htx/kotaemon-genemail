import ktem.db.base_models as base_models
from ktem.db.engine import engine
from sqlmodel import SQLModel
from theflow.settings import settings
from theflow.utils.modules import import_dotted_string

_base_conv = (
    import_dotted_string(settings.KH_TABLE_CONV, safe=False)
    if hasattr(settings, "KH_TABLE_CONV")
    else base_models.BaseConversation
)

_base_user = (
    import_dotted_string(settings.KH_TABLE_USER, safe=False)
    if hasattr(settings, "KH_TABLE_USER")
    else base_models.BaseUser
)

_base_settings = (
    import_dotted_string(settings.KH_TABLE_SETTINGS, safe=False)
    if hasattr(settings, "KH_TABLE_SETTINGS")
    else base_models.BaseSettings
)

_base_issue_report = (
    import_dotted_string(settings.KH_TABLE_ISSUE_REPORT, safe=False)
    if hasattr(settings, "KH_TABLE_ISSUE_REPORT")
    else base_models.BaseIssueReport
)

# HTX - Struttura nuove tabelle
_base_customer = (
    import_dotted_string(settings.KH_TABLE_CUSTOMER, safe=False)
    if hasattr(settings, "KH_TABLE_CUSTOMER")
    else base_models.BaseCustomer
)

_base_tender_type = (
    import_dotted_string(settings.KH_TABLE_TENDER_TYPE, safe=False)
    if hasattr(settings, "KH_TABLE_TENDER_TYPE")
    else base_models.BaseTenderType
)

_base_scheda_prompt = (
    import_dotted_string(settings.KH_TABLE_SCHEDA_PROMPT, safe=False)
    if hasattr(settings, "KH_TABLE_SCHEDA_PROMPT")
    else base_models.BaseSchedaPrompt
)
# HTX - Fine struttura nuove tabelle


class Conversation(_base_conv, table=True):  # type: ignore
    """Conversation record"""


class User(_base_user, table=True):  # type: ignore
    """User table"""


class Settings(_base_settings, table=True):  # type: ignore
    """Record of settings"""


class IssueReport(_base_issue_report, table=True):  # type: ignore
    """Record of issues"""


# HTX - Struttura tabella Customer
class Customer(_base_customer, table=True):  # type: ignore
    """Customer table"""
# HTX - Fine struttura tabella Customer


# HTX - Struttura tabella TenderType
class TenderType(_base_tender_type, table=True):  # type: ignore
    """TenderType table"""
# HTX - Fine struttura tabella TenderType


# HTX - Struttura tabella SchedaPrompt
class SchedaPrompt(_base_scheda_prompt, table=True):  # type: ignore
    """SchedaPrompt table"""
# HTX - Fine struttura tabella SchedaPrompt


if not getattr(settings, "KH_ENABLE_ALEMBIC", False):
    SQLModel.metadata.create_all(engine)
