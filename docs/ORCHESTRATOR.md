# RAGOrchestrator Module

## Overview

The `RAGOrchestrator` is the central coordination component of the Context-Aware Retrieval Engine. It manages the complete RAG pipeline, from document ingestion to retrieval execution, providing a unified interface for all retrieval operations.

## Architecture

The orchestrator follows the **Coordinator Pattern**, managing interactions between:
- **Embedding Generator**: Converts text to vector embeddings
- **Vector Store**: Stores and retrieves embeddings
- **Retrieval Strategies**: Executes different retrieval approaches

## Key Features

### 1. Document Ingestion Pipeline

The orchestrator processes documents through a multi-stage pipeline:

```python
orchestrator.ingest_documents(documents, chunk_size=500)
```

**Pipeline stages:**
1. **Chunking**: Splits documents by paragraphs or fixed size
2. **Embedding Generation**: Creates vector embeddings for each chunk
3. **Storage**: Persists embeddings with metadata in vector store
4. **Statistics Tracking**: Records ingestion metrics

**Chunking Strategy:**
- Primary: Split by double newlines (paragraphs)
- Fallback: Split by single newlines
- Large paragraphs: Split into fixed-size chunks with 10% overlap
- Word boundary preservation: Breaks at spaces when possible

### 2. Retrieval Coordination

Routes queries to appropriate retrieval strategies:

```python
result = orchestrator.retrieve(query, strategy_name="raw", k=3)
```

**Features:**
- Strategy selection by name
- Consistent interface across strategies
- Error handling for unknown strategies
- Configurable result count (k)

### 3. Statistics and Monitoring

Provides system-wide statistics:

```python
stats = orchestrator.get_statistics()
# Returns: {
#   "total_chunks": 18,
#   "embedding_dimension": 384,
#   "available_strategies": ["raw", "enhanced"]
# }
```

## Usage Examples

### Basic Usage

```python
from src.embedding import EmbeddingGenerator
from src.storage import NumpyVectorStore
from src.retrieval import RawVectorSearch, AIEnhancedRetrieval
from src.mocks import QueryExpander
from src.orchestrator import RAGOrchestrator

# Initialize components
embedding_generator = EmbeddingGenerator()
vector_store = NumpyVectorStore()

# Create strategies
raw_strategy = RawVectorSearch(embedding_generator, vector_store)
query_expander = QueryExpander()
enhanced_strategy = AIEnhancedRetrieval(
    embedding_generator, vector_store, query_expander
)

# Create orchestrator
orchestrator = RAGOrchestrator(
    embedding_generator,
    vector_store,
    strategies={"raw": raw_strategy, "enhanced": enhanced_strategy}
)

# Ingest documents
documents = [
    "Python is a programming language.",
    "Machine learning uses algorithms."
]
stats = orchestrator.ingest_documents(documents, chunk_size=500)

# Retrieve results
result = orchestrator.retrieve("programming", strategy_name="raw", k=3)
```

### Advanced Usage

```python
# Custom chunk size for fine-grained control
stats = orchestrator.ingest_documents(documents, chunk_size=200)

# Multiple ingestion cycles
orchestrator.ingest_documents(batch1, chunk_size=500)
orchestrator.ingest_documents(batch2, chunk_size=500)

# Strategy comparison
raw_result = orchestrator.retrieve(query, strategy_name="raw", k=3)
enhanced_result = orchestrator.retrieve(query, strategy_name="enhanced", k=3)

# Monitor system state
stats = orchestrator.get_statistics()
print(f"Total chunks: {stats['total_chunks']}")
```

## Data Models

### IngestionStats

Returned by `ingest_documents()`:

```python
@dataclass
class IngestionStats:
    total_chunks: int           # Number of chunks created
    embedding_dimension: int    # Dimensionality of embeddings
    total_tokens: int          # Approximate token count
    ingestion_time_ms: float   # Ingestion time in milliseconds
```

### RetrievalResult

Returned by `retrieve()`:

```python
@dataclass
class RetrievalResult:
    query: str                      # Original query
    expanded_query: Optional[str]   # Expanded query (if applicable)
    chunks: List[str]              # Retrieved text chunks
    scores: List[float]            # Similarity scores
    latency_ms: float              # Retrieval latency
    strategy_name: str             # Strategy used
```

## Error Handling

### StrategyNotFoundError

Raised when requesting an unknown strategy:

```python
try:
    result = orchestrator.retrieve(query, strategy_name="unknown", k=3)
except StrategyNotFoundError as e:
    print(f"Error: {e}")
    # Error: Unknown strategy 'unknown'. Available strategies: raw, enhanced
```

### ValueError

Raised for invalid inputs:

```python
# Empty documents list
orchestrator.ingest_documents([], chunk_size=500)
# ValueError: Documents list cannot be empty.

# Invalid chunk size
orchestrator.ingest_documents(documents, chunk_size=0)
# ValueError: chunk_size must be positive, got 0

# Empty query
orchestrator.retrieve("", strategy_name="raw", k=3)
# ValueError: Query must be a non-empty string.
```

## Performance Characteristics

### Ingestion Performance

- **Chunking**: O(n) where n is total document length
- **Embedding Generation**: Depends on model and batch size
- **Storage**: O(m) where m is number of chunks

**Typical metrics** (5 documents, ~1300 words):
- Total chunks: 18
- Ingestion time: ~240ms
- Embedding dimension: 384

### Retrieval Performance

- **Raw Vector Search**: ~45ms for 18 chunks
- **AI-Enhanced Retrieval**: ~34ms for 18 chunks (includes query expansion)

Performance scales with:
- Number of stored chunks
- Vector store implementation (FAISS > ChromaDB > NumPy)
- Embedding dimension

## Design Patterns

### Dependency Injection

All components are injected via constructor:

```python
orchestrator = RAGOrchestrator(
    embedding_generator=embedding_generator,
    vector_store=vector_store,
    strategies=strategies
)
```

**Benefits:**
- Testability: Easy to mock components
- Flexibility: Swap implementations without code changes
- Clarity: Explicit dependencies

### Strategy Pattern

Retrieval strategies implement common interface:

```python
class RetrievalStrategy(ABC):
    @abstractmethod
    def retrieve(self, query: str, k: int) -> RetrievalResult:
        pass
```

**Benefits:**
- Extensibility: Add new strategies without modifying orchestrator
- Consistency: All strategies have same interface
- Comparison: Easy to benchmark different approaches

## Testing

The orchestrator has comprehensive test coverage (98%):

### Test Categories

1. **Initialization Tests**: Verify proper setup and validation
2. **Ingestion Tests**: Test chunking, embedding, and storage
3. **Retrieval Tests**: Verify strategy routing and execution
4. **Statistics Tests**: Ensure accurate metric tracking
5. **Chunking Tests**: Validate text splitting logic
6. **Integration Tests**: End-to-end pipeline verification

### Running Tests

```bash
# Run all orchestrator tests
pytest tests/test_orchestrator.py -v

# Run specific test class
pytest tests/test_orchestrator.py::TestDocumentIngestion -v

# Run with coverage
pytest tests/test_orchestrator.py --cov=src.orchestrator
```

## Integration with Other Components

### Embedding Generator

```python
# Orchestrator uses embedding generator for:
# 1. Getting embedding dimension
dimension = embedding_generator.get_embedding_dimension()

# 2. Encoding text chunks
embeddings = embedding_generator.encode(chunks)
```

### Vector Store

```python
# Orchestrator uses vector store for:
# 1. Storing embeddings with metadata
vector_store.add(embeddings, texts, metadata)

# 2. Retrieval (delegated to strategies)
# Strategies call vector_store.search(query_embedding, k)
```

### Retrieval Strategies

```python
# Orchestrator delegates retrieval to strategies:
strategy = strategies[strategy_name]
result = strategy.retrieve(query, k)
```

## Best Practices

### Chunk Size Selection

- **Small chunks (200-300)**: Better precision, more chunks
- **Medium chunks (400-600)**: Balanced approach (recommended)
- **Large chunks (800-1000)**: Better context, fewer chunks

### Strategy Selection

- **Raw Vector Search**: Fast, direct semantic matching
- **AI-Enhanced Retrieval**: Better for complex queries, handles ambiguity

### Error Handling

Always handle potential errors:

```python
try:
    stats = orchestrator.ingest_documents(documents, chunk_size=500)
    result = orchestrator.retrieve(query, strategy_name="raw", k=3)
except ValueError as e:
    print(f"Invalid input: {e}")
except StrategyNotFoundError as e:
    print(f"Strategy error: {e}")
```

## Future Enhancements

Potential improvements for production use:

1. **Batch Ingestion**: Process large document sets in batches
2. **Incremental Updates**: Add/remove individual documents
3. **Persistence**: Save/load orchestrator state
4. **Async Operations**: Non-blocking ingestion and retrieval
5. **Caching**: Cache frequently accessed embeddings
6. **Monitoring**: Detailed performance metrics and logging

## References

- [Requirements Document](../specs/context-aware-retrieval-engine/requirements.md)
- [Design Document](../specs/context-aware-retrieval-engine/design.md)
- [Implementation Tasks](../specs/context-aware-retrieval-engine/tasks.md)
- [Demo Script](../examples/demo_orchestrator.py)
