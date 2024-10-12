from pydantic import BaseModel, Field
from typing import Optional

class PersonalityTrait(BaseModel):

    name: Optional[str] = Field(default=None, description="Name of the personality trait")
    description: Optional[str] = Field(default=None, description="Description of the personality trait")