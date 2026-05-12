"""Basic Usage Example for Context-Aware Retrieval Engine.

This script demonstrates the complete workflow of ingesting documents
and retrieving relevant chunks using both retrieval strategies.

Usage:
    python examples/basic_usage.py
"""

from src.config import RAGConfig
from src.embedding import EmbeddingGenerator
from src.storage import NumpyVectorStore
from src.mocks import QueryExpander
from src.retrieval import RawVectorSearch, AIEnhancedRetrieval
from src.orchestrator import RAGOrchestrator


def main():
    """Demonstrate basic ingestion and retrieval workflow."""
    
    print("=" * 80)
    print("Context-Aware Retrieval Engine - Basic Usage Example")
    print("=" * 80)
    print()
    
    # Step 1: Create configuration
    print("Step 1: Creating configuration...")
    config = RAGConfig(
        embedding_model="all-MiniLM-L6-v2",
        vector_store_type="numpy",
        similarity_metric="cosine",
        top_k=3,
        chunk_size=500,
        expansion_strategy="synonym_addition"
    )
    print(f"[OK] Configuration created")
    print(f"  Embedding Model: {config.embedding_model}")
    print(f"  Vector Store: {config.vector_store_type}")
    print(f"  Similarity Metric: {config.similarity_metric}")
    print()
    
    # Step 2: Initialize components
    print("Step 2: Initializing components...")
    
    # Initialize embedding generator
    embedding_generator = EmbeddingGenerator(model_name=config.embedding_model)
    print(f"[OK] Embedding generator initialized")
    print(f"  Embedding dimension: {embedding_generator.get_embedding_dimension()}")
    
    # Initialize vector store
    vector_store = NumpyVectorStore(similarity_metric=config.similarity_metric)
    print(f"[OK] Vector store initialized")
    
    # Initialize query expander
    query_expander = QueryExpander(expansion_strategy=config.expansion_strategy)
    print(f"[OK] Query expander initialized")
    
    # Initialize retrieval strategies
    raw_search = RawVectorSearch(embedding_generator, vector_store)
    ai_enhanced = AIEnhancedRetrieval(embedding_generator, vector_store, query_expander)
    
    strategies = {
        "raw": raw_search,
        "enhanced": ai_enhanced
    }
    print(f"[OK] Retrieval strategies initialized: {', '.join(strategies.keys())}")
    
    # Create orchestrator
    orchestrator = RAGOrchestrator(
        embedding_generator=embedding_generator,
        vector_store=vector_store,
        strategies=strategies
    )
    print(f"[OK] Orchestrator created")
    print()
    
    # Step 3: Ingest sample documents
    print("Step 3: Ingesting sample documents...")
    
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
        slow down write operations, requiring careful trade-off analysis."""
    ]
    
    stats = orchestrator.ingest_documents(sample_documents, chunk_size=config.chunk_size)
    
    print(f"[OK] Ingestion complete!")
    print(f"  Total Chunks: {stats.total_chunks}")
    print(f"  Embedding Dimension: {stats.embedding_dimension}")
    print(f"  Total Tokens (approx): {stats.total_tokens}")
    print(f"  Ingestion Time: {stats.ingestion_time_ms:.2f}ms")
    print()
    
    # Step 4: Retrieve with different strategies
    print("Step 4: Retrieving relevant chunks...")
    print()
    
    test_queries = [
        "How does the system handle peak load?",
        "What is machine learning?",
        "Explain database performance optimization"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print("-" * 80)
        print(f"Query {i}: {query}")
        print("-" * 80)
        print()
        
        # Raw Vector Search
        print("Strategy: Raw Vector Search")
        raw_result = orchestrator.retrieve(query, "raw", k=config.top_k)
        print(f"  Latency: {raw_result.latency_ms:.2f}ms")
        print(f"  Top {len(raw_result.chunks)} Results:")
        for j, (chunk, score) in enumerate(zip(raw_result.chunks, raw_result.scores), 1):
            print(f"    {j}. [Score: {score:.4f}] {chunk[:80]}...")
        print()
        
        # AI-Enhanced Retrieval
        print("Strategy: AI-Enhanced Retrieval")
        ai_result = orchestrator.retrieve(query, "enhanced", k=config.top_k)
        print(f"  Expanded Query: {ai_result.expanded_query}")
        print(f"  Latency: {ai_result.latency_ms:.2f}ms")
        print(f"  Top {len(ai_result.chunks)} Results:")
        for j, (chunk, score) in enumerate(zip(ai_result.chunks, ai_result.scores), 1):
            print(f"    {j}. [Score: {score:.4f}] {chunk[:80]}...")
        print()
    
    # Step 5: Display system statistics
    print("=" * 80)
    print("Step 5: System Statistics")
    print("=" * 80)
    
    stats_dict = orchestrator.get_statistics()
    print(f"Total Chunks Stored: {stats_dict['total_chunks']}")
    print(f"Embedding Dimension: {stats_dict['embedding_dimension']}")
    print(f"Available Strategies: {', '.join(stats_dict['available_strategies'])}")
    print()
    
    print("=" * 80)
    print("Basic Usage Example Complete!")
    print("=" * 80)
    print()
    print("Next Steps:")
    print("  1. Try modifying the sample documents")
    print("  2. Experiment with different queries")
    print("  3. Change configuration parameters (chunk_size, top_k, etc.)")
    print("  4. Try different vector stores (FAISS, ChromaDB)")
    print("  5. Run the benchmark example to compare strategies")


if __name__ == "__main__":
    main()
