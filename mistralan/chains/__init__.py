from langchain_mistralai.chat_models import ChatMistralAI


from .event_extractor import get_event_extractor



def get_mistral() -> ChatMistralAI:
    return ChatMistralAI(model="mistral-large-latest", temperature=0.2) # type: ignore