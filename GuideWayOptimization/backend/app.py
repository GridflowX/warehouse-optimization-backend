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

class InputParams(BaseModel):
    alpha: float
    beta: float

@app.get("/")
def root():
    return {"message": "PRT Algorithm API is running", "status": "healthy"}

@app.post("/input")
def run(params: InputParams):
    try:
        output = run_algorithm(params.alpha, params.beta)
        
        return {"status": "success", "output": output}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/output")
def get_result():
    try:
        json_output_path = os.path.join(os.path.dirname(__file__), "json_output.json")
        if os.path.exists(json_output_path):
            with open(json_output_path, "r") as f:
                return json.load(f)
    except FileNotFoundError:
        try:
            # Try parent directory
            with open("../json_output.json", "r") as f:
                return json.load(f)
        except FileNotFoundError:
            try:
                # Fallback to graph_output.json if json_output.json doesn't exist
                with open("../guidewayOptimizationAlgorithm/graph_output.json", "r") as f:
                    return json.load(f)
            except FileNotFoundError:
                raise HTTPException(status_code=404, detail="No result found")
