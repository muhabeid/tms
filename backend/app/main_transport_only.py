"""
Minimal reproduction case - just Transport module
This will help isolate if the issue is with Transport specifically or interaction with other modules
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import app.models  # Ensure all models are registered
from app.api.v1 import transport

app = FastAPI(title="TMS Transport Test")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Only include Transport router
app.include_router(transport.router, prefix="/api/v1/transport", tags=["transport"])

@app.get("/ping")
async def ping():
    return {"ping": "pong", "module": "transport-only"}

@app.get("/")
async def root():
    return {"message": "Transport module test server", "status": "running"}
