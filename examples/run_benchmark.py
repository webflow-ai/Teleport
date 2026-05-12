"""Benchmark Execution Example for Context-Aware Retrieval Engine.

This script demonstrates how to run a comprehensive benchmark comparing
retrieval strategies across multiple queries.

Usage:
    python examples/run_benchmark.py
"""

from src.config import RAGConfig
from src.embedding import EmbeddingGenerator
from src.storage import NumpyVectorStore
from src.mocks import QueryExpander
from src.retrieval import RawVectorSearch, AIEnhancedRetrieval
from src.orchestrator import RAGOrchestrator
from src.benchmark import BenchmarkEngine


def main():
    """Demonstrate benchmark execution workflow."""
    
    print("=" * 80)
    print("Context-Aware Retrieval Engine - Benchmark Example")
    print("=" * 80)
    print()
    
    # Step 1: Create configuration with benchmark queries
    print("Step 1: Creating configuration with benchmark queries...")
    
    benchmark_queries = [
        "How does the system handle peak load and traffic spikes?",
        "What are the key concepts in machine learning?",
        "Explain database indexing and query optimization",
        "What is the difference between authentication and authorization?",
        "How do microservices communicate with each other?",
        "What are the advantages of REST APIs over other protocols?"
    ]
    
    config = RAGConfig(
        embedding_model="all-MiniLM-L6-v2",
        vector_store_type="numpy",
        similarity_metric="cosine",
        top_k=3,
        chunk_size=500,
        expansion_strategy="synonym_addition",
        benchmark_queries=benchmark_queries
    )
    
    print(f"[OK] Configuration created with {len(benchmark_queries)} benchmark queries")
    print()
    
    # Step 2: Initialize components
    print("Step 2: Initializing RAG system...")
    
    embedding_generator = EmbeddingGenerator(model_name=config.embedding_model)
    vector_store = NumpyVectorStore(similarity_metric=config.similarity_metric)
    query_expander = QueryExpander(expansion_strategy=config.expansion_strategy)
    
    strategies = {
        "raw": RawVectorSearch(embedding_generator, vector_store),
        "enhanced": AIEnhancedRetrieval(embedding_generator, vector_store, query_expander)
    }
    
    orchestrator = RAGOrchestrator(
        embedding_generator=embedding_generator,
        vector_store=vector_store,
        strategies=strategies
    )
    
    print(f"[OK] RAG system initialized")
    print(f"  Strategies: {', '.join(strategies.keys())}")
    print()
    
    # Step 3: Ingest sample documents
    print("Step 3: Ingesting sample technical documentation...")
    
    sample_documents = [
        """Python is a high-level, interpreted programming language known for its 
        simplicity and readability. It supports multiple programming paradigms including 
        procedural, object-oriented, and functional programming. Python's extensive 
        standard library and vibrant ecosystem make it ideal for web development, 
        data science, automation, and more.""",
        
        """Machine learning is a subset of artificial intelligence that enables computers 
        to learn patterns from data without being explicitly programmed. Common algorithms 
        include supervised learning (classification, regression), unsupervised learning 
        (clustering, dimensionality reduction), and reinforcement learning. Deep learning, 
        using neural networks, has achieved breakthrough results in computer vision and 
        natural language processing.""",
        
        """Vector databases are specialized storage systems designed for high-dimensional 
        embeddings. They enable fast similarity search using techniques like approximate 
        nearest neighbor (ANN) search. Popular vector databases include FAISS, Pinecone, 
        Weaviate, and ChromaDB. These systems are essential for semantic search, 
        recommendation systems, and retrieval-augmented generation (RAG) applications.""",
        
        """The system handles peak load through multiple strategies. First, caching 
        reduces database queries by storing frequently accessed data in memory. Second, 
        load balancing distributes traffic across multiple servers. Third, horizontal 
        scaling adds more server instances to handle increased demand. Fourth, rate 
        limiting prevents system overload by throttling excessive requests.""",
        
        """Authentication and authorization are critical security mechanisms. Authentication 
        verifies user identity through credentials like passwords, tokens, or biometrics. 
        Authorization determines what authenticated users can access based on roles and 
        permissions. Common protocols include OAuth 2.0 for delegated authorization, 
        JWT for stateless authentication, and SAML for enterprise single sign-on.""",
        
        """Microservices architecture decomposes monolithic applications into loosely 
        coupled, independently deployable services. Each service owns its data and 
        communicates via APIs (REST, gRPC) or message queues. Benefits include independent 
        scaling, technology diversity, and fault isolation. Challenges include distributed 
        system complexity, network latency, and data consistency.""",
        
        """REST APIs provide a standardized interface for client-server communication 
        over HTTP. They use standard HTTP methods (GET, POST, PUT, DELETE) and status 
        codes. RESTful design principles include statelessness, resource-based URLs, 
        and hypermedia as the engine of application state (HATEOAS). Modern alternatives 
        include GraphQL for flexible queries and gRPC for high-performance RPC.""",
        
        """Database indexing dramatically improves query performance by creating efficient 
        data structures for fast lookups. B-tree indexes support range queries and are 
        default for most databases. Hash indexes provide O(1) lookups for equality checks. 
        Full-text indexes enable text search. However, indexes consume storage space and 
        slow down write operations, requiring careful trade-off analysis.""",
        
        """Distributed systems face unique challenges including network partitions, 
        clock synchronization, and consensus. The CAP theorem states that systems can 
        only guarantee two of three properties: Consistency, Availability, and Partition 
        tolerance. Consensus algorithms like Raft and Paxos enable distributed agreement. 
        Event sourcing and CQRS patterns help manage distributed state.""",
        
        """Container orchestration platforms like Kubernetes automate deployment, scaling, 
        and management of containerized applications. Key concepts include pods (groups 
        of containers), services (network endpoints), deployments (declarative updates), 
        and ingress (external access). Kubernetes provides self-healing, auto-scaling, 
        and rolling updates for production workloads."""
    ]
    
    stats = orchestrator.ingest_documents(sample_documents, chunk_size=config.chunk_size)
    
    print(f"[OK] Ingestion complete!")
    print(f"  Total Chunks: {stats.total_chunks}")
    print(f"  Ingestion Time: {stats.ingestion_time_ms:.2f}ms")
    print()
    
    # Step 4: Create benchmark engine
    print("Step 4: Creating benchmark engine...")
    benchmark_engine = BenchmarkEngine(orchestrator)
    print(f"[OK] Benchmark engine created")
    print()
    
    # Step 5: Run benchmark
    print("Step 5: Running benchmark...")
    print(f"  Queries: {len(benchmark_queries)}")
    print(f"  Strategies: {len(strategies)}")
    print(f"  Output: benchmark_example_results.md")
    print()
    
    print("Executing benchmark (this may take a moment)...")
    metrics_by_strategy = benchmark_engine.run_benchmark(
        queries=benchmark_queries,
        output_path="benchmark_example_results.md"
    )
    
    print("[OK] Benchmark execution complete!")
    print()
    
    # Step 6: Display summary metrics
    print("=" * 80)
    print("Step 6: Benchmark Summary")
    print("=" * 80)
    print()
    
    for strategy_name, metrics in metrics_by_strategy.items():
        print(f"Strategy: {strategy_name}")
        print(f"  Average Similarity Score: {metrics.avg_similarity_score:.4f}")
        print(f"  Unique Chunks Retrieved: {metrics.unique_chunks_retrieved}")
        print(f"  Average Latency: {metrics.avg_latency_ms:.2f}ms")
        print(f"  Total Queries: {len(metrics.query_results)}")
        print()
    
    # Step 7: Analyze results
    print("=" * 80)
    print("Step 7: Result Analysis")
    print("=" * 80)
    print()
    
    # Compare strategies
    strategy_names = list(metrics_by_strategy.keys())
    if len(strategy_names) >= 2:
        strategy1 = strategy_names[0]
        strategy2 = strategy_names[1]
        
        metrics1 = metrics_by_strategy[strategy1]
        metrics2 = metrics_by_strategy[strategy2]
        
        print(f"Comparing {strategy1} vs {strategy2}:")
        print()
        
        # Similarity score comparison
        score_diff = metrics2.avg_similarity_score - metrics1.avg_similarity_score
        score_pct = (score_diff / metrics1.avg_similarity_score) * 100 if metrics1.avg_similarity_score > 0 else 0
        print(f"Similarity Score:")
        print(f"  {strategy1}: {metrics1.avg_similarity_score:.4f}")
        print(f"  {strategy2}: {metrics2.avg_similarity_score:.4f}")
        print(f"  Difference: {score_diff:+.4f} ({score_pct:+.2f}%)")
        print()
        
        # Diversity comparison
        print(f"Result Diversity:")
        print(f"  {strategy1}: {metrics1.unique_chunks_retrieved} unique chunks")
        print(f"  {strategy2}: {metrics2.unique_chunks_retrieved} unique chunks")
        print()
        
        # Latency comparison
        latency_diff = metrics2.avg_latency_ms - metrics1.avg_latency_ms
        latency_pct = (latency_diff / metrics1.avg_latency_ms) * 100 if metrics1.avg_latency_ms > 0 else 0
        print(f"Latency:")
        print(f"  {strategy1}: {metrics1.avg_latency_ms:.2f}ms")
        print(f"  {strategy2}: {metrics2.avg_latency_ms:.2f}ms")
        print(f"  Difference: {latency_diff:+.2f}ms ({latency_pct:+.2f}%)")
        print()
        
        # Calculate overlap
        chunks1 = set()
        chunks2 = set()
        for result in metrics1.query_results:
            chunks1.update(result.chunks)
        for result in metrics2.query_results:
            chunks2.update(result.chunks)
        
        overlap = chunks1.intersection(chunks2)
        overlap_pct = (len(overlap) / len(chunks1)) * 100 if len(chunks1) > 0 else 0
        
        print(f"Result Overlap:")
        print(f"  Common chunks: {len(overlap)}")
        print(f"  Overlap percentage: {overlap_pct:.1f}%")
        print()
    
    print("=" * 80)
    print("Benchmark Example Complete!")
    print("=" * 80)
    print()
    print("Next Steps:")
    print("  1. Review the detailed report: benchmark_example_results.md")
    print("  2. Analyze per-query results to understand strategy differences")
    print("  3. Try different expansion strategies (clarification, decomposition)")
    print("  4. Experiment with different similarity metrics (cosine vs euclidean)")
    print("  5. Test with your own domain-specific documents and queries")
    print()
    print("Key Insights:")
    print("  - Raw search is typically faster but may miss semantic variations")
    print("  - Enhanced search may retrieve more diverse results through expansion")
    print("  - Query expansion effectiveness depends on the expansion strategy")
    print("  - Consider the latency vs. quality trade-off for your use case")


if __name__ == "__main__":
    main()
