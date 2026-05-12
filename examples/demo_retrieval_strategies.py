"""Demo script showing retrieval strategies in action.

This script demonstrates both RawVectorSearch and AIEnhancedRetrieval
strategies with sample technical documentation.
"""

from src.embedding import EmbeddingGenerator
from src.storage import NumpyVectorStore
from src.mocks import QueryExpander
from src.retrieval import RawVectorSearch, AIEnhancedRetrieval


def main():
    """Run retrieval strategy demonstration."""
    
    print("=" * 80)
    print("Context-Aware Retrieval Engine - Retrieval Strategies Demo")
    print("=" * 80)
    print()
    
    # Initialize components
    print("Initializing components...")
    embedding_generator = EmbeddingGenerator()
    vector_store = NumpyVectorStore(similarity_metric="cosine")
    query_expander = QueryExpander(expansion_strategy="synonym_addition")
    
    # Sample technical documentation
    sample_docs = [
        "Python is a high-level, interpreted programming language known for its simplicity and readability.",
        "Machine learning algorithms enable computers to learn patterns from data without explicit programming.",
        "Vector databases store embeddings and enable fast similarity search for semantic retrieval.",
        "The system handles peak load by implementing caching, load balancing, and horizontal scaling.",
        "Authentication and authorization mechanisms ensure secure access control to system resources.",
        "Microservices architecture decomposes applications into loosely coupled, independently deployable services.",
        "REST APIs provide a standardized interface for client-server communication over HTTP.",
        "Database indexing improves query performance by creating efficient data structures for lookups.",
    ]
    
    print(f"Ingesting {len(sample_docs)} documents...")
    embeddings = embedding_generator.encode(sample_docs)
    vector_store.add(embeddings, sample_docs)
    print(f"✓ Stored {len(sample_docs)} document chunks")
    print()
    
    # Initialize retrieval strategies
    raw_search = RawVectorSearch(embedding_generator, vector_store)
    ai_enhanced = AIEnhancedRetrieval(embedding_generator, vector_store, query_expander)
    
    # Test queries
    test_queries = [
        "How does the system handle load?",
        "What is machine learning?",
        "Explain database performance optimization"
    ]
    
    # Run retrieval for each query
    for i, query in enumerate(test_queries, 1):
        print("=" * 80)
        print(f"Query {i}: {query}")
        print("=" * 80)
        print()
        
        # Raw Vector Search
        print("Strategy 1: Raw Vector Search")
        print("-" * 80)
        raw_result = raw_search.retrieve(query, k=3)
        print(f"Original Query: {raw_result.query}")
        print(f"Latency: {raw_result.latency_ms:.2f}ms")
        print(f"\nTop {len(raw_result.chunks)} Results:")
        for j, (chunk, score) in enumerate(zip(raw_result.chunks, raw_result.scores), 1):
            print(f"\n  {j}. [Score: {score:.4f}]")
            print(f"     {chunk}")
        print()
        
        # AI-Enhanced Retrieval
        print("Strategy 2: AI-Enhanced Retrieval")
        print("-" * 80)
        ai_result = ai_enhanced.retrieve(query, k=3)
        print(f"Original Query: {ai_result.query}")
        print(f"Expanded Query: {ai_result.expanded_query}")
        print(f"Latency: {ai_result.latency_ms:.2f}ms")
        print(f"\nTop {len(ai_result.chunks)} Results:")
        for j, (chunk, score) in enumerate(zip(ai_result.chunks, ai_result.scores), 1):
            print(f"\n  {j}. [Score: {score:.4f}]")
            print(f"     {chunk}")
        print()
        
        # Compare results
        print("Comparison:")
        print("-" * 80)
        raw_chunks_set = set(raw_result.chunks)
        ai_chunks_set = set(ai_result.chunks)
        overlap = raw_chunks_set & ai_chunks_set
        
        print(f"Raw Search Latency: {raw_result.latency_ms:.2f}ms")
        print(f"AI-Enhanced Latency: {ai_result.latency_ms:.2f}ms")
        print(f"Overlapping Results: {len(overlap)}/{len(raw_result.chunks)}")
        print(f"Query Expansion Changed Query: {ai_result.query != ai_result.expanded_query}")
        print()
    
    print("=" * 80)
    print("Demo Complete!")
    print("=" * 80)


if __name__ == "__main__":
    main()
