import streamlit as st
from google.cloud import pubsub_v1
from mistralan.environement import GCLOUD_PROJECT_ID, CHUNK_TOPIC
from mistralan.schemas import ConversationChunk, ConversationInfo
from datetime import date
import orjson



st.title('hackathon app')
publisher = pubsub_v1.PublisherClient()
topic_path = publisher.topic_path(GCLOUD_PROJECT_ID, CHUNK_TOPIC)

chunk_input = st.text_input("Enter the conversation chunk:")
patient_id = st.text_input("Enter the patient id:", value='001')
patient_name = st.text_input("Enter the patient name:", value='RoBERTo')
chunk_id = 0

if st.button('Run'):
    try: 
        st.write('running...')
        conversation = ConversationChunk(
            info=ConversationInfo(
                id="0",
                patient_id="001",
                patient_name="RoBERTo",
                date=date.today()),
            content=chunk_input,
            ts=0
        )
        data = orjson.dumps(conversation.model_dump(mode="json"))
        future = publisher.publish(topic_path, data)
        chunk_id+=1
        st.write(future.result())

    except Exception as e:
        st.write('An error occurred:', e)
        
        