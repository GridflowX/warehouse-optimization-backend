from typing import Any, Dict
from pydantic import BaseModel

class Context(BaseModel):
    domain: str
    action: str
    bap_id: str
    bpp_id: str
    transaction_id: str
    message_id: str
    timestamp: str

class BecknRequest(BaseModel):
    context: Context
    message: Dict[str, Any]

class ContextOnlyRequest(BaseModel):
    context: Context