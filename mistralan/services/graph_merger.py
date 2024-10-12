from neo4j import GraphDatabase
import orjson

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
    e.source_id = $source_id
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


def callback(message: pubsub_v1.subscriber.message.Message) -> None:  # type: ignore
    with GraphDatabase.driver(NEO4J_HOST, auth=(NEO4J_USER, NEO4J_PASSWORD)) as driver:
        driver.verify_connectivity()
        data = orjson.loads(message.data)
        print("Received data")
        analysis = AnalyserOutput.validate_python(data)
        source_id = analysis["chunk"].info.id + "." + str(analysis["chunk"].ts)
        event_map: dict[str, Event] = {}
        for event in analysis["events"].events:
            if not event.end_date:
                event.end_date = ""
            print("Saving event", event)
            _, _, _ = driver.execute_query(
                query_=EVENT_CREATE,
                event=event.model_dump(),
                source_id=source_id,
            )
            event_map[event.cid] = event
        emotion_map = {e.cid: e for e in analysis["states"].emotional_states}
        symptom_map = {e.cid: e for e in analysis["states"].symptoms}
        traits_map = {e.cid: e for e in analysis["states"].personality_traits}
        for produce in analysis["relations"].produced_emotions:
            event = event_map[produce.event_cid]
            target = emotion_map[produce.emotion_cid]
            _, _, _ = driver.execute_query(
                query_=PRODUCE_MERGER,
                event=event.model_dump(),
                target=target.model_dump(),
                rel=produce.model_dump(exclude={"event_cid", "emotion_cid"}),
            )
        for cause in analysis["relations"].caused_symptoms:
            event = event_map[cause.event_cid]
            target = symptom_map[cause.symptom_cid]
            _, _, _ = driver.execute_query(
                query_=CAUSE_MERGE,
                event=event.model_dump(),
                target=target.model_dump(),
                rel=cause.model_dump(exclude={"event_cid", "symptom_cid"}),
            )
        for triger in analysis["relations"].triggered_traits:
            event = event_map[triger.event_cid]
            target = traits_map[triger.traits_cid]
            _, _, _ = driver.execute_query(
                query_=TRIGGER_MERGE,
                event=event.model_dump(),
                target=target.model_dump(),
                rel=triger.model_dump(exclude={"event_cid", "traits_cid"}),
            )
        event_ids = list(event_map.keys())
        records, _, _ = driver.execute_query(query_=GET_DATA, ids=event_ids)
    print("Done")
    message.ack()


streaming_pull_future = subscriber.subscribe(subscription_path, callback=callback)
print(f"Listening for messages on {subscription_path}..\n")

with subscriber:
    try:
        # When `timeout` is not set, result() will block indefinitely,
        # unless an exception is encountered first.
        streaming_pull_future.result()
    except KeyboardInterrupt:
        streaming_pull_future.cancel()  # Trigger the shutdown.
        streaming_pull_future.result()  # Block until the shutdown is complete.
