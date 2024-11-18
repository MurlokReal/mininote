from fastapi import FastAPI

import uvicorn

from notes.views import router as notes_router

app = FastAPI()
app.include_router(notes_router, tags=["Notes"])


if __name__ == '__main__':
    uvicorn.run(app)
