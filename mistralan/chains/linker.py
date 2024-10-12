from typing import TypedDict

from pydantic import BaseModel, Field
from langchain.chat_models.base import BaseChatModel
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import Runnable

from ..schemas import Event, Produce, Cause, Trigger

class Relations(BaseModel):
    produced_emotions: list[Produce]
    caused_symptoms: list[Cause]
    triggered_traits: list[Trigger]

SYSTEM_PROMPT = """You are an expert analyst in psychology.

We have extracted events and psychological states from a patient interview with a therapist.

You are asked to link events with corresponding states threw relations.

**Relations:**
- Event Produces Emotion: An event can produce an emotion on an individual.
    - Sign: '+' means that the event increased the feeling of an emotion, '-' means it deacreased it.
    - Level: how hard the emotion was decreased or increased.
- Event Causes Physical Symptoms: An event can cause physical symptoms as a result to an emotion.
- Event Triggers Personality Traits: An event can trigger the expression of a personality trait.
"""

USER_PROMPT = """Conversation:
Patient Name: {patient_name}
Conversation Date: {date}
----
{content}
----

Extracted Events:
{events}

Extracted State:
{states}
"""

class Input(TypedDict):
    date: str
    content: str
    patient_name: str

def get_linker(llm: BaseChatModel) -> Runnable[Input, Events]:
    
    llm_ = llm.with_structured_output(Events)
    
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", SYSTEM_PROMPT),
            ("human", USER_PROMPT)
        ]
    )
    
    return prompt | llm_ # type: ignore
    