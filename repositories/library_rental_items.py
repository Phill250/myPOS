from sqlalchemy.orm import Session
from models.library_rental_items import LibraryRentalItem

class LibraryRentalItemRepository:
    def get(self, db: Session, id: int):
        return db.query(LibraryRentalItem).filter(LibraryRentalItem.rental_item_id == id).first()

    def get_all(self, db: Session):
        return db.query(LibraryRentalItem).all()

    def create(self, db: Session, data: dict):
        db_item = LibraryRentalItem(**data)
        db.add(db_item)
        db.commit()
        db.refresh(db_item)
        return db_item

    def update(self, db: Session, db_obj: LibraryRentalItem, data: dict):
        for key, value in data.items():
            setattr(db_obj, key, value)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def delete(self, db: Session, db_obj: LibraryRentalItem):
        db.delete(db_obj)
        db.commit()
        return True

library_rental_item_repository = LibraryRentalItemRepository()
