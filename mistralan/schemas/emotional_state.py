from pydantic import BaseModel, Field
from typing import Optional

class EmotionalState(BaseModel):

    name: Optional[str] = Field(default=None, description="Name of the emotion")
    description: Optional[str] = Field(default=None, description="description of the emotion")
    polarity: Optional[int] = Field(default=None, description="How positive or negative the emotion is on a scale of -10 to 10, -10 being very negative and 10 being very positive")