from .event_extractor import EventExtractor, Events
from .states_extractor import StateExtractor, States
from typing import TypedDict
from ..schemas import ConversationChunk

from langchain_core.runnables import RunnableParallel, RunnablePassthrough
from operator import itemgetter

class Input(TypedDict):
    chunk: ConversationChunk

class Output(TypedDict):
    chunk: ConversationChunk
    events: Events
    states: States


def get_extractor(
    event_extractor: EventExtractor,
    state_extractor: StateExtractor
):
    chain = RunnablePassthrough.assign(
        **{
            "event": itemgetter("chunk") | event_extractor,
            "states": itemgetter("chunk") | state_extractor
        }
    )
    return chain
