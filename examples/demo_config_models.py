"""Demo script showing how to use RAGConfig and data models.

This example demonstrates:
1. Creating and validating RAGConfig
2. Using data models (SearchResult, RetrievalResult, etc.)
3. Configuration-based system initialization
"""

from src.config import RAGConfig
from src.models import SearchResult, RetrievalResult, BenchmarkMetrics, IngestionStats


def demo_config_creation():
    """Demonstrate creating and validating configurations."""
    print("=" * 60)
    print("Demo 1: Configuration Creation and Validation")
    print("=" * 60)
    
    # Create default configuration
    print("\n1. Default Configuration:")
    config = RAGConfig()
    print(f"   Embedding Model: {config.embedding_model}")
    print(f"   Vector Store: {config.vector_store_type}")
    print(f"   Similarity Metric: {config.similarity_metric}")
    print(f"   Top-K: {config.top_k}")
    print(f"   Chunk Size: {config.chunk_size}")
    print(f"   Chunk Overlap: {config.chunk_overlap}")
    print(f"   Expansion Strategy: {config.expansion_strategy}")
    
    # Create custom configuration
    print("\n2. Custom Configuration:")
    custom_config = RAGConfig(
        embedding_model="all-MiniLM-L6-v2",
        vector_store_type="chromadb",
        similarity_metric="euclidean",
        top_k=5,
        chunk_size=1000,
        chunk_overlap=100,
        expansion_strategy="clarification",
        benchmark_queries=[
            "How does the system handle peak load?",
            "What are the security features?",
            "How is data stored?"
        ]
    )
    print(f"   Vector Store: {custom_config.vector_store_type}")
    print(f"   Top-K: {custom_config.top_k}")
    print(f"   Chunk Size: {custom_config.chunk_size}")
    print(f"   Benchmark Queries: {len(custom_config.benchmark_queries)} queries")
    
    # Demonstrate validation
    print("\n3. Configuration Validation:")
    try:
        invalid_config = RAGConfig(top_k=-1)
    except ValueError as e:
        print(f"   ✓ Validation caught invalid config: {e}")
    
    print("\n   ✓ Valid configurations pass validation automatically")


def demo_data_models():
    """Demonstrate using data models."""
    print("\n" + "=" * 60)
    print("Demo 2: Data Models Usage")
    print("=" * 60)
    
    # SearchResult
    print("\n1. SearchResult:")
    search_result = SearchResult(
        text="The system handles peak load by scaling horizontally.",
        score=0.87,
        metadata={"chunk_index": 5, "source": "architecture_doc"}
    )
    print(f"   Text: {search_result.text[:50]}...")
    print(f"   Score: {search_result.score}")
    print(f"   Metadata: {search_result.metadata}")
    
    # RetrievalResult
    print("\n2. RetrievalResult:")
    retrieval_result = RetrievalResult(
        query="How does the system handle peak load?",
        expanded_query="How does the system handle peak load? process manage traffic",
        chunks=[
            "The system scales horizontally by adding more nodes.",
            "Load balancing distributes traffic across instances.",
            "Auto-scaling monitors metrics and adjusts capacity."
        ],
        scores=[0.87, 0.82, 0.78],
        latency_ms=45.3,
        strategy_name="AIEnhancedRetrieval"
    )
    print(f"   Query: {retrieval_result.query}")
    print(f"   Expanded: {retrieval_result.expanded_query}")
    print(f"   Retrieved {len(retrieval_result.chunks)} chunks")
    print(f"   Latency: {retrieval_result.latency_ms:.2f} ms")
    print(f"   Strategy: {retrieval_result.strategy_name}")
    
    # IngestionStats
    print("\n3. IngestionStats:")
    ingestion_stats = IngestionStats(
        total_chunks=47,
        embedding_dimension=384,
        total_tokens=5823,
        ingestion_time_ms=1234.5
    )
    print(f"   Total Chunks: {ingestion_stats.total_chunks}")
    print(f"   Embedding Dimension: {ingestion_stats.embedding_dimension}")
    print(f"   Total Tokens: {ingestion_stats.total_tokens}")
    print(f"   Ingestion Time: {ingestion_stats.ingestion_time_ms:.2f} ms")
    
    # BenchmarkMetrics
    print("\n4. BenchmarkMetrics:")
    benchmark_metrics = BenchmarkMetrics(
        strategy_name="RawVectorSearch",
        avg_similarity_score=0.78,
        unique_chunks_retrieved=12,
        avg_latency_ms=38.5,
        query_results=[retrieval_result]
    )
    print(f"   Strategy: {benchmark_metrics.strategy_name}")
    print(f"   Avg Similarity: {benchmark_metrics.avg_similarity_score:.4f}")
    print(f"   Unique Chunks: {benchmark_metrics.unique_chunks_retrieved}")
    print(f"   Avg Latency: {benchmark_metrics.avg_latency_ms:.2f} ms")
    print(f"   Query Results: {len(benchmark_metrics.query_results)}")


def demo_config_based_initialization():
    """Demonstrate using config for system initialization."""
    print("\n" + "=" * 60)
    print("Demo 3: Configuration-Based System Initialization")
    print("=" * 60)
    
    # Create configuration
    config = RAGConfig(
        embedding_model="all-MiniLM-L6-v2",
        vector_store_type="numpy",
        similarity_metric="cosine",
        top_k=3,
        chunk_size=500,
        chunk_overlap=50,
        expansion_strategy="synonym_addition"
    )
    
    print("\n1. Configuration Settings:")
    print(f"   Embedding Model: {config.embedding_model}")
    print(f"   Vector Store: {config.vector_store_type}")
    print(f"   Similarity Metric: {config.similarity_metric}")
    print(f"   Top-K: {config.top_k}")
    
    print("\n2. System would be initialized with these settings:")
    print(f"   ✓ EmbeddingGenerator(model_name='{config.embedding_model}')")
    print(f"   ✓ {config.vector_store_type.upper()}VectorStore(similarity_metric='{config.similarity_metric}')")
    print(f"   ✓ QueryExpander(expansion_strategy='{config.expansion_strategy}')")
    print(f"   ✓ Retrieval strategies configured with top_k={config.top_k}")
    
    print("\n3. Document ingestion would use:")
    print(f"   ✓ chunk_size={config.chunk_size} characters")
    print(f"   ✓ chunk_overlap={config.chunk_overlap} characters")


def demo_model_interoperability():
    """Demonstrate how models work together."""
    print("\n" + "=" * 60)
    print("Demo 4: Model Interoperability")
    print("=" * 60)
    
    # Create search results
    print("\n1. Creating SearchResults from vector store:")
    search_results = [
        SearchResult(text=f"Chunk {i}", score=0.9 - i * 0.1, metadata={"idx": i})
        for i in range(3)
    ]
    print(f"   Created {len(search_results)} search results")
    
    # Convert to RetrievalResult
    print("\n2. Converting to RetrievalResult:")
    retrieval_result = RetrievalResult(
        query="Test query",
        expanded_query=None,
        chunks=[r.text for r in search_results],
        scores=[r.score for r in search_results],
        latency_ms=30.0,
        strategy_name="RawVectorSearch"
    )
    print(f"   Query: {retrieval_result.query}")
    print(f"   Chunks: {retrieval_result.chunks}")
    print(f"   Scores: {retrieval_result.scores}")
    
    # Aggregate into BenchmarkMetrics
    print("\n3. Aggregating into BenchmarkMetrics:")
    all_scores = [score for score in retrieval_result.scores]
    avg_score = sum(all_scores) / len(all_scores)
    
    metrics = BenchmarkMetrics(
        strategy_name="RawVectorSearch",
        avg_similarity_score=avg_score,
        unique_chunks_retrieved=len(set(retrieval_result.chunks)),
        avg_latency_ms=retrieval_result.latency_ms,
        query_results=[retrieval_result]
    )
    print(f"   Strategy: {metrics.strategy_name}")
    print(f"   Avg Score: {metrics.avg_similarity_score:.4f}")
    print(f"   Unique Chunks: {metrics.unique_chunks_retrieved}")


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("RAGConfig and Data Models Demo")
    print("=" * 60)
    
    demo_config_creation()
    demo_data_models()
    demo_config_based_initialization()
    demo_model_interoperability()
    
    print("\n" + "=" * 60)
    print("Demo Complete!")
    print("=" * 60)
    print("\nKey Takeaways:")
    print("1. RAGConfig provides centralized configuration with validation")
    print("2. Data models provide type-safe data structures")
    print("3. Models work together seamlessly in the pipeline")
    print("4. Configuration enables easy system customization")
    print("=" * 60 + "\n")
