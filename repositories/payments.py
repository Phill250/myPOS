from sqlalchemy.orm import Session
from models.payments import Payment

class PaymentRepository:
    def get(self, db: Session, id: int):
        return db.query(Payment).filter(Payment.payment_id == id).first()

    def get_all(self, db: Session):
        return db.query(Payment).all()

    def create(self, db: Session, data: dict):
        db_payment = Payment(**data)
        db.add(db_payment)
        db.commit()
        db.refresh(db_payment)
        return db_payment

    def update(self, db: Session, db_obj: Payment, data: dict):
        for key, value in data.items():
            setattr(db_obj, key, value)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def delete(self, db: Session, db_obj: Payment):
        db.delete(db_obj)
        db.commit()
        return True

payment_repository = PaymentRepository()
