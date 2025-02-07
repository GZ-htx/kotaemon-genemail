from sqlmodel import Session, select
from ktem.db.models import Customer, engine

def get_customers_from_db():
    with Session(engine) as session:
        statement = select(Customer)
        results = session.exec(statement).all()
    return results


def get_customer_by_id(id):
    with Session(engine) as session:
        statement = select(Customer).where(Customer.id == id)
        result = session.exec(statement).first()
    return result
