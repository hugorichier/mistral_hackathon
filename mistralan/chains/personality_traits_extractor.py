from datetime import datetime
from typing import Optional, List, TypedDict
from langchain_core.prompts import ChatPromptTemplate
from langchain.chat_models.base import BaseChatModel
from langchain_core.runnables import Runnable

from pydantic import BaseModel, Field

class PersonalyTrait(BaseModel):

    name: Optional[str] = Field(default=None, description="Name of the personality trait")
    description: Optional[str] = Field(default=None, description="Description of the personality trait")

class PersonalyTraits(BaseModel):
    events: list[PersonalyTrait]

SYSTEM_PROMPT = """You are a assistant for a psychologist during a therapy session. 
                You need to deduct emotional states, physical symptoms and personality traits from what the patient says. 
                If you cannot deduct one of these from the prompt give None values"""

USER_PROMPT = """{content}"""

class Input(TypedDict):
    content: str

def get_personality_trait_extractor(llm: BaseChatModel) -> Runnable[Input, PersonalyTraits]:
    
    llm_ = llm.with_structured_output(PersonalyTraits)
    
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", SYSTEM_PROMPT),
            ("human", USER_PROMPT)
        ]
    )
    
    return prompt | llm_ # type: ignore