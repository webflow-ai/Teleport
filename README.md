# Context-Aware Retrieval Engine

A local Retrieval-Augmented Generation (RAG) pipeline that demonstrates semantic search capabilities using vector embeddings. The system provides two retrieval strategies—direct similarity search and AI-enhanced query expansion—with comprehensive benchmarking to compare their effectiveness.

## Features

- **Local-First Architecture**: Runs entirely on your machine using open-source libraries (sentence-transformers, FAISS, ChromaDB)
- **Dual Retrieval Strategies**: Compare raw vector search against AI-enhanced query expansion
- **Multiple Vector Store Backends**: Choose between FAISS, ChromaDB, or NumPy-based storage
- **Comprehensive Benchmarking**: Built-in tools to quantify retrieval effectiveness
- **Cloud Migration Path**: Designed for easy migration to Vertex AI services
- **Property-Based Testing**: Extensive test coverage with 26 correctness properties

## Quick Start

### Installation

1. **Clone the repository**:
```bash
git clone <repository-url>
cd context-aware-retrieval-engine
```

2. **Create a virtual environment** (recommended):
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. **Install dependencies**:
```bash
pip install -r requirements.txt
```

### Basic Usage

Here's a minimal example to get started:

```python
from src.embedding import EmbeddingGenerator
from src.storage import NumpyVectorStore
from src.retrieval import RawVectorSearch, AIEnhancedRetrieval
from src.mocks import QueryExpander
from src.orchestrator import RAGOrchestrator

# Initialize components
embedding_generator = EmbeddingGenerator(model_name="all-MiniLM-L6-v2")
vector_store = NumpyVectorStore(similarity_metric="cosine")

# Create retrieval strategies
raw_strategy = RawVectorSearch(embedding_generator, vector_store)

query_expander = QueryExpander(expansion_strategy="synonym_addition")
enhanced_strategy = AIEnhancedRetrieval(
    embedding_generator, 
    vector_store, 
    query_expander
)

# Create orchestrator
orchestrator = RAGOrchestrator(
    embedding_generator,
    vector_store,
    strategies={"raw": raw_strategy, "enhanced": enhanced_strategy}
)

# Ingest documents
documents = [
    "Microservices architecture is a design pattern...",
    "Load balancing distributes incoming network traffic...",
    "Caching is a technique used to store frequently accessed data..."
]

stats = orchestrator.ingest_documents(documents, chunk_size=300)
print(f"Ingested {stats.total_chunks} chunks in {stats.ingestion_time_ms:.2f}ms")

# Retrieve with raw vector search
result = orchestrator.retrieve(
    query="How does the system handle peak load?",
    strategy_name="raw",
    k=3
)

print(f"Found {len(result.chunks)} results in {result.latency_ms:.2f}ms")
for chunk, score in zip(result.chunks, result.scores):
    print(f"Score: {score:.4f} - {chunk[:100]}...")
```

### Running Examples

The `examples/` directory contains demonstration scripts:

```bash
# Basic orchestrator demo
python examples/demo_orchestrator.py

# Retrieval strategies comparison
python examples/demo_retrieval_strategies.py

# Query expansion demo
python examples/demo_query_expander.py

# Benchmarking demo
python examples/demo_benchmark.py
```

## Configuration

The system is highly configurable through the `RAGConfig` class:

```python
from src.config import RAGConfig

config = RAGConfig(
    # Embedding settings
    embedding_model="all-MiniLM-L6-v2",
    
    # Vector store settings
    vector_store_type="faiss",  # Options: "faiss", "chromadb", "numpy"
    similarity_metric="cosine",  # Options: "cosine", "euclidean"
    
    # Retrieval settings
    top_k=3,
    
    # Chunking settings
    chunk_size=500,
    chunk_overlap=50,
    
    # Query expansion settings
    expansion_strategy="synonym_addition",  # Options: "synonym_addition", "clarification", "decomposition"
    
    # Benchmark settings
    benchmark_queries=["query1", "query2", "query3"]
)

# Validate configuration
config.validate()
```

### Configuration Options

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `embedding_model` | str | `"all-MiniLM-L6-v2"` | Sentence-transformers model name |
| `vector_store_type` | str | `"faiss"` | Vector store backend: `"faiss"`, `"chromadb"`, or `"numpy"` |
| `similarity_metric` | str | `"cosine"` | Similarity metric: `"cosine"` or `"euclidean"` |
| `top_k` | int | `3` | Number of results to return |
| `chunk_size` | int | `500` | Maximum chunk size in characters |
| `chunk_overlap` | int | `50` | Overlapping characters between chunks |
| `expansion_strategy` | str | `"synonym_addition"` | Query expansion strategy |
| `benchmark_queries` | List[str] | `[]` | Queries for benchmarking |

## Document Ingestion

The ingestion pipeline processes documents through three stages:

1. **Chunking**: Splits documents by paragraphs or fixed size
2. **Embedding**: Generates vector embeddings for each chunk
3. **Storage**: Stores embeddings and text in the vector database

```python
# Ingest with custom chunk size
stats = orchestrator.ingest_documents(
    documents=["doc1", "doc2", "doc3"],
    chunk_size=300  # Smaller chunks for more granular retrieval
)

print(f"Total chunks: {stats.total_chunks}")
print(f"Embedding dimension: {stats.embedding_dimension}")
print(f"Approximate tokens: {stats.total_tokens}")
print(f"Ingestion time: {stats.ingestion_time_ms:.2f}ms")
```

## Retrieval Strategies

### Raw Vector Search

Direct embedding-based similarity search without query modification:

```python
result = orchestrator.retrieve(
    query="What is caching?",
    strategy_name="raw",
    k=3
)

print(f"Query: {result.query}")
print(f"Latency: {result.latency_ms:.2f}ms")
for chunk, score in zip(result.chunks, result.scores):
    print(f"Score: {score:.4f} - {chunk}")
```

### AI-Enhanced Retrieval

Query expansion followed by similarity search:

```python
result = orchestrator.retrieve(
    query="How to improve database performance?",
    strategy_name="enhanced",
    k=3
)

print(f"Original query: {result.query}")
print(f"Expanded query: {result.expanded_query}")
print(f"Latency: {result.latency_ms:.2f}ms")
for chunk, score in zip(result.chunks, result.scores):
    print(f"Score: {score:.4f} - {chunk}")
```

## Benchmarking

Compare retrieval strategies across multiple queries:

```python
from src.benchmark import BenchmarkEngine

# Create benchmark engine
benchmark = BenchmarkEngine(orchestrator)

# Define test queries
queries = [
    "How does the system handle peak load?",
    "What is caching?",
    "How to improve database performance?"
]

# Run benchmark
benchmark.run_benchmark(
    queries=queries,
    output_path="retrieval_benchmark.md"
)

print("Benchmark complete! Results saved to retrieval_benchmark.md")
```

The benchmark generates a detailed Markdown report with:
- Per-query results for both strategies
- Similarity scores for each retrieved chunk
- Average similarity scores
- Result diversity metrics
- Result overlap analysis
- Latency comparisons

## Vector Store Backends

### FAISS (Recommended for Performance)

```python
from src.storage import FAISSVectorStore

vector_store = FAISSVectorStore(
    dimension=384,  # Must match embedding dimension
    similarity_metric="cosine"
)

# Save and load
vector_store.save("vector_store.faiss")
vector_store.load("vector_store.faiss")
```

### ChromaDB (Recommended for Persistence)

```python
from src.storage import ChromaDBVectorStore

vector_store = ChromaDBVectorStore(
    collection_name="rag_collection",
    persist_directory="./chroma_db"
)

# Automatic persistence
```

### NumPy (Recommended for Small Datasets)

```python
from src.storage import NumpyVectorStore

vector_store = NumpyVectorStore(similarity_metric="cosine")

# Save and load
vector_store.save("vector_store.npy")
vector_store.load("vector_store.npy")
```

## Testing

The project includes comprehensive test coverage with property-based tests:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test categories
pytest tests/test_embedding.py
pytest tests/test_retrieval.py
pytest tests/test_orchestrator.py

# Run property-based tests only
pytest -m property
```

## Project Structure

```
context-aware-retrieval-engine/
├── src/
│   ├── embedding.py          # Embedding generation
│   ├── storage.py            # Vector store implementations
│   ├── retrieval.py          # Retrieval strategies
│   ├── mocks.py              # Query expander mock
│   ├── orchestrator.py       # Pipeline orchestration
│   ├── benchmark.py          # Benchmarking engine
│   ├── config.py             # Configuration management
│   └── models.py             # Data models
├── tests/
│   ├── fixtures/             # Test fixtures
│   ├── test_embedding.py     # Embedding tests
│   ├── test_storage.py       # Storage tests
│   ├── test_retrieval.py     # Retrieval tests
│   └── test_orchestrator.py  # Orchestrator tests
├── examples/
│   ├── demo_orchestrator.py  # Complete pipeline demo
│   ├── demo_retrieval_strategies.py
│   ├── demo_query_expander.py
│   └── demo_benchmark.py
├── docs/
│   ├── ARCHITECTURE.md       # Design documentation
│   ├── MIGRATION.md          # Vertex AI migration guide
│   ├── SIMILARITY_METRICS.md # Metric selection guide
│   ├── BENCHMARKING.md       # Benchmarking guide
│   └── API.md                # API reference
├── requirements.txt          # Python dependencies
├── pyproject.toml           # Package configuration
└── README.md                # This file
```

## Documentation

- **[Architecture Guide](docs/ARCHITECTURE.md)**: Component design and data flow
- **[Migration Guide](docs/MIGRATION.md)**: Path to Vertex AI services
- **[Similarity Metrics](docs/SIMILARITY_METRICS.md)**: Choosing the right metric
- **[Benchmarking Guide](docs/BENCHMARKING.md)**: Running and interpreting benchmarks
- **[API Reference](docs/API.md)**: Complete API documentation
- **[Contributing](CONTRIBUTING.md)**: Development guidelines

## Requirements

- Python 3.8+
- sentence-transformers
- faiss-cpu (or faiss-gpu)
- chromadb
- numpy
- hypothesis (for testing)
- pytest (for testing)

See `requirements.txt` for complete dependency list.

## Performance

- **Vector store query latency**: < 1 second for datasets up to 1000 chunks
- **Raw vector search**: < 500ms per query
- **Embedding generation**: ~50ms per chunk (CPU)
- **Memory usage**: ~100MB for 1000 chunks with 384-dimensional embeddings

## Limitations

- **Local-only**: No cloud integration in current version (see Migration Guide)
- **Query expansion**: Rule-based mock, not true LLM-based expansion
- **Scale**: Optimized for datasets up to 10,000 chunks
- **Languages**: English text only (model-dependent)

## Migration to Production

This system is designed as a learning platform and prototype. For production use:

1. **Migrate to Vertex AI Embeddings**: Replace sentence-transformers with Vertex AI Text Embedding API
2. **Use Vertex AI Vector Search**: Replace local vector stores with Matching Engine
3. **Integrate Gemini**: Replace mock query expander with Vertex AI Generative AI
4. **Add authentication**: Implement proper API authentication and authorization
5. **Scale infrastructure**: Use managed services for auto-scaling

See [docs/MIGRATION.md](docs/MIGRATION.md) for detailed migration instructions.

## License

[Your License Here]

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## Support

For issues, questions, or contributions, please open an issue on GitHub.

## Acknowledgments

- Built with [sentence-transformers](https://www.sbert.net/)
- Vector storage powered by [FAISS](https://github.com/facebookresearch/faiss) and [ChromaDB](https://www.trychroma.com/)
- Property-based testing with [Hypothesis](https://hypothesis.readthedocs.io/)
