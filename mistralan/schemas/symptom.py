from pydantic import BaseModel, Field
from typing import Optional

class Symptom(BaseModel):

    name: Optional[str] = Field(default=None, description="Name of the symptom")
    description: Optional[str] = Field(default=None, description="description of the symptom")
    location: Optional[str] = Field(default=None, description="where the symptom is located on the human body")
