from sqlmodel import Session, select
from ktem.db.models import SchedaPrompt, engine

def get_prompts_from_db():
    with Session(engine) as session:
        statement = select(SchedaPrompt)
        results = session.exec(statement).all()
    return results


def get_prompt_by_id(id):
    with Session(engine) as session:
        statement = select(SchedaPrompt).where(SchedaPrompt.id == id)
        result = session.exec(statement).first()
    return result
