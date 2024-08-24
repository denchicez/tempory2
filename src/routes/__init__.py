from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from src.config import settings
from fastapi.middleware.gzip import GZipMiddleware
from .register_route import register_route
from .like_route import like_route

prefix = ""
app = FastAPI(
    openapi_prefix='',
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(GZipMiddleware)
app.include_router(register_route)
app.include_router(like_route)
