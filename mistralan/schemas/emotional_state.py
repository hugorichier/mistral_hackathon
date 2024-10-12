from pydantic import BaseModel, Field, computed_field
from typing import Optional


class EmotionalState(BaseModel):
    """Emotion felt by the patient."""

    name: str = Field(description="Name of the emotion.")
    description: str = Field(description="Definition of the emotion.")
    polarity: Optional[int] = Field(
        default=0,
        description="How positive or negative the emotion is on a scale of -10 to 10, -10 being very negative and 10 being very positive",
    )

    @computed_field
    @property
    def cid(self) -> str:
        """Common identifier."""
        return self.name.lower().replace(" ", "_")
