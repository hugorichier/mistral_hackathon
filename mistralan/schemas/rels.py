from pydantic import BaseModel, Field
from typing import Literal


class Produce(BaseModel):
    """An event that produce an emotion."""
    event_cid: str = Field(description="Source event common id.")
    emotion_cid: str = Field(description="Emotion common id.")
    sign: Literal["+", "-"] = Field(description="The event increased (+) or descreased (-) the feeling of an emotion.")
    intensity: Literal["low", "high", "medium"] = Field("medium", description="The intensity of the produced effect.")
    
class Cause(BaseModel):
    """An event that cause physical symptoms."""
    event_cid: str = Field(description="Source event common id.")
    symptom_cid: str = Field(description="Symptom common id.")

class Trigger(BaseModel):
    """An event that triggers a personnality trait."""
    event_cid: str = Field(description="Source event common id.")
    traits_cid: str = Field(description="Traits common id.")