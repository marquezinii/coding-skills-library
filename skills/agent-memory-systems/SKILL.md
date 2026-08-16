---
name: agent-memory-systems
description: "Memory is the cornerstone of intelligent agents. Without it, every
  interaction starts from zero. This skill covers the architecture of agent
  memory: short-term (context window), long-term (vector stores), and the
  cognitive architectures that organize them."
metadata:
  risk: safe
  source: vibeship-spawner-skills (Apache 2.0)
  date_added: 2026-02-27
---

# Agent Memory Systems

Memory is the cornerstone of intelligent agents. Without it, every interaction
starts from zero. This skill covers the architecture of agent memory: short-term
(context window), long-term (vector stores), and the cognitive architectures
that organize them.

Key insight: Memory isn't just storage - it's retrieval. A million stored facts
mean nothing if you can't find the right one. Chunking, embedding, and retrieval
strategies determine whether your agent remembers or forgets.

The field is fragmented with inconsistent terminology. We use the CoALA cognitive
architecture framework: semantic memory (facts), episodic memory (experiences),
and procedural memory (how-to knowledge).

## Principles

- Memory quality = retrieval quality, not storage quantity
- Chunk for retrieval, not for storage
- Context isolation is the enemy of memory
- Right memory type for right information
- Decay old memories - not everything should be forever
- Test retrieval accuracy before production
- Background memory formation beats real-time

## Capabilities

- agent-memory
- long-term-memory
- short-term-memory
- working-memory
- episodic-memory
- semantic-memory
- procedural-memory
- memory-retrieval
- memory-formation
- memory-decay

## Scope

- vector-database-operations → data-engineer
- rag-pipeline-architecture → llm-architect
- embedding-model-selection → ml-engineer
- knowledge-graph-design → knowledge-engineer

## Tooling

### Memory_frameworks

- LangMem (LangChain) - When: LangGraph agents with persistent memory Note: Semantic, episodic, procedural memory types
- MemGPT / Letta - When: Virtual context management, OS-style memory Note: Hierarchical memory tiers, automatic paging
- Mem0 - When: User memory layer for personalization Note: Designed for user preferences and history

### Vector_stores

- Pinecone - When: Managed, enterprise-scale (billions of vectors) Note: Best query performance, highest cost
- Qdrant - When: Complex metadata filtering, open-source Note: Rust-based, excellent filtering
- Weaviate - When: Hybrid search, knowledge graph features Note: GraphQL interface, good for relationships
- ChromaDB - When: Prototyping, small/medium apps Note: Developer-friendly, ~20ms p50 at 100K vectors
- pgvector - When: Already using PostgreSQL, simpler setup Note: Good for <1M vectors, familiar tooling

### Embedding_models

- OpenAI text-embedding-3-large - When: Best quality, 3072 dimensions Note: $0.13/1M tokens
- OpenAI text-embedding-3-small - When: Good balance, 1536 dimensions Note: $0.02/1M tokens, 5x cheaper
- nomic-embed-text-v1.5 - When: Open-source, local deployment Note: 768 dimensions, good quality
- all-MiniLM-L6-v2 - When: Lightweight, fast local embedding Note: 384 dimensions, lowest latency

## Patterns

### Memory Type Architecture

Choosing the right memory type for different information

**When to use**: Designing agent memory system

# MEMORY TYPE ARCHITECTURE (CoALA Framework):

"""
Three memory types for different purposes:

1. Semantic Memory: Facts and knowledge
   - What you know about the world
   - User preferences, domain knowledge
   - Stored in profiles (structured) or collections (unstructured)

2. Episodic Memory: Experiences and events
   - What happened (timestamped events)
   - Past conversations, task outcomes
   - Used for learning from experience

3. Procedural Memory: How to do things
   - Rules, skills, workflows
   - Often implemented as few-shot examples
   - "How did I solve this before?"
"""

## LangMem Implementation
"""
from langmem import MemoryStore
from langgraph.graph import StateGraph

# Initialize memory store
memory = MemoryStore(
    connection_string=os.environ["POSTGRES_URL"]
)

# Semantic memory: user profile
await memory.semantic.upsert(
    namespace="user_profile",
    key=user_id,
    content={
        "name": "Alice",
        "preferences": ["dark mode", "concise responses"],
        "expertise_level": "developer",
    }
)

# Episodic memory: past interaction
await memory.episodic.add(
    namespace="conversations",
    content={
        "timestamp": datetime.now(),
        "summary": "Helped debug authentication issue",
        "outcome": "resolved",
        "key_insights": ["Token expiry was root cause"],
    },
    metadata={"user_id": user_id, "topic": "debugging"}
)

# Procedural memory: learned pattern
await memory.procedural.add(
    namespace="skills",
    content={
        "task_type": "debug_auth",
        "steps": ["Check token expiry", "Verify refresh flow"],
        "example_interaction": few_shot_example,
    }
)
"""

## Memory Retrieval at Runtime
"""
async def prepare_context(user_id, query):
    # Get user profile (semantic)
    profile = await memory.semantic.get(
        namespace="user_profile",
        key=user_id
    )

    # Find relevant past experiences (episodic)
    similar_experiences = await memory.episodic.search(
        namespace="conversations",
        query=query,
        filter={"user_id": user_id},
        limit=3
    )

    # Find relevant skills (procedural)
    relevant_skills = await memory.procedural.search(
        namespace="skills",
        query=query,
        limit=2
    )

    return {
        "profile": profile,
        "past_experiences": similar_experiences,
        "relevant_skills": relevant_skills,
    }
"""

### Vector Store Selection Pattern

Choosing the right vector database for your use case

**When to use**: Setting up persistent memory storage

# VECTOR STORE SELECTION:

"""
Decision matrix:

|            | Pinecone | Qdrant | Weaviate | ChromaDB | pgvector |
|------------|----------|--------|----------|----------|----------|
| Scale      | Billions | 100M+  | 100M+    | 1M       | 1M       |
| Managed    | Yes      | Both   | Both     | Self     | Self     |
| Filtering  | Basic    | Best   | Good     | Basic    | SQL      |
| Hybrid     | No       | Yes    | Best     | No       | Yes      |
| Cost       | High     | Medium | Medium   | Free     | Free     |
| Latency    | 5ms      | 7ms    | 10ms     | 20ms     | 15ms     |
"""

## Pinecone (Enterprise Scale)
"""
from pinecone import Pinecone

pc = Pinecone(api_key=os.environ["PINECONE_API_KEY"])
index = pc.Index("agent-memory")

# Upsert with metadata
index.upsert(
    vectors=[
        {
            "id": f"memory-{uuid4()}",
            "values": embedding,
            "metadata": {
                "user_id": user_id,
                "timestamp": datetime.now().isoformat(),
                "type": "episodic",
                "content": memory_text,
            }
        }
    ],
    namespace=namespace
)

# Query with filter
results = index.query(
    vector=query_embedding,
    filter={"user_id": user_id, "type": "episodic"},
    top_k=5,
    include_metadata=True
)
"""

## Qdrant (Complex Filtering)
"""
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct, Filter, FieldCondition

client = QdrantClient(url="http://localhost:6333")

# Complex filtering with Qdrant
results = client.search(
    collection_name="agent_memory",
    query_vector=query_embedding,
    query_filter=Filter(
        must=[
            FieldCondition(key="user_id", match={"value": user_id}),
            FieldCondition(key="type", match={"value": "semantic"}),
        ],
        should=[
            FieldCondition(key="topic", match={"any": ["auth", "security"]}),
        ]
    ),
    limit=5
)
"""

## ChromaDB (Prototyping)
"""
import chromadb

client = chromadb.PersistentClient(path="./memory_db")
collection = client.get_or_create_collection("agent_memory")

# Simple and fast for prototypes
collection.add(
    ids=[str(uuid4())],
    embeddings=[embedding],
    documents=[memory_text],
    metadatas=[{"user_id": user_id, "type": "episodic"}]
)

results = collection.query(
    query_embeddings=[query_embedding],
    n_results=5,
    where={"user_id": user_id}
)
"""

### Chunking Strategy Pattern

Breaking documents into retrievable chunks

**When to use**: Processing documents for memory storage

# CHUNKING STRATEGIES:

"""
The chunking dilemma:
- Too large: Vector loses specificity
- Too small: Loses context

Optimal chunk size depends on:
- Document type (code vs prose vs data)
- Query patterns (factual vs exploratory)
- Embedding model (each has sweet spot)

General guidance: 256-512 tokens for most use cases
"""

## Fixed-Size Chunking (Baseline)
"""
from langchain.text_splitter import RecursiveCharacterTextSplitter

splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,      # Characters
    chunk_overlap=50,    # Overlap prevents cutting sentences
    separators=["\n\n", "\n", ". ", " ", ""]  # Priority order
)

chunks = splitter.split_text(document)
"""

## Semantic Chunking (Better Quality)
"""
from langchain_experimental.text_splitter import SemanticChunker
from langchain_openai import OpenAIEmbeddings

# Splits based on semantic similarity
splitter = SemanticChunker(
    embeddings=OpenAIEmbeddings(),
    breakpoint_threshold_type="percentile",
    breakpoint_threshold_amount=95
)

chunks = splitter.split_text(document)
"""


## Extended guidance

Detailed sections were moved without removing content. Load only the sections needed for the current task:

- [Structure-Aware Chunking (Documents with Hierarchy)](references/extended-guidance.md#structure-aware-chunking-documents-with-hierarchy)
- [Contextual Chunking (Anthropic's Approach)](references/extended-guidance.md#contextual-chunking-anthropics-approach)
- [Code-Specific Chunking](references/extended-guidance.md#code-specific-chunking)
- [LangGraph Background Processing](references/extended-guidance.md#langgraph-background-processing)
- [Memory Consolidation (Like Sleep)](references/extended-guidance.md#memory-consolidation-like-sleep)
- [Time-Based Decay](references/extended-guidance.md#time-based-decay)
- [Utility-Based Decay (MIRIX Approach)](references/extended-guidance.md#utility-based-decay-mirix-approach)
- [Sharp Edges](references/extended-guidance.md#sharp-edges)
- [Hierarchical Chunking](references/extended-guidance.md#hierarchical-chunking)
- [Test different sizes](references/extended-guidance.md#test-different-sizes)
- [Size recommendations by content type](references/extended-guidance.md#size-recommendations-by-content-type)
- [Use overlap to prevent boundary issues](references/extended-guidance.md#use-overlap-to-prevent-boundary-issues)
- [Always filter by metadata first](references/extended-guidance.md#always-filter-by-metadata-first)
- [Use hybrid search (semantic + keyword)](references/extended-guidance.md#use-hybrid-search-semantic-keyword)
- [Rerank results with cross-encoder](references/extended-guidance.md#rerank-results-with-cross-encoder)
- [Add temporal scoring](references/extended-guidance.md#add-temporal-scoring)
- [Update instead of append for preferences](references/extended-guidance.md#update-instead-of-append-for-preferences)
- [Explicit versioning for facts](references/extended-guidance.md#explicit-versioning-for-facts)
- [Detect conflicts on storage](references/extended-guidance.md#detect-conflicts-on-storage)
- [Conflict detection heuristic](references/extended-guidance.md#conflict-detection-heuristic)
- [Periodic consolidation](references/extended-guidance.md#periodic-consolidation)
- [Budget tokens for different memory types](references/extended-guidance.md#budget-tokens-for-different-memory-types)
- [Dynamic k based on chunk size](references/extended-guidance.md#dynamic-k-based-on-chunk-size)
- [Track embedding model in metadata](references/extended-guidance.md#track-embedding-model-in-metadata)
- [Filter by model version on retrieval](references/extended-guidance.md#filter-by-model-version-on-retrieval)
- Additional subsections remain in the same reference.

