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

    def describe(self) -> str:
        return (
            f"Symptoms: {len(self.symptoms)}\n"
            f"Personality Traits: {len(self.personality_traits)}\n"
            f"Emotion: {len(self.emotional_states)}"
        )


SYSTEM_PROMPT = """You are a assistant for a psychologist during a therapy session.

You need to deduct states like emotion, physical symptoms and personality traits from what the patient says.

**Task**
1. Read carefully the full conversation
2. Identify emotions, personnality traits and symptoms expressed by the patient
3. Infer emotions and personnality traits from the patient answers
4. Review extracted emotions, personnality traits and symptoms; ensure uniqueness and completness of information accross the conversation"""

USER_PROMPT = """Conversation:
{content}"""


class Input(TypedDict):
    content: str


StateExtractor = Runnable[Input, States]


def get_states_extractor(llm: BaseChatModel) -> StateExtractor:
    def _delay(x):
        time.sleep(5)
        return x

    llm_ = llm.with_structured_output(States)

    prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT),
        ("human", USER_PROMPT),
    ])

    chain = {"content": attrgetter("content")} | RunnableLambda(_delay) | prompt | llm_

    return chain  # type: ignore
