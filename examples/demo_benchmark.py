"""Demo script for the Benchmark Engine.

This script demonstrates how to use the BenchmarkEngine to compare
retrieval strategies across a set of queries.
"""

from src.embedding import EmbeddingGenerator
from src.storage import NumpyVectorStore
from src.retrieval import RawVectorSearch, AIEnhancedRetrieval
from src.mocks import QueryExpander
from src.orchestrator import RAGOrchestrator
from src.benchmark import BenchmarkEngine


def main():
    """Run benchmark demo."""
    print("=" * 80)
    print("Benchmark Engine Demo")
    print("=" * 80)
    print()
    
    # Initialize components
    print("1. Initializing components...")
    embedding_generator = EmbeddingGenerator(model_name="all-MiniLM-L6-v2")
    vector_store = NumpyVectorStore(similarity_metric="cosine")
    query_expander = QueryExpander(expansion_strategy="synonym_addition")
    
    # Create retrieval strategies
    raw_search = RawVectorSearch(embedding_generator, vector_store)
    enhanced_search = AIEnhancedRetrieval(embedding_generator, vector_store, query_expander)
    
    strategies = {
        "raw": raw_search,
        "enhanced": enhanced_search
    }
    
    # Create orchestrator
    orchestrator = RAGOrchestrator(embedding_generator, vector_store, strategies)
    print("   ✓ Components initialized")
    print()
    
    # Ingest sample documents
    print("2. Ingesting sample documents...")
    documents = [
        """Microservices architecture is a design pattern where applications are composed 
        of small, independent services that communicate over well-defined APIs. Each service 
        is responsible for a specific business capability and can be developed, deployed, 
        and scaled independently.""",
        
        """Event-driven architecture is a software design pattern where system components 
        communicate by producing and consuming events. Events represent state changes or 
        significant occurrences in the system. This pattern enables loose coupling and 
        asynchronous communication between services.""",
        
        """Domain-Driven Design (DDD) is an approach to software development that emphasizes 
        collaboration between technical experts and domain experts. It focuses on creating 
        a shared understanding of the business domain through ubiquitous language and 
        bounded contexts.""",
        
        """CQRS (Command Query Responsibility Segregation) is a pattern that separates read 
        and write operations into different models. Commands modify state, while queries 
        retrieve data. This separation allows for optimized data models and improved 
        scalability.""",
        
        """API Gateway is a server that acts as an entry point for client requests to 
        backend services. It handles request routing, composition, protocol translation, 
        and cross-cutting concerns like authentication, rate limiting, and monitoring."""
    ]
    
    stats = orchestrator.ingest_documents(documents, chunk_size=500)
    print(f"   ✓ Ingested {stats.total_chunks} chunks")
    print(f"   ✓ Embedding dimension: {stats.embedding_dimension}")
    print(f"   ✓ Ingestion time: {stats.ingestion_time_ms:.2f} ms")
    print()
    
    # Define benchmark queries
    print("3. Defining benchmark queries...")
    queries = [
        "How do microservices communicate?",
        "What is the difference between commands and queries?",
        "How does an API Gateway work?"
    ]
    
    for i, query in enumerate(queries, 1):
        print(f"   Query {i}: \"{query}\"")
    print()
    
    # Create benchmark engine
    print("4. Running benchmark...")
    benchmark_engine = BenchmarkEngine(orchestrator)
    
    # Run benchmark
    metrics = benchmark_engine.run_benchmark(
        queries=queries,
        output_path="retrieval_benchmark.md"
    )
    print("   ✓ Benchmark completed")
    print()
    
    # Display results
    print("5. Benchmark Results:")
    print()
    print("-" * 80)
    print(f"{'Strategy':<20} {'Avg Similarity':<20} {'Unique Chunks':<20} {'Avg Latency (ms)':<20}")
    print("-" * 80)
    
    for strategy_name, strategy_metrics in metrics.items():
        print(
            f"{strategy_name:<20} "
            f"{strategy_metrics.avg_similarity_score:<20.4f} "
            f"{strategy_metrics.unique_chunks_retrieved:<20} "
            f"{strategy_metrics.avg_latency_ms:<20.2f}"
        )
    
    print("-" * 80)
    print()
    
    # Show sample query result
    print("6. Sample Query Result (Query 1):")
    print()
    
    for strategy_name, strategy_metrics in metrics.items():
        result = strategy_metrics.query_results[0]
        
        print(f"   Strategy: {strategy_name}")
        print(f"   Query: \"{result.query}\"")
        
        if result.expanded_query:
            print(f"   Expanded: \"{result.expanded_query}\"")
        
        print(f"   Latency: {result.latency_ms:.2f} ms")
        print(f"   Retrieved {len(result.chunks)} chunks:")
        
        for i, (chunk, score) in enumerate(zip(result.chunks, result.scores), 1):
            print(f"      {i}. Score: {score:.4f}")
            print(f"         {chunk[:100]}...")
        
        print()
    
    print("=" * 80)
    print("Benchmark report saved to: retrieval_benchmark.md")
    print("=" * 80)


if __name__ == "__main__":
    main()
