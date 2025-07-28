from fastapi import FastAPI, HTTPException
from httpx import AsyncClient

app = FastAPI()

# Shared HTTP client for efficiency
client = AsyncClient(timeout=None)

@app.get("/")
def ping():
    return {"message": "Main Backend is running", "status": "healthy"}

# Guideway Optimization API endpoints
@app.get("/checkguideway")
async def check_guidewayoptimizationhealth():
    try:
        response = await client.get("http://guidewayoptimization:8000/")
        return response.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/input")
async def input_guidewayoptimizationendpoint(data: dict):
    try:
        response = await client.post("http://guidewayoptimization:8000/input", json=data)
        return response.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.get("/output")
async def output_guidewayoptimizationendpoint():
    try:
        response = await client.get("http://guidewayoptimization:8000/output")
        return response.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Package and Retrieval API endpoints
@app.get("/checkpackageretrieval")
async def check_packageretrievaloptimizationhealth():
    try:
        response = await client.get("http://packageandretrievaloptimization:8000/")
        return response.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/pack")
async def pack_packageretrievaloptimizationendpoint(data: dict):
    try:
        response = await client.post("http://packageandretrievaloptimization:8000/pack", json=data)
        return response.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
# Waiting Time Pallets API endpoints
@app.get("/checkwtpallets")
async def check_wtpalletsoptimizationhealth():
    try:
        response = await client.get("http://wtpalletsoptimization:8000/")
        return response.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.get("/optimize")
async def optimize_wtpalletsoptimizationendpoint():
    try:
        response = await client.get("http://wtpalletsoptimization:8000/optimize")
        return response.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))