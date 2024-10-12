import os




GCLOUD_PROJECT_ID = os.getenv("GCLOUD_PROJECT_ID", "mistral-alan-hack24par-812")
CHUNK_TOPIC = os.getenv("CHUNK_TOPIC", "conversation-chunk")
EVENT_EXTRACTOR = os.getenv("EVENT_EXTRACTOR", "event-extractor")