from datetime import datetime
from typing import Optional, List, TypedDict
from langchain_core.prompts import ChatPromptTemplate
from langchain.chat_models.base import BaseChatModel
from langchain_core.runnables import Runnable

from pydantic import BaseModel, Field

class EmotionalState(BaseModel):

    name: Optional[str] = Field(description="Name of the emotion")
    description: Optional[str] = Field(description="description of the emotion")
    polarity: Optional[int] = Field(description="How positive or negative the emotion is on a scale of -10 to 10, -10 being very negative and 10 being very positive")

class EmotionalStates(BaseModel):
    events: list[EmotionalState]

SYSTEM_PROMPT = """You are a assistant for a psychologist during a therapy session. 
                You need to deduct emotional states, physical symptoms and personality traits from what the patient says. 
                If you cannot deduct one of these from the prompt give None values"""

USER_PROMPT = """{content}"""

class Input(TypedDict):
    content: str

def get_emotional_state_extractor(llm: BaseChatModel) -> Runnable[Input, EmotionalState]:
    
    llm_ = llm.with_structured_output(EmotionalState)
    
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", SYSTEM_PROMPT),
            ("human", USER_PROMPT)
        ]
    )
    
    return prompt | llm_ # type: ignore