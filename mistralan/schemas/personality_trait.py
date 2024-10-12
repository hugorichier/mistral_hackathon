from pydantic import BaseModel, Field, computed_field
from typing import Optional


class PersonalityTrait(BaseModel):
    """Personality traits expressed in the patient response and actions."""

    name: str = Field(description="Name of the personality trait.")
    description: Optional[str] = Field(
        description="Definition of the personality trait."
    )

    @computed_field
    @property
    def cid(self) -> str:
        """Common identifier."""
        return self.name.lower().replace(" ", "_")
