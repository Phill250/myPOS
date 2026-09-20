from sqlalchemy.orm import Session
from models.retail_sales import RetailSale

class RetailSaleRepository:
    def get(self, db: Session, id: int):
        return db.query(RetailSale).filter(RetailSale.sale_id == id).first()

    def get_all(self, db: Session):
        return db.query(RetailSale).all()

    def get_all_for_customer(self, db: Session, customer_id: int):
        return db.query(RetailSale).filter(RetailSale.customer_id == customer_id).all()

    def create(self, db: Session, data: dict):
        db_sale = RetailSale(**data)
        db.add(db_sale)
        db.commit()
        db.refresh(db_sale)
        return db_sale

    def update(self, db: Session, db_obj: RetailSale, data: dict):
        for key, value in data.items():
            setattr(db_obj, key, value)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def delete(self, db: Session, db_obj: RetailSale):
        db.delete(db_obj)
        db.commit()
        return True


retail_sale_repository = RetailSaleRepository()