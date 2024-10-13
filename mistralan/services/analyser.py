import time
from google.cloud import pubsub_v1
import orjson
import logging
import sys
from langchain_core.runnables import RunnableLambda

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

logging.basicConfig(stream=sys.stdout)
logger = logging.getLogger("analyser")
logger.setLevel(logging.INFO)

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


def _sleep(x):
    time.sleep(5)
    return x


chain = RunnableLambda(_sleep) | extractor | linker


def callback(message: pubsub_v1.subscriber.message.Message) -> None:  # type: ignore
    data = orjson.loads(message.data)
    conversation_chunk = ConversationChunk.model_validate(data)
    logger.info("=" * 50)
    logger.info("Chunk Received")
    logger.info(conversation_chunk.info)
    logger.info("Analysing...")
    start = time.perf_counter()
    result = chain.invoke({"chunk": conversation_chunk})
    logger.info(f"State:\n{result['states'].describe()}")
    logger.info(f"Events: {len(result['events'].events)}")
    for event in result["events"].events:
        logger.info(event.cid)
    logger.info(f"Analysis done in {time.perf_counter() - start}")
    logger.info("Emit message to merger...")
    data = AnalyserOutput.dump_json(result)

    future = publisher.publish(topic_path, data)
    future.result()
    message.ack()
    logger.info("End")


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
    except Exception as e:
        logger.warning(f"Error while processing chunk {e}")
