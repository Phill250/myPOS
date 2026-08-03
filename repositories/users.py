from sqlalchemy.orm import Session
from models.users import User

class UserRepository:
    def get_by_id(self, db: Session, id: int):
        return db.query(User).filter(User.user_id == id).first()

    def get_by_username(self, db: Session, username: str):
        return db.query(User).filter(User.username == username).first()

    def get_all(self, db: Session):
        return db.query(User).all()

    def create(self, db: Session, data: dict):
        db_user = User(**data)
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user

    def update(self, db: Session, db_obj: User, data: dict):
        for key, value in data.items():
            setattr(db_obj, key, value)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def delete(self, db: Session, db_obj: User):
        db.delete(db_obj)
        db.commit()
        return True

user_repository = UserRepository()
