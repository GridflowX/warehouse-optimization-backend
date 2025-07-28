from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import json
from backend.runner import run_algorithm
import os

app = FastAPI()

# Add CORS middleware to allow all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

@app.get("/")
def root():
    return {"message": "Wt-Pallete Algorithm API is running", "status": "healthy"}


@app.get("/optimize")
def run():
    try:
        return run_algorithm()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))