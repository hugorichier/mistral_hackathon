from pydantic import BaseModel, Field
from typing import Optional

class PersonalityTrait(BaseModel):
    """Personality traits expressed in the patient response and actions."""
    name: Optional[str] = Field(description="Name of the personality trait")
    description: Optional[str] = Field(description="Description of the personality trait")