# Setup

## Neo4J

Pop a Neo4J instance and add those indexes:

**Vector Index on Events**

```cypher
CREATE VECTOR INDEX events IF NOT EXISTS
FOR (m:Event)
ON m.embedding
OPTIONS { indexConfig: {
 `vector.dimensions`: 1024,
 `vector.similarity_function`: 'cosine'
}}
```

**Vector Index Usage**
```cypher
MATCH (m:Event {cid: "friend's_text"})
CALL db.index.vector.queryNodes('events', 5, m.embedding)
YIELD node AS event, score
RETURN event.name AS name, event.desc AS desc, score
```

**Source Index on Events**
```cypher
CREATE TEXT INDEX event_source IF NOT EXISTS FOR (n:Event) ON (n.source_id)
```
## Google Cloud

Create the pub sub topics as follow:

```bash
gcloud pubsub topics create conversation-chunk
gcloud pubsub subscriptions create chunk-analyser --topic conversation-chunk
gcloud pubsub topics create gcloud pubsub topics create subgraph
gcloud pubsub subscriptions create graph-merger --topic subgraph
```
# Runing

`docker compose up`

## Requirements

**Mistral API Key**
A `MISTRAL_API_KEY` should be accessible to docker compose.

**Environement**
Check the environement.py file for environement vars. Default values shall be correct tho.
