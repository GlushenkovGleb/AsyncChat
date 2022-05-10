from fastapi import FastAPI

from .api import rest, socket

app = FastAPI()
app.include_router(rest.router)
app.include_router(socket.router)
