from langchain_mistralai.chat_models import ChatMistralAI


from .event_extractor import get_event_extractor
from .states_extractor import get_states_extractor
from .extractor import get_extractor
from .linker import get_linker


def get_mistral() -> ChatMistralAI:
    return ChatMistralAI(model="mistral-large-latest", temperature=0.2) # type: ignore