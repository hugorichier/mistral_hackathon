from datetime import datetime
from typing import Optional, List, TypedDict
from langchain_core.prompts import ChatPromptTemplate
from langchain.chat_models.base import BaseChatModel
from langchain_core.runnables import Runnable, RunnableLambda
from operator import attrgetter
from pydantic import BaseModel, Field
from ..schemas import Symptom, PersonalityTrait, EmotionalState
import time

class States(BaseModel):
    symptoms: list[Symptom]
    personality_traits: list[PersonalityTrait]
    emotional_states: list[EmotionalState]

SYSTEM_PROMPT = """You are a assistant for a psychologist during a therapy session. 
You need to deduct states like emotion, physical symptoms and personality traits from what the patient says. 
If you cannot deduct one of these from the prompt give None values."""

USER_PROMPT = """{content}"""

class Input(TypedDict):
    content: str
    
StateExtractor = Runnable[Input, States]

def get_states_extractor(llm: BaseChatModel) -> StateExtractor:
    
    def _delay(x):
        time.sleep(5)
        return x

    llm_ = llm.with_structured_output(States)
    
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", SYSTEM_PROMPT),
            ("human", USER_PROMPT)
        ]
    )

    chain = {
        "content": attrgetter("content")
    } | RunnableLambda(_delay) | prompt | llm_
    
    return chain