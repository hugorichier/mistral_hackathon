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
