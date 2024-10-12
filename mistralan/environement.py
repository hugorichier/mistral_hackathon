import os




GCLOUD_PROJECT_ID = os.getenv("GCLOUD_PROJECT_ID", "mistral-alan-hack24par-812")
CHUNK_TOPIC = os.getenv("CHUNK_TOPIC", "conversation-chunk")
CHUNK_ANALYSER_SUB = os.getenv("EVENT_EXTRACTOR", "chunk-analyser")
NEO4J_HOST = os.getenv("NEO4J_HOST", "neo4j://34.79.251.17:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "123456789")