from concurrent.futures import TimeoutError
from google.cloud import pubsub_v1
import orjson

from ..environement import GCLOUD_PROJECT_ID, CHUNK_TOPIC, EVENT_EXTRACTOR
from ..chains import get_event_extractor, get_mistral
from ..schemas import ConversationChunk

subscriber = pubsub_v1.SubscriberClient()
subscription_path = subscriber.subscription_path(GCLOUD_PROJECT_ID, EVENT_EXTRACTOR)

chain = get_event_extractor(get_mistral())

def callback(message: pubsub_v1.subscriber.message.Message) -> None:
    data = orjson.loads(message.data)
    conversation = ConversationChunk.model_validate(data)
    print(f"Receinved chunks, analysing...")
    events = chain.invoke({
        "date": conversation.info.date.strftime("%Y-%M-%d"),
        "content": conversation.content,
        "patient_name": conversation.info.patient_name
    })
    for event in events.events:
        print(event)
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