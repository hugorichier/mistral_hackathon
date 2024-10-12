from typing import TypedDict

from pydantic import BaseModel, Field
from langchain.chat_models.base import BaseChatModel
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import Runnable

from operator import attrgetter

from ..schemas import Event, ConversationChunk

class Events(BaseModel):
    events: list[Event]

SYSTEM_PROMPT = """You are conversational analyst.

You are extracting events described in a conversation between a psychologist and a patient.

An event is a specific, discrete occurrence that happens at a particular point in time.
It's short-lived and can be easily identified with a start and an end. Examples include a meeting, a car accident, or a job interview.
Events are usually concrete, one-time actions or incidents.

**Task**
1. Read carefully the conversation
2. Identify specific events that the patient went threw
3. Extract each of these events, indentifying a start date and a potential end date for each
4. Review the list of events, ensure consistency and uniqueness, delete incomplete or irelevant events
"""

USER_PROMPT = """Patient Name: {patient_name}
Conversation Date: {date}

{content}
"""

EventExtractor = Runnable[ConversationChunk, Events]

def get_event_extractor(llm: BaseChatModel) -> EventExtractor:
    
    llm_ = llm.with_structured_output(Events)
    
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", SYSTEM_PROMPT),
            ("human", USER_PROMPT)
        ]
    )
    
    chain = {
        "date": lambda x: x.info.date,
        "content": attrgetter("content"),
        "patient_name": lambda x: x.info.patient_name
    } | prompt | llm_
    
    return chain # type: ignore
    