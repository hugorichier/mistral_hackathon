from pydantic import BaseModel, Field
from typing import Optional

class Symptom(BaseModel):
    """Physical symptoms experienced by the patient."""
    name: str = Field(description="Name of the symptom.")
    description: str = Field(description="description of the symptom.")
    location: Optional[str] = Field(default=None, description="where the symptom is located on the human body.")
