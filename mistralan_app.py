import streamlit as st
from google.cloud import pubsub_v1
from mistralan.environement import GCLOUD_PROJECT_ID, CHUNK_TOPIC, NEO4J_HOST, NEO4J_USER, NEO4J_PASSWORD
from mistralan.schemas import ConversationChunk, ConversationInfo
from datetime import date
import orjson
import datetime
from neo4j import GraphDatabase
from neo4j.graph import Node, Relationship
from typing import cast
from streamlit_agraph import agraph, Node, Edge, Config


st.title('hackathon app')
publisher = pubsub_v1.PublisherClient()
topic_path = publisher.topic_path(GCLOUD_PROJECT_ID, CHUNK_TOPIC)
ts = datetime.datetime.now()

with st.sidebar:

    st.write('Conversation inputs')
    chunk_input = st.text_input("Enter the conversation chunk:")
    patient_id = st.text_input("Enter the patient id:", value='001')
    patient_name = st.text_input("Enter the patient name:", value='RoBERTo')
    conversation_id = st.text_input("Enter the conversation id:", value='0')
    chunk_id = 0

    if st.button('Run'):
        try: 
            st.write('running...')
            conversation = ConversationChunk(
                info=ConversationInfo(
                    id=conversation_id,
                    patient_id=patient_id,
                    patient_name=patient_name,
                    date=date.today() + datetime.timedelta(weeks=70)),
                content=chunk_input,
                ts=0
            )
            data = orjson.dumps(conversation.model_dump(mode="json"))
            future = publisher.publish(topic_path,data)
            chunk_id+=1
            st.write(future.result())

        except Exception as e:
            st.write('An error occurred:', e)
        

agraph_nodes = []
agraph_edges = []

with st.sidebar:
    refresh_button = st.button('refresh')

    if refresh_button:
        GET_DATA = """MATCH path = (e:Event)-[r1]->(n)<-[r2]-(other:Event)
                        WHERE e.source_id STARTS WITH '1.' AND not n:Event
                        UNWIND relationships(path) as rels
                        UNWIND nodes(path) as nodes
                        return collect(distinct rels) as rels, collect(distinct nodes) as nodes
                        """

        with GraphDatabase.driver(NEO4J_HOST, auth=(NEO4J_USER, NEO4J_PASSWORD)) as driver:
            driver.verify_connectivity()
            records, _, _ = driver.execute_query(GET_DATA)

        element_id_to_cid = {}
        cid_to_node = {}
        edges = []

        label_to_color = {
            "Emotion": "#33658A",
            "Cause": "#F26419",
            "PersonalityTrait": "#86BBD8",
            "Event": "#758E4F",
            "Symptom": "#F6AE2D"}

        for node in records[0].get("nodes"):

            node = cast(Node, node)
            element_id_to_cid[node.element_id] = node.get("cid")
            node_type, = node.labels
            if node.get("cid") not in cid_to_node:
                agraph_nodes.append(Node(id=node.get("cid"),
                    size=25 if node_type == "Event" else 15,
                    label = node.get("name"),
                    color=label_to_color[node_type],
                    title=node.get("desc")
                ))

                cid_to_node[node.get("cid")] = {**node}

        for rel in records[0].get("rels"):
            rel = cast(Relationship, rel)
            start_cid = element_id_to_cid[rel.start_node.element_id]
            end_cid = element_id_to_cid[rel.end_node.element_id]

            agraph_edges.append( Edge(source=start_cid,
                   target=end_cid,
                   label=rel.type,
                   color="black"
                   ) 
            )
        print(agraph_edges)


config = Config(width=750,
    height=950,
    directed=True, 
    physics=True, 
    hierarchical=False,
    # **kwargs
    )

return_value = agraph(nodes=agraph_nodes, 
                edges=agraph_edges, 
                config=config)

