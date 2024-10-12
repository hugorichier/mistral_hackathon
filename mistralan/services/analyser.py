import time
from google.cloud import pubsub_v1
import orjson

from ..environement import GCLOUD_PROJECT_ID, CHUNK_ANALYSER_SUB, GRAPH_TOPIC
from ..chains import (
    get_event_extractor,
    get_mistral,
    get_linker,
    get_extractor,
    get_states_extractor,
    AnalyserOutput,
)
from ..schemas import ConversationChunk

subscriber = pubsub_v1.SubscriberClient()
subscription_path = subscriber.subscription_path(GCLOUD_PROJECT_ID, CHUNK_ANALYSER_SUB)

publisher = pubsub_v1.PublisherClient()
topic_path = publisher.topic_path(GCLOUD_PROJECT_ID, GRAPH_TOPIC)

llm = get_mistral()

event_extractor = get_event_extractor(llm)
state_extractor = get_states_extractor(llm)
extractor = get_extractor(
    event_extractor=event_extractor, state_extractor=state_extractor
)
linker = get_linker(llm)

chain = extractor | linker


def callback(message: pubsub_v1.subscriber.message.Message) -> None:  # type: ignore
    data = orjson.loads(message.data)
    conversation_chunk = ConversationChunk.model_validate(data)
    print("Chunk Received")
    print(
        f"Conversation: {conversation_chunk.info.id}\n",
        f"Patient: {conversation_chunk.info.patient_name}",
        f"({conversation_chunk.info.patient_id})",
    )
    print("Analysing...")
    start = time.perf_counter()
    result = chain.invoke({"chunk": conversation_chunk})
    print(f"State:\n{result['states'].describe()}")
    print(f"Events: {len(result['events'].events)}")
    for event in result["events"].events:
        print(event.cid)
    result["relations"].describe()
    print(f"Analysis done in {time.perf_counter() - start}")
    print("Emit message to merger...")
    data = AnalyserOutput.dump_json(result)

    future = publisher.publish(topic_path, data)
    future.result()
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
