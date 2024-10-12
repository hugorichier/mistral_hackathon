from pydantic import BaseModel, Field, computed_field
from typing import Optional


class Symptom(BaseModel):
    """Physical symptoms experienced by the patient."""

    name: str = Field(description="Name of the symptom.")
    description: str = Field(description="Definition of the symptom.")
    location: Optional[str] = Field(
        default=None, description="where the symptom is located on the human body."
    )

    @computed_field
    @property
    def cid(self) -> str:
        """Common identifier."""
        return self.name.lower().replace(" ", "_")
