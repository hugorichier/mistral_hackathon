from typing_extensions import TypedDict

from pydantic import BaseModel, TypeAdapter
from langchain.chat_models.base import BaseChatModel
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import Runnable, RunnablePassthrough

from ..schemas import Produce, Cause, Trigger, ConversationChunk
from .event_extractor import Events
from .states_extractor import States


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
Patient Name: {{ chunk.info.patient_name }}
Conversation Date: {{ chunk.info.date }}
----
{{ chunk.content }}
----

**Extracted Events**
{% for event in events.events %}
Common id: {{ event.cid }}
Description: {{ event.description }}
{%- endfor %}

**Extracted State**
Emotions:
{% for e in states.emotional_states %}
Common id: {{ e.cid }}
Description: {{ e.description }}
{%- endfor %}

Symptoms:
{% for s in states.symptoms %}
Common id: {{ s.cid }}
Description: {{ s.description }}
{%- endfor %}

Personality:
{% for t in states.personality_traits %}
Common id: {{ t.cid }}
Description: {{ t.description }}
{%- endfor %}
"""


class Input(TypedDict):
    chunk: ConversationChunk
    events: Events
    states: States


class Output(TypedDict):
    chunk: ConversationChunk
    events: Events
    states: States
    relations: Relations


AnalyserOutput = TypeAdapter(Output)


def get_linker(llm: BaseChatModel) -> Runnable[Input, Output]:
    llm_ = llm.with_structured_output(Relations)

    prompt = ChatPromptTemplate.from_messages(
        [("system", SYSTEM_PROMPT), ("human", USER_PROMPT)], template_format="jinja2"
    )

    chain = RunnablePassthrough.assign(relations=prompt | llm_)

    return chain  # type: ignore
