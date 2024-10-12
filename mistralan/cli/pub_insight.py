from neo4j import GraphDatabase
from neo4j.graph import Node, Relationship
import orjson
from typing import cast

from ..environement import (
    NEO4J_HOST,
    NEO4J_PASSWORD,
    NEO4J_USER,
    GCLOUD_PROJECT_ID,
    INSIGHT_TOPIC,
)
from google.cloud import pubsub_v1


publisher = pubsub_v1.PublisherClient()
topic_path = publisher.topic_path(GCLOUD_PROJECT_ID, INSIGHT_TOPIC)

GET_DATA = """MATCH path = (e:Event)-[r1]->(n)<-[r2]-(other:Event)
WHERE e.source_id STARTS WITH '1.' AND not n:Event
UNWIND relationships(path) as rels
UNWIND nodes(path) as nodes
return collect(distinct rels) as rels, collect(distinct nodes) as nodes
"""

with GraphDatabase.driver(NEO4J_HOST, auth=(NEO4J_USER, NEO4J_PASSWORD)) as driver:
    driver.verify_connectivity()
    records, _, _ = driver.execute_query(GET_DATA, ids=["argument_with_manager"])

nodes = {}
edges = []

for node in records[0].get("nodes"):
    node = cast(Node, node)
    print(node)
    nodes[node.element_id] = {**node, "_id": node.element_id}

data = orjson.dumps(nodes)


future = publisher.publish(topic_path, data)
print(future.result())

print(f"Published messages to {topic_path}.")
