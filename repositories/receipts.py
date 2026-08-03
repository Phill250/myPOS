from sqlalchemy.orm import Session
from models.receipts import Receipt

class ReceiptRepository:
    def get(self, db: Session, id: int):
        return db.query(Receipt).filter(Receipt.receipt_id == id).first()

    def get_all(self, db: Session):
        return db.query(Receipt).all()

    def create(self, db: Session, data: dict):
        db_receipt = Receipt(**data)
        db.add(db_receipt)
        db.commit()
        db.refresh(db_receipt)
        return db_receipt

    def update(self, db: Session, db_obj: Receipt, data: dict):
        for key, value in data.items():
            setattr(db_obj, key, value)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def delete(self, db: Session, db_obj: Receipt):
        db.delete(db_obj)
        db.commit()
        return True

receipt_repository = ReceiptRepository()
