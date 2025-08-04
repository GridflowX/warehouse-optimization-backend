from fastapi import APIRouter, HTTPException
from httpx import AsyncClient

router = APIRouter()
client = AsyncClient(timeout=None)

@router.get("/")
def ping():
    return {"message": "Main Backend is running", "status": "healthy"}

@router.get("/checkguideway")
async def check_guidewayoptimizationhealth():
    try:
        response = await client.get("http://guidewayoptimization:8000/")
        return response.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/output")
async def output_guidewayoptimizationendpoint():
    try:
        response = await client.get("http://guidewayoptimization:8000/output")
        return response.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/checkpackageretrieval")
async def check_packageretrievaloptimizationhealth():
    try:
        response = await client.get("http://packageandretrievaloptimization:8000/")
        return response.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/checkwtpallets")
async def check_wtpalletsoptimizationhealth():
    try:
        response = await client.get("http://wtpalletsoptimization:8000/")
        return response.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))