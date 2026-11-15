from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.api import api_router

app = FastAPI(
    title="EARTH-TO-SPACE Terrestrial Analog API",
    description="Lightweight point-query API scoring Earth locations against Moon & Mars target profiles.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)
