from sqlalchemy.orm import Session
from models.retail_sale_items import RetailSaleItem

class RetailSaleItemRepository:
    def get(self, db: Session, id: int):
        return db.query(RetailSaleItem).filter(RetailSaleItem.sale_item_id == id).first()

    def get_all(self, db: Session):
        return db.query(RetailSaleItem).all()

    def create(self, db: Session, data: dict):
        db_item = RetailSaleItem(**data)
        db.add(db_item)
        db.commit()
        db.refresh(db_item)
        return db_item

    def update(self, db: Session, db_obj: RetailSaleItem, data: dict):
        for key, value in data.items():
            setattr(db_obj, key, value)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def delete(self, db: Session, db_obj: RetailSaleItem):
        db.delete(db_obj)
        db.commit()
        return True

sale_item_repository = RetailSaleItemRepository()
