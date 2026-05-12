# Architecture Documentation

## Overview

The Context-Aware Retrieval Engine is a modular RAG (Retrieval-Augmented Generation) pipeline designed with local-first principles and cloud migration in mind. This document describes the system architecture, component design, data flow, and design patterns used throughout the implementation.

## Table of Contents

- [System Architecture](#system-architecture)
- [Component Design](#component-design)
- [Data Flow](#data-flow)
- [Design Patterns](#design-patterns)
- [Module Interfaces](#module-interfaces)
- [Data Models](#data-models)
- [Error Handling Strategy](#error-handling-strategy)

## System Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     RAG Orchestrator                            │
│  (Coordinates ingestion and retrieval pipeline)                │
└────────────┬────────────────────────────────────┬───────────────┘
             │                                    │
             │                                    │
    ┌────────▼────────┐                  ┌───────▼────────┐
    │  Ingestion      │                  │   Retrieval    │
    │  Pipeline       │                  │   Pipeline     │
    └────────┬────────┘                  └───────┬────────┘
             │                                    │
             │                                    │
    ┌────────▼────────┐                  ┌───────▼────────┐
    │  Text Chunker   │                  │   Strategy     │
    │                 │                  │   Router       │
    └────────┬────────┘                  └───────┬────────┘
             │                                    │
             │                           ┌────────┴────────┐
    ┌────────▼────────┐                  │                 │
    │   Embedding     │◄─────────────────┤  Raw Vector    │
    │   Generator     │                  │  Search         │
    └────────┬────────┘                  │                 │
             │                           └─────────────────┘
             │                                    │
    ┌────────▼────────┐                  ┌───────▼────────┐
    │  Vector Store   │◄─────────────────┤  AI-Enhanced   │
    │  (FAISS/Chroma/ │                  │  Retrieval     │
    │   NumPy)        │                  │                 │
    └─────────────────┘                  └────────┬────────┘
                                                  │
                                         ┌────────▼────────┐
                                         │  Query Expander │
                                         │  (Mock)         │
                                         └─────────────────┘
```

### Component Layers

The system is organized into three logical layers:

1. **Orchestration Layer** (`orchestrator.py`)
   - Manages component lifecycle
   - Coordinates ingestion and retrieval workflows
   - Provides unified API for system interaction

2. **Core Components Layer**
   - **Embedding Generator** (`embedding.py`): Text-to-vector conversion
   - **Vector Store** (`storage.py`): Vector storage and similarity search
   - **Retrieval Strategies** (`retrieval.py`): Query execution strategies
   - **Query Expander** (`mocks.py`): Query enhancement (mock)

3. **Support Layer**
   - **Configuration** (`config.py`): System configuration management
   - **Data Models** (`models.py`): Shared data structures
   - **Benchmark Engine** (`benchmark.py`): Strategy comparison

## Component Design

### 1. Embedding Generator

**Purpose**: Convert text into dense vector representations using sentence-transformers.

**Key Responsibilities**:
- Load and manage sentence-transformers model
- Generate embeddings for single or batch text inputs
- Provide embedding dimensionality information
- Handle encoding errors gracefully

**Interface**:
```python
class EmbeddingGenerator:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2")
    def encode(self, texts: Union[str, List[str]]) -> np.ndarray
    def get_embedding_dimension(self) -> int
```

**Design Decisions**:
- Uses sentence-transformers for local execution (no API dependencies)
- Supports both single and batch encoding for flexibility
- Interface mirrors Vertex AI TextEmbeddingModel for easy migration
- Model loaded once at initialization for performance

### 2. Vector Store

**Purpose**: Store and retrieve embeddings with associated text using similarity search.

**Key Responsibilities**:
- Store embeddings with text and metadata
- Perform k-nearest neighbor similarity search
- Persist and load vector indices
- Support multiple backend implementations (FAISS, ChromaDB, NumPy)

**Interface**:
```python
class VectorStore(ABC):
    @abstractmethod
    def add(self, embeddings: np.ndarray, texts: List[str], 
            metadata: Optional[List[Dict]] = None)
    
    @abstractmethod
    def search(self, query_embedding: np.ndarray, k: int = 3) -> List[SearchResult]
    
    @abstractmethod
    def save(self, path: str)
    
    @abstractmethod
    def load(self, path: str)
```

**Implementations**:

1. **FAISSVectorStore**: High-performance in-memory search
   - Uses `IndexFlatIP` for cosine similarity (with L2 normalization)
   - Best for: Speed-critical applications, large datasets
   - Persistence: Separate index and metadata files

2. **ChromaDBVectorStore**: Developer-friendly with built-in persistence
   - Automatic persistence to disk
   - Best for: Development, prototyping, small-to-medium datasets
   - Persistence: Automatic to specified directory

3. **NumpyVectorStore**: Simple NumPy-based implementation
   - Pure NumPy operations for similarity search
   - Best for: Small datasets, educational purposes, minimal dependencies
   - Persistence: NumPy save/load format

**Design Decisions**:
- Abstract base class enables backend swapping without code changes
- Similarity metric configurable (cosine vs. Euclidean)
- Metadata support for tracking source documents
- Consistent interface across all implementations

### 3. Retrieval Strategies

**Purpose**: Execute different retrieval approaches with a common interface.

**Key Responsibilities**:
- Generate query embeddings
- Execute similarity search
- Measure and report latency
- Return structured results

**Interface**:
```python
class RetrievalStrategy(ABC):
    @abstractmethod
    def retrieve(self, query: str, k: int = 3) -> RetrievalResult
```

**Implementations**:

1. **RawVectorSearch**: Direct embedding-based search
   - Query → Embedding → Similarity Search → Results
   - No query modification
   - Fastest execution time
   - Best for: Well-formed queries, known terminology

2. **AIEnhancedRetrieval**: Query expansion + search
   - Query → Expansion → Embedding → Similarity Search → Results
   - Uses QueryExpander to enhance query
   - Captures both original and expanded queries
   - Best for: Ambiguous queries, exploratory search

**Design Decisions**:
- Strategy pattern enables easy addition of new retrieval approaches
- Dependency injection for testability
- Latency measurement built into each strategy
- Results include full context (query, scores, metadata)

### 4. Query Expander (Mock)

**Purpose**: Simulate Vertex AI GenerativeModel for query enhancement.

**Key Responsibilities**:
- Expand queries using rule-based logic
- Log all interactions for debugging
- Support multiple expansion strategies
- Mirror Vertex AI interface for migration

**Interface**:
```python
class QueryExpander:
    def __init__(self, expansion_strategy: str = "synonym_addition")
    def expand_query(self, query: str) -> str
    def get_interaction_log(self) -> List[Dict]
```

**Expansion Strategies**:
1. **synonym_addition**: Add synonyms for key terms
2. **clarification**: Add clarifying context
3. **decomposition**: Break complex queries into sub-queries

**Design Decisions**:
- Rule-based implementation for local execution
- Interface matches Vertex AI GenerativeModel
- Interaction logging for debugging and analysis
- Configurable strategies for experimentation

### 5. RAG Orchestrator

**Purpose**: Coordinate the complete ingestion and retrieval pipeline.

**Key Responsibilities**:
- Manage component lifecycle
- Execute document ingestion (chunk → embed → store)
- Route queries to appropriate strategies
- Track system statistics
- Provide unified API

**Interface**:
```python
class RAGOrchestrator:
    def __init__(self, embedding_generator: EmbeddingGenerator,
                 vector_store: VectorStore,
                 strategies: Dict[str, RetrievalStrategy])
    
    def ingest_documents(self, documents: List[str], 
                        chunk_size: int = 500) -> IngestionStats
    
    def retrieve(self, query: str, strategy_name: str, 
                k: int = 3) -> RetrievalResult
    
    def get_statistics(self) -> Dict
```

**Design Decisions**:
- Dependency injection for all components
- Flexible strategy registration via dictionary
- Automatic chunking with paragraph detection
- Statistics tracking for monitoring
- Clear error messages for unknown strategies

### 6. Benchmark Engine

**Purpose**: Compare retrieval strategies across multiple queries.

**Key Responsibilities**:
- Execute queries against multiple strategies
- Collect results, scores, and latency
- Calculate quality metrics (similarity, diversity, overlap)
- Generate structured comparison reports

**Interface**:
```python
class BenchmarkEngine:
    def __init__(self, orchestrator: RAGOrchestrator)
    
    def run_benchmark(self, queries: List[str], 
                     output_path: str = "retrieval_benchmark.md")
    
    def calculate_metrics(self, results: Dict) -> BenchmarkMetrics
```

**Metrics Calculated**:
- Average similarity score per strategy
- Unique chunks retrieved (diversity)
- Overlapping chunks (consistency)
- Average latency per strategy

**Design Decisions**:
- Markdown output for human readability
- Structured metrics for programmatic analysis
- Graceful handling of strategy failures
- Per-query and aggregate metrics

## Data Flow

### Ingestion Pipeline

```
┌──────────────┐
│   Raw Text   │
│  Documents   │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│    Chunk     │  Split by paragraphs or fixed size
│  Documents   │  with overlap
└──────┬───────┘
       │
       ▼
┌──────────────┐
│   Generate   │  sentence-transformers
│  Embeddings  │  (384-dim vectors)
└──────┬───────┘
       │
       ▼
┌──────────────┐
│    Store     │  FAISS/ChromaDB/NumPy
│  Embeddings  │  with text & metadata
└──────────────┘
```

**Data Transformations**:
1. **Text → Chunks**: Documents split into manageable pieces
2. **Chunks → Embeddings**: Text converted to 384-dimensional vectors
3. **Embeddings → Storage**: Vectors indexed for fast similarity search

### Retrieval Pipeline (Raw Vector Search)

```
┌──────────────┐
│  User Query  │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│   Generate   │  sentence-transformers
│   Query      │  (384-dim vector)
│  Embedding   │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│  Similarity  │  Cosine similarity
│    Search    │  (top-k results)
└──────┬───────┘
       │
       ▼
┌──────────────┐
│   Return     │  Chunks + scores
│   Results    │  + metadata
└──────────────┘
```

### Retrieval Pipeline (AI-Enhanced)

```
┌──────────────┐
│  User Query  │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│    Expand    │  Add synonyms,
│    Query     │  clarifications
└──────┬───────┘
       │
       ▼
┌──────────────┐
│   Generate   │  sentence-transformers
│   Expanded   │  (384-dim vector)
│  Embedding   │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│  Similarity  │  Cosine similarity
│    Search    │  (top-k results)
└──────┬───────┘
       │
       ▼
┌──────────────┐
│   Return     │  Chunks + scores
│   Results    │  + both queries
└──────────────┘
```

## Design Patterns

### 1. Strategy Pattern

**Used in**: Retrieval strategies

**Purpose**: Enable interchangeable retrieval algorithms

**Implementation**:
```python
class RetrievalStrategy(ABC):
    @abstractmethod
    def retrieve(self, query: str, k: int) -> RetrievalResult:
        pass

# Concrete strategies
class RawVectorSearch(RetrievalStrategy): ...
class AIEnhancedRetrieval(RetrievalStrategy): ...

# Usage
orchestrator = RAGOrchestrator(
    strategies={
        "raw": RawVectorSearch(...),
        "enhanced": AIEnhancedRetrieval(...)
    }
)
```

**Benefits**:
- Easy to add new retrieval strategies
- Strategies can be selected at runtime
- Consistent interface for all strategies

### 2. Dependency Injection

**Used in**: All major components

**Purpose**: Enable testability and flexibility

**Implementation**:
```python
class RAGOrchestrator:
    def __init__(self, 
                 embedding_generator: EmbeddingGenerator,
                 vector_store: VectorStore,
                 strategies: Dict[str, RetrievalStrategy]):
        self.embedding_generator = embedding_generator
        self.vector_store = vector_store
        self.strategies = strategies
```

**Benefits**:
- Easy to mock components for testing
- Components can be swapped without code changes
- Clear dependencies visible in constructor

### 3. Adapter Pattern

**Used in**: Mock components (QueryExpander, EmbeddingGenerator)

**Purpose**: Match Vertex AI interfaces for easy migration

**Implementation**:
```python
# Local implementation with Vertex AI-compatible interface
class QueryExpander:
    def expand_query(self, query: str) -> str:
        # Rule-based logic
        pass

# Future Vertex AI implementation
class VertexAIQueryExpander:
    def expand_query(self, query: str) -> str:
        # Call Vertex AI API
        pass
```

**Benefits**:
- Smooth migration path to cloud services
- Can test with mocks, deploy with real services
- Interface compatibility verified early

### 4. Factory Pattern

**Used in**: Vector store creation (implicit)

**Purpose**: Create appropriate vector store based on configuration

**Potential Implementation**:
```python
class VectorStoreFactory:
    @staticmethod
    def create(config: RAGConfig) -> VectorStore:
        if config.vector_store_type == "faiss":
            return FAISSVectorStore(...)
        elif config.vector_store_type == "chromadb":
            return ChromaDBVectorStore(...)
        elif config.vector_store_type == "numpy":
            return NumpyVectorStore(...)
```

**Benefits**:
- Centralized creation logic
- Easy to add new vector store types
- Configuration-driven instantiation

## Module Interfaces

### Embedding Generator

```python
class EmbeddingGenerator:
    """Generates vector embeddings from text."""
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """Initialize with sentence-transformers model."""
        
    def encode(self, texts: Union[str, List[str]]) -> np.ndarray:
        """Generate embeddings for text(s).
        
        Args:
            texts: Single string or list of strings
            
        Returns:
            numpy array of shape (n, embedding_dim)
        """
        
    def get_embedding_dimension(self) -> int:
        """Return embedding dimensionality."""
```

### Vector Store

```python
class VectorStore(ABC):
    """Abstract interface for vector storage."""
    
    @abstractmethod
    def add(self, embeddings: np.ndarray, texts: List[str], 
            metadata: Optional[List[Dict]] = None):
        """Store embeddings with text and metadata."""
        
    @abstractmethod
    def search(self, query_embedding: np.ndarray, k: int = 3) -> List[SearchResult]:
        """Find k most similar embeddings."""
        
    @abstractmethod
    def save(self, path: str):
        """Persist to disk."""
        
    @abstractmethod
    def load(self, path: str):
        """Load from disk."""
```

### Retrieval Strategy

```python
class RetrievalStrategy(ABC):
    """Abstract interface for retrieval strategies."""
    
    @abstractmethod
    def retrieve(self, query: str, k: int = 3) -> RetrievalResult:
        """Execute retrieval strategy.
        
        Returns:
            RetrievalResult with chunks, scores, and metadata
        """
```

### Orchestrator

```python
class RAGOrchestrator:
    """Coordinates ingestion and retrieval."""
    
    def __init__(self, embedding_generator: EmbeddingGenerator,
                 vector_store: VectorStore,
                 strategies: Dict[str, RetrievalStrategy]):
        """Initialize with dependencies."""
        
    def ingest_documents(self, documents: List[str], 
                        chunk_size: int = 500) -> IngestionStats:
        """Process documents through ingestion pipeline."""
        
    def retrieve(self, query: str, strategy_name: str, 
                k: int = 3) -> RetrievalResult:
        """Execute retrieval using specified strategy."""
        
    def get_statistics(self) -> Dict:
        """Return system statistics."""
```

## Data Models

### SearchResult

```python
@dataclass
class SearchResult:
    """Single search result from vector store."""
    text: str                    # Original text chunk
    score: float                 # Similarity score
    metadata: Optional[Dict]     # Additional metadata
```

### RetrievalResult

```python
@dataclass
class RetrievalResult:
    """Complete retrieval result."""
    query: str                   # Original query
    expanded_query: Optional[str] # Expanded query (if applicable)
    chunks: List[str]            # Retrieved text chunks
    scores: List[float]          # Similarity scores
    latency_ms: float            # Retrieval latency
    strategy_name: str           # Strategy used
```

### IngestionStats

```python
@dataclass
class IngestionStats:
    """Statistics from document ingestion."""
    total_chunks: int            # Number of chunks created
    embedding_dimension: int     # Embedding dimensionality
    total_tokens: int            # Approximate token count
    ingestion_time_ms: float     # Processing time
```

### BenchmarkMetrics

```python
@dataclass
class BenchmarkMetrics:
    """Aggregated benchmark results."""
    strategy_name: str           # Strategy being evaluated
    avg_similarity_score: float  # Average similarity
    unique_chunks_retrieved: int # Diversity metric
    avg_latency_ms: float        # Average latency
    query_results: List[RetrievalResult]  # Individual results
```

## Error Handling Strategy

### Principles

1. **Fail Fast**: Validate inputs early and raise clear exceptions
2. **Graceful Degradation**: Return partial results when possible
3. **Detailed Logging**: Log errors with context for debugging
4. **User-Friendly Messages**: Include actionable suggestions

### Error Categories

#### 1. Input Validation Errors

**When**: Invalid user inputs (empty queries, negative k values)

**Handling**: Raise `ValueError` with descriptive message

```python
if not query or not query.strip():
    raise ValueError("Query cannot be empty")

if k <= 0:
    raise ValueError(f"k must be positive, got {k}")
```

#### 2. Component Errors

**When**: Component failures (model loading, storage errors)

**Handling**: Raise specific exceptions with recovery suggestions

```python
try:
    self.model = SentenceTransformer(model_name)
except Exception as e:
    raise ModelNotFoundError(
        f"Failed to load model '{model_name}'. "
        f"Available models: {AVAILABLE_MODELS}"
    ) from e
```

#### 3. Strategy Errors

**When**: Unknown strategy names, strategy execution failures

**Handling**: Raise `StrategyNotFoundError` with available options

```python
if strategy_name not in self.strategies:
    available = ", ".join(self.strategies.keys())
    raise StrategyNotFoundError(
        f"Unknown strategy '{strategy_name}'. "
        f"Available: {available}"
    )
```

#### 4. Storage Errors

**When**: Dimension mismatches, persistence failures

**Handling**: Raise specific exceptions with diagnostic information

```python
if embeddings.shape[1] != self.dimension:
    raise DimensionMismatchError(
        f"Expected dimension {self.dimension}, "
        f"got {embeddings.shape[1]}"
    )
```

### Recovery Strategies

1. **Empty Store**: Return empty results with warning
2. **Partial Failures**: Log errors, continue with valid items
3. **Fallback**: If enhanced retrieval fails, fall back to raw search
4. **Retry**: Retry transient failures with exponential backoff

## Performance Considerations

### Latency Targets

- **Vector store query**: < 1 second for 1000 chunks
- **Raw vector search**: < 500ms per query
- **Embedding generation**: ~50ms per chunk (CPU)

### Memory Usage

- **Embeddings**: ~1.5KB per chunk (384 dimensions × 4 bytes)
- **1000 chunks**: ~1.5MB for embeddings + text storage
- **Model**: ~80MB for all-MiniLM-L6-v2

### Optimization Strategies

1. **Batch Processing**: Process multiple texts in single embedding call
2. **Index Optimization**: Use FAISS for large datasets
3. **Caching**: Cache frequently accessed embeddings
4. **Lazy Loading**: Load models only when needed

## Testing Architecture

### Test Layers

1. **Unit Tests**: Individual component testing
2. **Integration Tests**: End-to-end pipeline testing
3. **Property Tests**: Universal correctness properties
4. **Performance Tests**: Latency and throughput validation

### Test Coverage Goals

- Overall: ≥ 80%
- Critical paths: 100%
- Property tests: All 26 properties
- Edge cases: All identified scenarios

## Future Enhancements

### Potential Improvements

1. **Hybrid Search**: Combine vector and keyword search
2. **Reranking**: Add reranking stage for improved relevance
3. **Caching**: Cache embeddings and query results
4. **Async Operations**: Async API for better concurrency
5. **Streaming**: Stream results for large result sets

### Migration Path

See [MIGRATION.md](MIGRATION.md) for detailed cloud migration guide.

## References

- [Sentence-Transformers Documentation](https://www.sbert.net/)
- [FAISS Documentation](https://github.com/facebookresearch/faiss/wiki)
- [ChromaDB Documentation](https://docs.trychroma.com/)
- [Vertex AI Documentation](https://cloud.google.com/vertex-ai/docs)
