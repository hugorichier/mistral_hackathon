from datetime import datetime
from typing import Optional, List, TypedDict
from langchain_core.prompts import ChatPromptTemplate
from langchain.chat_models.base import BaseChatModel
from langchain_core.runnables import Runnable

from pydantic import BaseModel, Field

class Symptom(BaseModel):

    name: Optional[str] = Field(description="Name of the symptom")
    description: Optional[str] = Field(description="description of the symptom")
    location: Optional[str] = Field(description="where the symptom is located on the human body")

class Symptoms(BaseModel):
    events: list[Symptom]

SYSTEM_PROMPT = """You are a assistant for a psychologist during a therapy session. 
                You need to deduct emotional states, physical symptoms and personality traits from what the patient says. 
                If you cannot deduct one of these from the prompt give None values"""

USER_PROMPT = """{content}"""

class Input(TypedDict):
    content: str

def get_symptom_extractor(llm: BaseChatModel) -> Runnable[Input, Symptoms]:
    
    llm_ = llm.with_structured_output(Symptoms)
    
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", SYSTEM_PROMPT),
            ("human", USER_PROMPT)
        ]
    )
    
    return prompt | llm_ # type: ignore