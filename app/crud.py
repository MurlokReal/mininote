# app/crud.py
from sqlalchemy.orm import Session
from models import User as UserModel, Note as NoteModel
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password: str):
    return pwd_context.hash(password)


def create_user(db: Session, username: str, password: str):
    hashed_password = get_password_hash(password)
    db_user = UserModel(username=username, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_user_by_username(db: Session, username: str):
    return db.query(UserModel).filter(UserModel.username == username).first()


def create_note(db: Session, title: str, content: str, owner_id: int):
    note = NoteModel(title=title, content=content, owner_id=owner_id)
    db.add(note)
    db.commit()
    db.refresh(note)
    return note


def get_notes_by_user(db: Session, owner_id: int):
    return db.query(NoteModel).filter(NoteModel.owner_id == owner_id).all()
