from fastapi import APIRouter, HTTPException
from models import BecknRequest
from httpx import AsyncClient
from models import ContextOnlyRequest

router = APIRouter()
client = AsyncClient(timeout=None)

def format_beckn_response(context: dict, data: dict, action_suffix: str):
    context["action"] = f"on_{action_suffix}"
    return {
        "context": context,
        "message": data
    }

@router.post("/search")
async def beckn_search(req: BecknRequest):
    try:
        res = await client.post("http://guidewayoptimization:8000/input", json=req.message)
        return format_beckn_response(req.context.dict(), res.json(), "search")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/select")
async def beckn_select(req: BecknRequest):
    try:
        res = await client.post("http://packageandretrievaloptimization:8000/pack", json=req.message)
        return format_beckn_response(req.context.dict(), res.json(), "select")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/confirm")
async def beckn_confirm(req: ContextOnlyRequest):
    try:
        res = await client.get("http://wtpalletsoptimization:8000/optimize")
        return format_beckn_response(req.context.dict(), res.json(), "confirm")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))