from pydantic import BaseModel


class UserCreate(BaseModel):
    username: str
    password: str


class UserInDB(UserCreate):
    hashed_password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class NoteCreate(BaseModel):
    title: str
    content: str


class NoteOut(BaseModel):
    id: int
    title: str
    content: str
    owner_id: int

    class Config:
        from_attributes = True
