from pydantic import BaseModel, Field


class Event(BaseModel):
    """An event that occured."""
    name: str = Field(description="Short name of the event.")
    start_date: str = Field(None, description="Reference start day of occuring event.")
    end_date: str | None = Field(None, description="Reference end day of occuring event.")
    description: str = Field("Short description of the event.")
    participants: list[str] = Field(description="List of participants in the event, can be individuals or groups of people.")