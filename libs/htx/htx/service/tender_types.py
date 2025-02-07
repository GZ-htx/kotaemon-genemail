from sqlmodel import Session, select
from ktem.db.models import TenderType, engine

### PROMPT DI DEFAULT ###
DEFAULT_ATTACHMENT_DESCRIPTION = "In allegato trovi uno o più file che descrivono un bando di finanziamento.\
 I documenti contengono informazioni dettagliate sulle finalità, i criteri di ammissibilità e le modalità \
 di partecipazione al bando. Ti chiedo di estrarre le informazioni più rilevanti per il cliente."

DEFAULT_CUSTOMER_DESCRIPTION = "Di seguito una descrizione del cliente.\n\
Nome cliente: {customer_name}\n\
Attività: {customer_description}"

DEFAULT_TASK_DESCRIPTION = "Puoi aiutarmi a scrivere un'email che informi il cliente \
riguardo a un bando che potrebbe essere di suo interesse? L'email deve essere chiara,\
 sintetica e professionale, includendo un riepilogo delle informazioni più rilevanti \
 e il motivo per cui il bando potrebbe essere vantaggioso per il cliente. "

DEFAULT_TEMPLATE_DESCRIPTION = "L'email deve contenere: \n\
- Un'introduzione che contestualizzi il motivo della comunicazione. \n\
- Un riepilogo del bando con gli elementi principali (titolo, ente promotore, finalità, importo disponibile, requisiti principali). \n\
- Le motivazioni della pertinenza del bando rispetto al cliente. \n\
- Le scadenze principali. \n\
- Un invito a contattarci per maggiori dettagli."


def get_tender_types_from_db():
    with Session(engine) as session:
        statement = select(TenderType)
        results = session.exec(statement).all()
    return results


def get_tender_type_by_id(id):
    with Session(engine) as session:
        statement = select(TenderType).where(TenderType.id == id)
        result = session.exec(statement).first()
    return result
