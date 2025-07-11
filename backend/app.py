from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import json
from runner import run_algorithm

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

@app.post("/input")
def run(params: InputParams):
    try:
        output = run_algorithm(params.alpha, params.beta)
        
        return {"status": "success", "output": output}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
def root():
    return {"message": "PRT Algorithm API is running", "status": "healthy"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.get("/output")
def get_result():
    try:
        # First try to read json_output.json from backend directory
        with open("json_output.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        try:
            # Try parent directory
            with open("../json_output.json", "r") as f:
                return json.load(f)
        except FileNotFoundError:
            try:
                # Fallback to graph_output.json if json_output.json doesn't exist
                with open("../graph_output.json", "r") as f:
                    return json.load(f)
            except FileNotFoundError:
                raise HTTPException(status_code=404, detail="No result found")
