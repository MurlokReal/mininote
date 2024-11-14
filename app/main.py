from datetime import timedelta

from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import models, schemas, crud, auth
from database import engine, Base, get_db
from config import ACCESS_TOKEN_EXPIRE_MINUTES
from jose import JWTError, jwt
from fastapi.middleware.cors import CORSMiddleware


Base.metadata.create_all(bind=engine)

app = FastAPI()

# Настройка CORS
origins = [
    "http://localhost",  # Разрешить доступ с localhost
    "http://127.0.0.1",  # Разрешить доступ с 127.0.0.1
    # Добавьте другие разрешенные источники по мере необходимости
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Разрешенные источники
    allow_credentials=True,
    allow_methods=["*"],  # Разрешить все методы
    allow_headers=["*"],  # Разрешить все заголовки
)


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, auth.SECRET_KEY, algorithms=[auth.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = crud.get_user_by_username(db, username=username)
    if user is None:
        raise credentials_exception
    return user


# CRUD для заметок
@app.post("/notes/", response_model=schemas.NoteOut)
def create_note(
    note: schemas.NoteCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    return crud.create_note(db=db, title=note.title, content=note.content, owner_id=current_user.id)

@app.get("/notes/", response_model=list[schemas.NoteOut])
def read_notes(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    return crud.get_notes_by_user(db, owner_id=current_user.id)

@app.get("/notes/{note_id}", response_model=schemas.NoteOut)
def read_note(note_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    note = db.query(models.Note).filter(models.Note.id == note_id, models.Note.owner_id == current_user.id).first()
    if note is None:
        raise HTTPException(status_code=404, detail="Note not found")
    return note

@app.put("/notes/{note_id}", response_model=schemas.NoteOut)
def update_note(
    note_id: int,
    updated_note: schemas.NoteCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    note = db.query(models.Note).filter(models.Note.id == note_id, models.Note.owner_id == current_user.id).first()
    if note is None:
        raise HTTPException(status_code=404, detail="Note not found")
    note.title = updated_note.title
    note.content = updated_note.content
    db.commit()
    db.refresh(note)
    return note

@app.delete("/notes/{note_id}", response_model=dict)
def delete_note(note_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    note = db.query(models.Note).filter(models.Note.id == note_id, models.Note.owner_id == current_user.id).first()
    if note is None:
        raise HTTPException(status_code=404, detail="Note not found")
    db.delete(note)
    db.commit()
    return {"detail": "Note deleted successfully"}


@app.post("/register/", response_model=schemas.UserCreate)
async def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_username(db, user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    return crud.create_user(db, user.username, user.password)


@app.post("/token", response_model=schemas.Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = crud.get_user_by_username(db, form_data.username)
    if not user or not crud.pwd_context.verify(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(data={"sub": user.username}, expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)