from pydantic import BaseModel, Field

from datetime import date


class ConversationInfo(BaseModel):
    id: str
    patient_name: str
    patient_id: str
    date: date
    
class ConversationChunk(BaseModel):
    info: ConversationInfo
    content: str
    ts: int