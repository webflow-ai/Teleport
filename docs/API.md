# API Reference

This document provides a comprehensive reference for all public interfaces and methods in the Context-Aware Retrieval Engine.

## Table of Contents

- [Embedding Generator](#embedding-generator)
- [Vector Store](#vector-store)
  - [VectorStore (Abstract)](#vectorstore-abstract)
  - [FAISSVectorStore](#faissvectorstore)
  - [ChromaDBVectorStore](#chromadbvectorstore)
  - [NumpyVectorStore](#numpyvectorstore)
- [Retrieval Strategies](#retrieval-strategies)
  - [RetrievalStrategy (Abstract)](#retrievalstrategy-abstract)
  - [RawVectorSearch](#rawvectorsearch)
  - [AIEnhancedRetrieval](#aienhancedretrieval)
- [Query Expander](#query-expander)
- [Orchestrator](#orchestrator)
- [Benchmark Engine](#benchmark-engine)
- [Data Models](#data-models)
- [Configuration](#configuration)

---

## Embedding Generator

### `EmbeddingGenerator`

Generates vector embeddings from text using sentence-transformers.

#### Constructor

```python
EmbeddingGenerator(model_name: str = "all-MiniLM-L6-v2")
```

**Parameters:**
- `model_name` (str, optional): Name of the sentence-transformers model to use. Default: `"all-MiniLM-L6-v2"`.

**Raises:**
- `ModelNotFoundError`: If the specified model cannot be found.
- `MemoryError`: If insufficient memory to load the model.
- `RuntimeError`: For other model loading failures.

**Example:**
```python
from src.embedding import EmbeddingGenerator

# Use default model
generator = EmbeddingGenerator()

# Use custom model
generator = EmbeddingGenerator("paraphrase-MiniLM-L6-v2")
```

#### Methods

##### `encode(texts: Union[str, List[str]]) -> np.ndarray`

Generate embeddings for input text(s).

**Parameters:**
- `texts` (str or List[str]): Single string or list of strings to encode.

**Returns:**
- `np.ndarray`: NumPy array of shape `(n, embedding_dim)` where `n` is the number of texts.

**Raises:**
- `ValueError`: If texts is empty or contains empty strings.
- `TypeError`: If texts contains non-string elements.

**Example:**
```python
# Single text
embedding = generator.encode("How does the system handle peak load?")
print(embedding.shape)  # (1, 384)

# Multiple texts
embeddings = generator.encode([
    "First document text",
    "Second document text"
])
print(embeddings.shape)  # (2, 384)
```

##### `get_embedding_dimension() -> int`

Return the dimensionality of generated embeddings.

**Returns:**
- `int`: Embedding dimension (e.g., 384 for all-MiniLM-L6-v2).

**Example:**
```python
dim = generator.get_embedding_dimension()
print(f"Embedding dimension: {dim}")  # 384
```

---

## Vector Store

### `VectorStore` (Abstract)

Abstract interface for vector storage backends. All vector store implementations must inherit from this class.

#### Methods

##### `add(embeddings: np.ndarray, texts: List[str], metadata: Optional[List[Dict]] = None) -> None`

Store embeddings with associated text and metadata.

**Parameters:**
- `embeddings` (np.ndarray): NumPy array of shape `(n, embedding_dim)`.
- `texts` (List[str]): List of text strings corresponding to each embedding.
- `metadata` (Optional[List[Dict]]): Optional list of metadata dictionaries.

**Raises:**
- `ValueError`: If embeddings and texts have mismatched lengths.
- `DimensionMismatchError`: If embeddings have wrong dimensionality.

##### `search(query_embedding: np.ndarray, k: int = 3) -> List[SearchResult]`

Find k most similar embeddings.

**Parameters:**
- `query_embedding` (np.ndarray): NumPy array of shape `(embedding_dim,)` or `(1, embedding_dim)`.
- `k` (int, optional): Number of results to return. Default: 3.

**Returns:**
- `List[SearchResult]`: List of SearchResult objects sorted by similarity (highest first).

**Raises:**
- `ValueError`: If k <= 0.
- `DimensionMismatchError`: If query_embedding has wrong dimensionality.

##### `save(path: str) -> None`

Persist vector store to disk.

**Parameters:**
- `path` (str): Directory path where store should be saved.

**Raises:**
- `IOError`: If unable to write to path.

##### `load(path: str) -> None`

Load vector store from disk.

**Parameters:**
- `path` (str): Directory path where store is saved.

**Raises:**
- `IOError`: If unable to read from path.
- `FileNotFoundError`: If path does not exist.

---

### `FAISSVectorStore`

FAISS-based vector store implementation using IndexFlatIP for cosine similarity.

#### Constructor

```python
FAISSVectorStore(dimension: int, similarity_metric: str = "cosine")
```

**Parameters:**
- `dimension` (int): Dimensionality of embeddings.
- `similarity_metric` (str, optional): `"cosine"` or `"euclidean"`. Default: `"cosine"`.

**Raises:**
- `ValueError`: If similarity_metric is not supported.
- `ImportError`: If faiss-cpu is not installed.

**Example:**
```python
from src.storage import FAISSVectorStore

# Create FAISS store with cosine similarity
store = FAISSVectorStore(dimension=384, similarity_metric="cosine")

# Add embeddings
store.add(embeddings, texts, metadata)

# Search
results = store.search(query_embedding, k=3)

# Persist
store.save("./vector_store")

# Load
store.load("./vector_store")
```

---

### `ChromaDBVectorStore`

ChromaDB-based vector store with built-in persistence.

#### Constructor

```python
ChromaDBVectorStore(collection_name: str = "rag_collection", 
                    persist_directory: str = "./chroma_db")
```

**Parameters:**
- `collection_name` (str, optional): Name of the ChromaDB collection. Default: `"rag_collection"`.
- `persist_directory` (str, optional): Directory for persistent storage. Default: `"./chroma_db"`.

**Raises:**
- `ImportError`: If chromadb is not installed.

**Example:**
```python
from src.storage import ChromaDBVectorStore

# Create ChromaDB store
store = ChromaDBVectorStore(
    collection_name="my_docs",
    persist_directory="./my_chroma_db"
)

# Add embeddings
store.add(embeddings, texts, metadata)

# Search
results = store.search(query_embedding, k=3)

# ChromaDB automatically persists data
```

---

### `NumpyVectorStore`

Simple NumPy-based vector store for small datasets and testing.

#### Constructor

```python
NumpyVectorStore(similarity_metric: str = "cosine")
```

**Parameters:**
- `similarity_metric` (str, optional): `"cosine"` or `"euclidean"`. Default: `"cosine"`.

**Raises:**
- `ValueError`: If similarity_metric is not supported.

**Example:**
```python
from src.storage import NumpyVectorStore

# Create NumPy store
store = NumpyVectorStore(similarity_metric="cosine")

# Add embeddings
store.add(embeddings, texts, metadata)

# Search
results = store.search(query_embedding, k=3)

# Persist
store.save("./numpy_store")

# Load
store.load("./numpy_store")
```

---

## Retrieval Strategies

### `RetrievalStrategy` (Abstract)

Abstract interface for retrieval strategies. All retrieval strategy implementations must inherit from this class.

#### Methods

##### `retrieve(query: str, k: int = 3) -> RetrievalResult`

Execute retrieval strategy.

**Parameters:**
- `query` (str): The user query string.
- `k` (int, optional): Number of results to return. Default: 3.

**Returns:**
- `RetrievalResult`: Object containing chunks, scores, and metadata.

**Raises:**
- `ValueError`: If query is empty or k is invalid.

---

### `RawVectorSearch`

Direct embedding-based similarity search without query modification.

#### Constructor

```python
RawVectorSearch(embedding_generator: EmbeddingGenerator, 
                vector_store: VectorStore)
```

**Parameters:**
- `embedding_generator` (EmbeddingGenerator): Component for generating text embeddings.
- `vector_store` (VectorStore): Component for storing and searching embeddings.

**Example:**
```python
from src.retrieval import RawVectorSearch
from src.embedding import EmbeddingGenerator
from src.storage import FAISSVectorStore

# Create components
generator = EmbeddingGenerator()
store = FAISSVectorStore(dimension=384)

# Create strategy
strategy = RawVectorSearch(generator, store)

# Retrieve
result = strategy.retrieve("How does the system handle peak load?", k=3)
print(f"Found {len(result.chunks)} chunks")
print(f"Latency: {result.latency_ms:.2f} ms")
```

#### Methods

##### `retrieve(query: str, k: int = 3) -> RetrievalResult`

Execute raw vector search retrieval.

**Parameters:**
- `query` (str): The user query string.
- `k` (int, optional): Number of results to return. Default: 3.

**Returns:**
- `RetrievalResult`: Result with original query and top-k similar chunks.

**Raises:**
- `ValueError`: If query is empty or k is invalid.

---

### `AIEnhancedRetrieval`

Query expansion followed by similarity search.

#### Constructor

```python
AIEnhancedRetrieval(embedding_generator: EmbeddingGenerator, 
                    vector_store: VectorStore,
                    query_expander: QueryExpander)
```

**Parameters:**
- `embedding_generator` (EmbeddingGenerator): Component for generating text embeddings.
- `vector_store` (VectorStore): Component for storing and searching embeddings.
- `query_expander` (QueryExpander): Component for expanding/rewriting queries.

**Example:**
```python
from src.retrieval import AIEnhancedRetrieval
from src.embedding import EmbeddingGenerator
from src.storage import FAISSVectorStore
from src.mocks import QueryExpander

# Create components
generator = EmbeddingGenerator()
store = FAISSVectorStore(dimension=384)
expander = QueryExpander(expansion_strategy="synonym_addition")

# Create strategy
strategy = AIEnhancedRetrieval(generator, store, expander)

# Retrieve
result = strategy.retrieve("How does the system handle peak load?", k=3)
print(f"Original query: {result.query}")
print(f"Expanded query: {result.expanded_query}")
print(f"Found {len(result.chunks)} chunks")
```

#### Methods

##### `retrieve(query: str, k: int = 3) -> RetrievalResult`

Execute AI-enhanced retrieval with query expansion.

**Parameters:**
- `query` (str): The user query string.
- `k` (int, optional): Number of results to return. Default: 3.

**Returns:**
- `RetrievalResult`: Result with both original and expanded queries, plus top-k chunks.

**Raises:**
- `ValueError`: If query is empty or k is invalid.

---

## Query Expander

### `QueryExpander`

Mocks Vertex AI GenerativeModel for query expansion using rule-based strategies.

#### Constructor

```python
QueryExpander(expansion_strategy: str = "synonym_addition")
```

**Parameters:**
- `expansion_strategy` (str, optional): Strategy to use for query expansion.
  - `"synonym_addition"`: Add synonyms to key terms
  - `"clarification"`: Add clarifying phrases
  - `"decomposition"`: Break complex queries into sub-queries
  
  Default: `"synonym_addition"`.

**Raises:**
- `ValueError`: If expansion_strategy is not valid.

**Example:**
```python
from src.mocks import QueryExpander

# Create expander with synonym addition
expander = QueryExpander(expansion_strategy="synonym_addition")

# Expand query
expanded = expander.expand_query("How does the system handle peak load?")
print(f"Expanded: {expanded}")

# Get interaction log
log = expander.get_interaction_log()
print(f"Total interactions: {len(log)}")
```

#### Methods

##### `expand_query(query: str) -> str`

Expand query using rule-based logic.

**Parameters:**
- `query` (str): The original user query string.

**Returns:**
- `str`: The expanded query string.

**Raises:**
- `ValueError`: If query is empty or None.

**Example:**
```python
# Synonym addition
expander = QueryExpander("synonym_addition")
result = expander.expand_query("fix the error")
# Result: "fix (resolve) the error (exception)"

# Clarification
expander = QueryExpander("clarification")
result = expander.expand_query("How does caching work?")
# Result: "What are the specific steps and mechanisms for does caching work?"

# Decomposition
expander = QueryExpander("decomposition")
result = expander.expand_query("What are the benefits and challenges?")
# Result: "What are the benefits and challenges? (including implementation, benefits, and challenges)"
```

##### `get_interaction_log() -> List[Dict]`

Return all logged interactions for debugging.

**Returns:**
- `List[Dict]`: List of dictionaries containing interaction details.
  - `timestamp`: ISO format timestamp
  - `strategy`: The expansion strategy used
  - `original_query`: The original query string
  - `expanded_query`: The expanded query string
  - `expansion_occurred`: Boolean indicating if expansion changed the query

**Example:**
```python
log = expander.get_interaction_log()
for entry in log:
    print(f"{entry['timestamp']}: {entry['original_query']} -> {entry['expanded_query']}")
```

---

## Orchestrator

### `RAGOrchestrator`

Coordinates the complete ingestion and retrieval pipeline.

#### Constructor

```python
RAGOrchestrator(embedding_generator: EmbeddingGenerator,
                vector_store: VectorStore,
                strategies: Dict[str, RetrievalStrategy])
```

**Parameters:**
- `embedding_generator` (EmbeddingGenerator): Component for generating text embeddings.
- `vector_store` (VectorStore): Component for storing and searching embeddings.
- `strategies` (Dict[str, RetrievalStrategy]): Dictionary mapping strategy names to RetrievalStrategy instances.

**Raises:**
- `ValueError`: If strategies dictionary is empty.

**Example:**
```python
from src.orchestrator import RAGOrchestrator
from src.embedding import EmbeddingGenerator
from src.storage import FAISSVectorStore
from src.retrieval import RawVectorSearch, AIEnhancedRetrieval
from src.mocks import QueryExpander

# Create components
generator = EmbeddingGenerator()
store = FAISSVectorStore(dimension=384)
expander = QueryExpander()

# Create strategies
raw_strategy = RawVectorSearch(generator, store)
enhanced_strategy = AIEnhancedRetrieval(generator, store, expander)

# Create orchestrator
orchestrator = RAGOrchestrator(
    embedding_generator=generator,
    vector_store=store,
    strategies={
        "raw": raw_strategy,
        "enhanced": enhanced_strategy
    }
)

# Ingest documents
documents = [
    "The system uses horizontal scaling...",
    "Load balancing distributes traffic..."
]
stats = orchestrator.ingest_documents(documents, chunk_size=500)
print(f"Ingested {stats.total_chunks} chunks in {stats.ingestion_time_ms:.2f} ms")

# Retrieve
result = orchestrator.retrieve("How does the system scale?", "enhanced", k=3)
print(f"Found {len(result.chunks)} chunks")
```

#### Methods

##### `ingest_documents(documents: List[str], chunk_size: int = 500) -> IngestionStats`

Process documents through ingestion pipeline.

**Parameters:**
- `documents` (List[str]): List of document strings to ingest.
- `chunk_size` (int, optional): Maximum size of each chunk in characters. Default: 500.

**Returns:**
- `IngestionStats`: Object containing ingestion metrics.

**Raises:**
- `ValueError`: If documents list is empty or chunk_size is invalid.

**Example:**
```python
documents = [
    "First document with multiple paragraphs...",
    "Second document with technical content..."
]

stats = orchestrator.ingest_documents(documents, chunk_size=500)
print(f"Total chunks: {stats.total_chunks}")
print(f"Embedding dimension: {stats.embedding_dimension}")
print(f"Total tokens: {stats.total_tokens}")
print(f"Ingestion time: {stats.ingestion_time_ms:.2f} ms")
```

##### `retrieve(query: str, strategy_name: str, k: int = 3) -> RetrievalResult`

Execute retrieval using specified strategy.

**Parameters:**
- `query` (str): The user query string.
- `strategy_name` (str): Name of the retrieval strategy to use (must match a key in strategies dictionary).
- `k` (int, optional): Number of results to return. Default: 3.

**Returns:**
- `RetrievalResult`: Object containing chunks, scores, and metadata.

**Raises:**
- `StrategyNotFoundError`: If strategy_name is not found in available strategies.
- `ValueError`: If query is empty or k is invalid.

**Example:**
```python
# Use raw vector search
result = orchestrator.retrieve(
    query="How does the system handle peak load?",
    strategy_name="raw",
    k=3
)

# Use AI-enhanced retrieval
result = orchestrator.retrieve(
    query="How does the system handle peak load?",
    strategy_name="enhanced",
    k=5
)
```

##### `get_statistics() -> Dict`

Return ingestion statistics and system information.

**Returns:**
- `Dict`: Dictionary containing:
  - `total_chunks`: Total number of chunks stored
  - `embedding_dimension`: Dimensionality of embeddings
  - `available_strategies`: List of available retrieval strategy names

**Example:**
```python
stats = orchestrator.get_statistics()
print(f"Total chunks: {stats['total_chunks']}")
print(f"Embedding dimension: {stats['embedding_dimension']}")
print(f"Available strategies: {stats['available_strategies']}")
```

---

## Benchmark Engine

### `BenchmarkEngine`

Compares retrieval strategies across query sets.

#### Constructor

```python
BenchmarkEngine(orchestrator: RAGOrchestrator)
```

**Parameters:**
- `orchestrator` (RAGOrchestrator): RAGOrchestrator instance with configured strategies.

**Raises:**
- `ValueError`: If orchestrator has no configured strategies.

**Example:**
```python
from src.benchmark import BenchmarkEngine

# Create benchmark engine
benchmark = BenchmarkEngine(orchestrator)

# Define queries
queries = [
    "How does the system handle peak load?",
    "What are the security mechanisms?",
    "How is data stored and retrieved?"
]

# Run benchmark
metrics = benchmark.run_benchmark(queries, output_path="benchmark_results.md")

# Analyze results
for strategy_name, metrics in metrics.items():
    print(f"{strategy_name}:")
    print(f"  Avg similarity: {metrics.avg_similarity_score:.4f}")
    print(f"  Unique chunks: {metrics.unique_chunks_retrieved}")
    print(f"  Avg latency: {metrics.avg_latency_ms:.2f} ms")
```

#### Methods

##### `run_benchmark(queries: List[str], output_path: str = "retrieval_benchmark.md") -> Dict`

Execute benchmark suite across all configured strategies.

**Parameters:**
- `queries` (List[str]): List of query strings to benchmark.
- `output_path` (str, optional): Path where benchmark report should be saved. Default: `"retrieval_benchmark.md"`.

**Returns:**
- `Dict`: Dictionary mapping strategy names to BenchmarkMetrics objects.

**Raises:**
- `ValueError`: If queries list is empty.
- `IOError`: If unable to write report to output_path.

**Example:**
```python
queries = [
    "How does the system handle peak load?",
    "What are the security mechanisms?",
    "How is data stored and retrieved?"
]

metrics = benchmark.run_benchmark(
    queries=queries,
    output_path="my_benchmark.md"
)

# Access metrics for specific strategy
raw_metrics = metrics["raw"]
print(f"Raw search avg similarity: {raw_metrics.avg_similarity_score:.4f}")
```

##### `calculate_metrics(strategy_name: str, results: List[RetrievalResult]) -> BenchmarkMetrics`

Calculate aggregated metrics for a strategy's results.

**Parameters:**
- `strategy_name` (str): Name of the strategy being evaluated.
- `results` (List[RetrievalResult]): List of RetrievalResult objects from benchmark execution.

**Returns:**
- `BenchmarkMetrics`: Object with calculated metrics.

**Raises:**
- `ValueError`: If results list is empty.

**Example:**
```python
# Typically called internally by run_benchmark, but can be used directly
results = [result1, result2, result3]
metrics = benchmark.calculate_metrics("raw", results)
print(f"Average similarity: {metrics.avg_similarity_score:.4f}")
```

---

## Data Models

### `SearchResult`

Single search result from vector store.

**Attributes:**
- `text` (str): The original text associated with the embedding.
- `score` (float): Similarity score (higher is more similar).
- `metadata` (Optional[Dict]): Optional metadata dictionary.

**Example:**
```python
from src.models import SearchResult

result = SearchResult(
    text="The system handles peak load by scaling horizontally.",
    score=0.87,
    metadata={"chunk_index": 5, "source": "architecture_doc"}
)
```

---

### `RetrievalResult`

Complete retrieval result with metadata.

**Attributes:**
- `query` (str): The original user query string.
- `expanded_query` (Optional[str]): The expanded query (None for raw search).
- `chunks` (List[str]): List of retrieved text chunks.
- `scores` (List[float]): List of similarity scores corresponding to chunks.
- `latency_ms` (float): Retrieval latency in milliseconds.
- `strategy_name` (str): Name of the retrieval strategy used.

**Example:**
```python
from src.models import RetrievalResult

result = RetrievalResult(
    query="How does the system handle peak load?",
    expanded_query="How does the system handle peak load? (process)",
    chunks=["The system scales horizontally...", "Load balancing is used..."],
    scores=[0.87, 0.82],
    latency_ms=45.3,
    strategy_name="AIEnhancedRetrieval"
)
```

---

### `BenchmarkMetrics`

Aggregated benchmark results for a retrieval strategy.

**Attributes:**
- `strategy_name` (str): Name of the retrieval strategy.
- `avg_similarity_score` (float): Average similarity score across all queries.
- `unique_chunks_retrieved` (int): Number of unique chunks retrieved.
- `avg_latency_ms` (float): Average retrieval latency in milliseconds.
- `query_results` (List[RetrievalResult]): List of individual RetrievalResult objects.

**Example:**
```python
from src.models import BenchmarkMetrics

metrics = BenchmarkMetrics(
    strategy_name="RawVectorSearch",
    avg_similarity_score=0.78,
    unique_chunks_retrieved=12,
    avg_latency_ms=38.5,
    query_results=[result1, result2, result3]
)
```

---

### `IngestionStats`

Statistics from document ingestion.

**Attributes:**
- `total_chunks` (int): Total number of text chunks created.
- `embedding_dimension` (int): Dimensionality of generated embeddings.
- `total_tokens` (int): Approximate total token count.
- `ingestion_time_ms` (float): Total ingestion time in milliseconds.

**Example:**
```python
from src.models import IngestionStats

stats = IngestionStats(
    total_chunks=47,
    embedding_dimension=384,
    total_tokens=5823,
    ingestion_time_ms=1234.5
)
```

---

## Configuration

### `RAGConfig`

System configuration for the Context-Aware Retrieval Engine.

**Attributes:**
- `embedding_model` (str): Name of the sentence-transformers model. Default: `"all-MiniLM-L6-v2"`.
- `vector_store_type` (str): Type of vector store backend (`"faiss"`, `"chromadb"`, `"numpy"`). Default: `"faiss"`.
- `similarity_metric` (str): Similarity metric (`"cosine"`, `"euclidean"`). Default: `"cosine"`.
- `top_k` (int): Number of results to return. Default: 3.
- `chunk_size` (int): Maximum chunk size in characters. Default: 500.
- `chunk_overlap` (int): Overlapping characters between chunks. Default: 50.
- `expansion_strategy` (str): Query expansion strategy. Default: `"synonym_addition"`.
- `benchmark_queries` (List[str]): List of queries for benchmarking. Default: empty list.

**Example:**
```python
from src.config import RAGConfig

# Create configuration with defaults
config = RAGConfig()

# Create custom configuration
config = RAGConfig(
    embedding_model="paraphrase-MiniLM-L6-v2",
    vector_store_type="chromadb",
    similarity_metric="cosine",
    top_k=5,
    chunk_size=300,
    chunk_overlap=30,
    expansion_strategy="clarification",
    benchmark_queries=[
        "How does the system scale?",
        "What are the security features?"
    ]
)

# Validate configuration (automatically called in __post_init__)
config.validate()
```

#### Methods

##### `validate() -> None`

Validate configuration values.

**Raises:**
- `ValueError`: If any configuration value is invalid.

**Example:**
```python
config = RAGConfig(top_k=5)
config.validate()  # Passes

config = RAGConfig(top_k=-1)
config.validate()  # Raises ValueError
```

---

## Complete Usage Example

Here's a complete example demonstrating the full API:

```python
from src.embedding import EmbeddingGenerator
from src.storage import FAISSVectorStore
from src.retrieval import RawVectorSearch, AIEnhancedRetrieval
from src.mocks import QueryExpander
from src.orchestrator import RAGOrchestrator
from src.benchmark import BenchmarkEngine
from src.config import RAGConfig

# 1. Create configuration
config = RAGConfig(
    embedding_model="all-MiniLM-L6-v2",
    vector_store_type="faiss",
    similarity_metric="cosine",
    top_k=3,
    chunk_size=500
)

# 2. Initialize components
generator = EmbeddingGenerator(config.embedding_model)
store = FAISSVectorStore(
    dimension=generator.get_embedding_dimension(),
    similarity_metric=config.similarity_metric
)
expander = QueryExpander(expansion_strategy=config.expansion_strategy)

# 3. Create retrieval strategies
raw_strategy = RawVectorSearch(generator, store)
enhanced_strategy = AIEnhancedRetrieval(generator, store, expander)

# 4. Create orchestrator
orchestrator = RAGOrchestrator(
    embedding_generator=generator,
    vector_store=store,
    strategies={
        "raw": raw_strategy,
        "enhanced": enhanced_strategy
    }
)

# 5. Ingest documents
documents = [
    "The system uses horizontal scaling to handle peak load...",
    "Load balancing distributes traffic across multiple servers...",
    "Caching reduces database queries and improves performance..."
]

stats = orchestrator.ingest_documents(documents, chunk_size=config.chunk_size)
print(f"Ingested {stats.total_chunks} chunks")

# 6. Retrieve with different strategies
query = "How does the system handle peak load?"

# Raw vector search
raw_result = orchestrator.retrieve(query, "raw", k=3)
print(f"Raw search found {len(raw_result.chunks)} chunks")

# AI-enhanced retrieval
enhanced_result = orchestrator.retrieve(query, "enhanced", k=3)
print(f"Enhanced search found {len(enhanced_result.chunks)} chunks")
print(f"Expanded query: {enhanced_result.expanded_query}")

# 7. Run benchmark
benchmark = BenchmarkEngine(orchestrator)
queries = [
    "How does the system handle peak load?",
    "What are the caching mechanisms?",
    "How is load balancing implemented?"
]

metrics = benchmark.run_benchmark(queries, output_path="benchmark.md")

# 8. Analyze results
for strategy_name, strategy_metrics in metrics.items():
    print(f"\n{strategy_name}:")
    print(f"  Avg similarity: {strategy_metrics.avg_similarity_score:.4f}")
    print(f"  Unique chunks: {strategy_metrics.unique_chunks_retrieved}")
    print(f"  Avg latency: {strategy_metrics.avg_latency_ms:.2f} ms")

# 9. Persist vector store
store.save("./my_vector_store")

# 10. Load vector store later
new_store = FAISSVectorStore(dimension=384, similarity_metric="cosine")
new_store.load("./my_vector_store")
```

---

## Error Handling

All components raise descriptive exceptions for error conditions:

- `ModelNotFoundError`: Embedding model not found
- `DimensionMismatchError`: Embedding dimension mismatch
- `StrategyNotFoundError`: Unknown retrieval strategy
- `ValueError`: Invalid parameter values
- `TypeError`: Invalid parameter types
- `IOError`: File I/O errors
- `FileNotFoundError`: Missing files
- `ImportError`: Missing dependencies

**Example:**
```python
try:
    generator = EmbeddingGenerator("nonexistent-model")
except ModelNotFoundError as e:
    print(f"Model error: {e}")

try:
    result = orchestrator.retrieve("query", "unknown_strategy")
except StrategyNotFoundError as e:
    print(f"Strategy error: {e}")
    print(f"Available: {orchestrator.get_statistics()['available_strategies']}")
```

---

## See Also

- [Architecture Documentation](ARCHITECTURE.md)
- [Migration Guide](MIGRATION.md)
- [Benchmarking Guide](BENCHMARKING.md)
- [Similarity Metrics Guide](SIMILARITY_METRICS.md)
- [README](../README.md)
