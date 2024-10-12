from datetime import datetime
from typing import Optional, List, TypedDict
from langchain_core.prompts import ChatPromptTemplate
from langchain.chat_models.base import BaseChatModel
from langchain_core.runnables import Runnable

from pydantic import BaseModel, Field
from ..schemas import emotional_state, personality_trait, symptom

class States(BaseModel):
    symptoms: list[symptom.Symptom]
    personality_traits: list[personality_trait.PersonalityTrait]
    emotional_states: list[emotional_state.EmotionalState]

SYSTEM_PROMPT = """You are a assistant for a psychologist during a therapy session. 
                You need to deduct states like emotion, physical symptoms and personality traits from what the patient says. 
                If you cannot deduct one of these from the prompt give None values"""

USER_PROMPT = """{content}"""

class Input(TypedDict):
    content: str

def get_states_extractor(llm: BaseChatModel) -> Runnable[Input, States]:
    
    llm_ = llm.with_structured_output(States)
    
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", SYSTEM_PROMPT),
            ("human", USER_PROMPT)
        ]
    )
    
    return prompt | llm_ # type: ignore