from fastapi import FastAPI
from src.api.get_request import router as get_router

app = FastAPI()

app.include_router(get_router)
