from typing import Annotated
from annotated_types import MinLen, MaxLen
from pydantic import BaseModel


class CreateNote(BaseModel):
    title: Annotated[str, MaxLen(100), MinLen(3)]
    text: str
