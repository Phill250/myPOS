from sqlalchemy.orm import Session
from models.library_rentals import LibraryRental

class LibraryRentalRepository:
    def get(self, db: Session, id: int):
        return db.query(LibraryRental).filter(LibraryRental.rental_id == id).first()

    def get_all(self, db: Session):
        return db.query(LibraryRental).all()

    def create(self, db: Session, data: dict):
        db_rental = LibraryRental(**data)
        db.add(db_rental)
        db.commit()
        db.refresh(db_rental)
        return db_rental

    def update(self, db: Session, db_obj: LibraryRental, data: dict):
        for key, value in data.items():
            setattr(db_obj, key, value)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def delete(self, db: Session, db_obj: LibraryRental):
        db.delete(db_obj)
        db.commit()
        return True

library_rental_repository = LibraryRentalRepository()
