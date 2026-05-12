"""Demo script for the RAGOrchestrator module.

This script demonstrates the complete RAG pipeline including:
- Document ingestion with chunking
- Embedding generation and storage
- Retrieval using both raw and AI-enhanced strategies
- Statistics monitoring
"""

from src.embedding import EmbeddingGenerator
from src.storage import NumpyVectorStore
from src.retrieval import RawVectorSearch, AIEnhancedRetrieval
from src.mocks import QueryExpander
from src.orchestrator import RAGOrchestrator


def main():
    """Run the orchestrator demo."""
    print("=" * 80)
    print("RAG Orchestrator Demo")
    print("=" * 80)
    print()
    
    # Step 1: Initialize components
    print("Step 1: Initializing components...")
    embedding_generator = EmbeddingGenerator(model_name="all-MiniLM-L6-v2")
    vector_store = NumpyVectorStore(similarity_metric="cosine")
    
    # Create retrieval strategies
    raw_strategy = RawVectorSearch(embedding_generator, vector_store)
    
    query_expander = QueryExpander(expansion_strategy="synonym_addition")
    enhanced_strategy = AIEnhancedRetrieval(embedding_generator, vector_store, query_expander)
    
    # Create orchestrator
    strategies = {
        "raw": raw_strategy,
        "enhanced": enhanced_strategy
    }
    orchestrator = RAGOrchestrator(embedding_generator, vector_store, strategies)
    print("✓ Components initialized")
    print()
    
    # Step 2: Ingest documents
    print("Step 2: Ingesting technical documents...")
    documents = [
        """Microservices architecture is a design pattern where applications are composed 
        of small, independent services that communicate over well-defined APIs. Each service 
        is responsible for a specific business capability and can be developed, deployed, 
        and scaled independently.""",
        
        """Load balancing distributes incoming network traffic across multiple servers to 
        ensure no single server becomes overwhelmed. This improves application availability, 
        reliability, and performance by preventing any one server from becoming a bottleneck.""",
        
        """Caching is a technique used to store frequently accessed data in a fast-access 
        storage layer. By reducing the need to fetch data from slower storage systems or 
        recompute results, caching significantly improves application performance and reduces 
        latency.""",
        
        """Database indexing creates data structures that improve the speed of data retrieval 
        operations. Indexes work like a book's index, allowing the database to quickly locate 
        data without scanning every row in a table. However, indexes consume additional storage 
        and can slow down write operations.""",
        
        """API rate limiting controls the number of requests a client can make to an API 
        within a specified time window. This prevents abuse, ensures fair resource allocation, 
        and protects backend systems from being overwhelmed by too many requests."""
    ]
    
    stats = orchestrator.ingest_documents(documents, chunk_size=300)
    
    print(f"✓ Ingestion complete:")
    print(f"  - Total chunks: {stats.total_chunks}")
    print(f"  - Embedding dimension: {stats.embedding_dimension}")
    print(f"  - Approximate tokens: {stats.total_tokens}")
    print(f"  - Ingestion time: {stats.ingestion_time_ms:.2f}ms")
    print()
    
    # Step 3: Query with raw vector search
    print("Step 3: Querying with Raw Vector Search...")
    query = "How does the system handle peak load?"
    print(f"Query: '{query}'")
    print()
    
    raw_result = orchestrator.retrieve(query, strategy_name="raw", k=3)
    
    print(f"Strategy: {raw_result.strategy_name}")
    print(f"Latency: {raw_result.latency_ms:.2f}ms")
    print(f"Results ({len(raw_result.chunks)} chunks):")
    for i, (chunk, score) in enumerate(zip(raw_result.chunks, raw_result.scores), 1):
        print(f"\n  [{i}] Score: {score:.4f}")
        print(f"      {chunk[:150]}...")
    print()
    
    # Step 4: Query with AI-enhanced retrieval
    print("Step 4: Querying with AI-Enhanced Retrieval...")
    print(f"Query: '{query}'")
    print()
    
    enhanced_result = orchestrator.retrieve(query, strategy_name="enhanced", k=3)
    
    print(f"Strategy: {enhanced_result.strategy_name}")
    print(f"Original query: '{enhanced_result.query}'")
    print(f"Expanded query: '{enhanced_result.expanded_query}'")
    print(f"Latency: {enhanced_result.latency_ms:.2f}ms")
    print(f"Results ({len(enhanced_result.chunks)} chunks):")
    for i, (chunk, score) in enumerate(zip(enhanced_result.chunks, enhanced_result.scores), 1):
        print(f"\n  [{i}] Score: {score:.4f}")
        print(f"      {chunk[:150]}...")
    print()
    
    # Step 5: Compare strategies
    print("Step 5: Comparing strategies...")
    print(f"Raw search latency: {raw_result.latency_ms:.2f}ms")
    print(f"Enhanced search latency: {enhanced_result.latency_ms:.2f}ms")
    print(f"Raw search avg score: {sum(raw_result.scores) / len(raw_result.scores):.4f}")
    print(f"Enhanced search avg score: {sum(enhanced_result.scores) / len(enhanced_result.scores):.4f}")
    
    # Check for overlap in results
    raw_chunks_set = set(raw_result.chunks)
    enhanced_chunks_set = set(enhanced_result.chunks)
    overlap = raw_chunks_set.intersection(enhanced_chunks_set)
    print(f"Result overlap: {len(overlap)} / {len(raw_result.chunks)} chunks")
    print()
    
    # Step 6: Display system statistics
    print("Step 6: System statistics...")
    system_stats = orchestrator.get_statistics()
    print(f"Total chunks stored: {system_stats['total_chunks']}")
    print(f"Embedding dimension: {system_stats['embedding_dimension']}")
    print(f"Available strategies: {', '.join(system_stats['available_strategies'])}")
    print()
    
    # Step 7: Try different queries
    print("Step 7: Testing with different queries...")
    test_queries = [
        "What is caching?",
        "How to improve database performance?",
        "API security best practices"
    ]
    
    for test_query in test_queries:
        result = orchestrator.retrieve(test_query, strategy_name="enhanced", k=1)
        print(f"\nQuery: '{test_query}'")
        print(f"Expanded: '{result.expanded_query}'")
        print(f"Top result (score: {result.scores[0]:.4f}): {result.chunks[0][:100]}...")
    
    print()
    print("=" * 80)
    print("Demo complete!")
    print("=" * 80)


if __name__ == "__main__":
    main()
