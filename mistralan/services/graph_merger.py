from neo4j import GraphDatabase
import orjson
import sys
import time
import logging
from langchain_huggingface.embeddings import HuggingFaceEndpointEmbeddings


from ..environement import (
    NEO4J_HOST,
    NEO4J_PASSWORD,
    NEO4J_USER,
    GCLOUD_PROJECT_ID,
    GRAPH_MERGE_SUB,
)
from google.cloud import pubsub_v1
from ..chains import (
    AnalyserOutput,
)
from ..schemas import Event

logging.basicConfig(stream=sys.stdout)
logger = logging.getLogger("analyser")
logger.setLevel(logging.INFO)

subscriber = pubsub_v1.SubscriberClient()
subscription_path = subscriber.subscription_path(GCLOUD_PROJECT_ID, GRAPH_MERGE_SUB)

EVENT_CREATE = """MERGE (e:Event {
    cid: $event.cid,
    name: $event.name,
    start_date: $event.start_date,
    end_date: $event.end_date
})
ON CREATE SET
    e.desc = $event.description,
    e.participants = $event.participants,
    e.source_id = $source_id,
    e.embedding = $event.embedding
"""

PRODUCE_MERGER = """MERGE (t:Emotion {cid: $target.cid})
ON CREATE SET t += $target
WITH t
MATCH (e:Event {cid: $event.cid, start_date: $event.start_date, end_date: $event.end_date})
WITH e, t
CREATE (e)-[r:PRODUCE]->(t)
SET r += $rel
"""

CAUSE_MERGE = """MERGE (t:Symptom {cid: $target.cid})
ON CREATE SET t += $target
WITH t
MATCH (e:Event {cid: $event.cid, start_date: $event.start_date, end_date: $event.end_date})
WITH e, t
CREATE (e)-[r:CAUSE]->(t)
SET r += $rel
"""

TRIGGER_MERGE = """MERGE (t:PersonalityTrait {cid: $target.cid})
ON CREATE SET t += $target
WITH t
MATCH (e:Event {cid: $event.cid, start_date: $event.start_date, end_date: $event.end_date})
WITH e, t
CREATE (e)-[r:TRIGGER]->(t)
SET r += $rel
"""

GET_DATA = """MATCH (current:Event)-[]->(n)<-[]-(other:Event)
WHERE current.cid in $ids AND not n:Event return *
"""

time.sleep(10)  # stupid tei healthcheck not working
embeddings = HuggingFaceEndpointEmbeddings(model="http://tei:80")


def callback(message: pubsub_v1.subscriber.message.Message) -> None:  # type: ignore
    with GraphDatabase.driver(NEO4J_HOST, auth=(NEO4J_USER, NEO4J_PASSWORD)) as driver:
        driver.verify_connectivity()
        data = orjson.loads(message.data)
        analysis = AnalyserOutput.validate_python(data)
        logger.info("=" * 50)
        logger.info("Analysis received")
        source_id = analysis["chunk"].info.id + "." + str(analysis["chunk"].ts)
        event_map: dict[str, Event] = {}
        event_batch = [e.name + "\n" + e.description for e in analysis["events"].events]
        logger.info("Embedding")
        event_embeddings = embeddings.embed_documents(event_batch)
        for i, event in enumerate(analysis["events"].events):
            if not event.end_date:
                event.end_date = ""
            logger.info(f"Saving event {event}")
            _, _, _ = driver.execute_query(
                query_=EVENT_CREATE,
                event=event.model_dump() | {"embedding": event_embeddings[i]},
                source_id=source_id,
            )
            event_map[event.cid] = event
        emotion_map = {e.cid: e for e in analysis["states"].emotional_states}
        symptom_map = {e.cid: e for e in analysis["states"].symptoms}
        traits_map = {e.cid: e for e in analysis["states"].personality_traits}
        for produce in analysis["relations"].produced_emotions:
            event = event_map.get(produce.event_cid)
            target = emotion_map.get(produce.emotion_cid)
            if event is None or target is None:
                continue
            _, _, _ = driver.execute_query(
                query_=PRODUCE_MERGER,
                event=event.model_dump(),
                target=target.model_dump(),
                rel=produce.model_dump(exclude={"event_cid", "emotion_cid"}),
            )
        for cause in analysis["relations"].caused_symptoms:
            event = event_map.get(cause.event_cid)
            target = emotion_map.get(cause.symptom_cid)
            if event is None or target is None:
                continue
            _, _, _ = driver.execute_query(
                query_=CAUSE_MERGE,
                event=event.model_dump(),
                target=target.model_dump(),
                rel=cause.model_dump(exclude={"event_cid", "symptom_cid"}),
            )
        for triger in analysis["relations"].triggered_traits:
            event = event_map.get(triger.event_cid)
            target = emotion_map.get(triger.traits_cid)
            if event is None or target is None:
                continue
            _, _, _ = driver.execute_query(
                query_=TRIGGER_MERGE,
                event=event.model_dump(),
                target=target.model_dump(),
                rel=triger.model_dump(exclude={"event_cid", "traits_cid"}),
            )
        event_ids = list(event_map.keys())
        _, _, _ = driver.execute_query(query_=GET_DATA, ids=event_ids)
    logger.info("Done")
    message.ack()


streaming_pull_future = subscriber.subscribe(subscription_path, callback=callback)
logger.info(f"Listening for messages on {subscription_path}..\n")

with subscriber:
    try:
        # When `timeout` is not set, result() will block indefinitely,
        # unless an exception is encountered first.
        streaming_pull_future.result()
    except KeyboardInterrupt:
        streaming_pull_future.cancel()  # Trigger the shutdown.
        streaming_pull_future.result()  # Block until the shutdown is complete.
