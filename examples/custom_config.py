"""Custom Configuration Example for Context-Aware Retrieval Engine.

This script demonstrates how to customize the RAG system configuration
for different use cases and requirements.

Usage:
    python examples/custom_config.py
"""

import json
from pathlib import Path

from src.config import RAGConfig
from src.embedding import EmbeddingGenerator
from src.storage import FAISSVectorStore, ChromaDBVectorStore, NumpyVectorStore
from src.mocks import QueryExpander
from src.retrieval import RawVectorSearch, AIEnhancedRetrieval
from src.orchestrator import RAGOrchestrator


def example_1_default_config():
    """Example 1: Using default configuration."""
    print("=" * 80)
    print("Example 1: Default Configuration")
    print("=" * 80)
    print()
    
    # Create default configuration
    config = RAGConfig()
    
    print("Default Configuration:")
    print(f"  Embedding Model: {config.embedding_model}")
    print(f"  Vector Store Type: {config.vector_store_type}")
    print(f"  Similarity Metric: {config.similarity_metric}")
    print(f"  Top-K: {config.top_k}")
    print(f"  Chunk Size: {config.chunk_size}")
    print(f"  Chunk Overlap: {config.chunk_overlap}")
    print(f"  Expansion Strategy: {config.expansion_strategy}")
    print()
    
    # Validate configuration
    try:
        config.validate()
        print("[OK] Configuration is valid")
    except ValueError as e:
        print(f"[ERROR] Configuration error: {e}")
    
    print()


def example_2_custom_config():
    """Example 2: Creating custom configuration."""
    print("=" * 80)
    print("Example 2: Custom Configuration")
    print("=" * 80)
    print()
    
    # Create custom configuration for large documents
    config = RAGConfig(
        embedding_model="all-MiniLM-L6-v2",
        vector_store_type="faiss",
        similarity_metric="cosine",
        top_k=5,  # Retrieve more results
        chunk_size=1000,  # Larger chunks for context
        chunk_overlap=100,  # More overlap for continuity
        expansion_strategy="clarification",  # Different expansion strategy
        benchmark_queries=[
            "What are the system requirements?",
            "How do I configure the application?",
            "What are the security best practices?"
        ]
    )
    
    print("Custom Configuration (Large Documents):")
    print(f"  Embedding Model: {config.embedding_model}")
    print(f"  Vector Store Type: {config.vector_store_type}")
    print(f"  Similarity Metric: {config.similarity_metric}")
    print(f"  Top-K: {config.top_k}")
    print(f"  Chunk Size: {config.chunk_size}")
    print(f"  Chunk Overlap: {config.chunk_overlap}")
    print(f"  Expansion Strategy: {config.expansion_strategy}")
    print(f"  Benchmark Queries: {len(config.benchmark_queries)}")
    print()
    
    # Validate configuration
    try:
        config.validate()
        print("[OK] Configuration is valid")
    except ValueError as e:
        print(f"[ERROR] Configuration error: {e}")
    
    print()


def example_3_save_load_config():
    """Example 3: Saving and loading configuration from JSON."""
    print("=" * 80)
    print("Example 3: Save and Load Configuration")
    print("=" * 80)
    print()
    
    # Create configuration
    config = RAGConfig(
        embedding_model="all-MiniLM-L6-v2",
        vector_store_type="chromadb",
        similarity_metric="euclidean",
        top_k=3,
        chunk_size=500,
        chunk_overlap=50,
        expansion_strategy="decomposition",
        benchmark_queries=[
            "Query 1",
            "Query 2",
            "Query 3"
        ]
    )
    
    # Save to JSON file
    config_path = Path("example_config.json")
    config_dict = {
        "embedding_model": config.embedding_model,
        "vector_store_type": config.vector_store_type,
        "similarity_metric": config.similarity_metric,
        "top_k": config.top_k,
        "chunk_size": config.chunk_size,
        "chunk_overlap": config.chunk_overlap,
        "expansion_strategy": config.expansion_strategy,
        "benchmark_queries": config.benchmark_queries
    }
    
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(config_dict, f, indent=2)
    
    print(f"[OK] Configuration saved to: {config_path}")
    print()
    
    # Load from JSON file
    with open(config_path, 'r', encoding='utf-8') as f:
        loaded_dict = json.load(f)
    
    loaded_config = RAGConfig(**loaded_dict)
    
    print(f"[OK] Configuration loaded from: {config_path}")
    print()
    print("Loaded Configuration:")
    print(f"  Embedding Model: {loaded_config.embedding_model}")
    print(f"  Vector Store Type: {loaded_config.vector_store_type}")
    print(f"  Similarity Metric: {loaded_config.similarity_metric}")
    print(f"  Top-K: {loaded_config.top_k}")
    print()
    
    # Clean up
    config_path.unlink()
    print(f"[OK] Cleaned up example file: {config_path}")
    print()


def example_4_vector_store_comparison():
    """Example 4: Comparing different vector store backends."""
    print("=" * 80)
    print("Example 4: Vector Store Backend Comparison")
    print("=" * 80)
    print()
    
    # Initialize embedding generator
    embedding_generator = EmbeddingGenerator()
    embedding_dim = embedding_generator.get_embedding_dimension()
    
    print(f"Embedding Dimension: {embedding_dim}")
    print()
    
    # Configuration for each vector store type
    vector_stores = {
        "FAISS": {
            "config": RAGConfig(vector_store_type="faiss", similarity_metric="cosine"),
            "description": "Fast in-memory search with GPU support"
        },
        "ChromaDB": {
            "config": RAGConfig(vector_store_type="chromadb", similarity_metric="cosine"),
            "description": "Developer-friendly with built-in persistence"
        },
        "NumPy": {
            "config": RAGConfig(vector_store_type="numpy", similarity_metric="cosine"),
            "description": "Simple implementation for small datasets"
        }
    }
    
    print("Vector Store Options:")
    print()
    
    for name, info in vector_stores.items():
        config = info["config"]
        description = info["description"]
        
        print(f"{name}:")
        print(f"  Type: {config.vector_store_type}")
        print(f"  Similarity Metric: {config.similarity_metric}")
        print(f"  Description: {description}")
        print(f"  Best For: ", end="")
        
        if name == "FAISS":
            print("Large-scale production deployments, GPU acceleration")
        elif name == "ChromaDB":
            print("Development, prototyping, persistent storage")
        elif name == "NumPy":
            print("Small datasets, learning, simple use cases")
        
        print()


def example_5_expansion_strategies():
    """Example 5: Comparing query expansion strategies."""
    print("=" * 80)
    print("Example 5: Query Expansion Strategies")
    print("=" * 80)
    print()
    
    strategies = {
        "synonym_addition": "Adds synonyms and related terms to the query",
        "clarification": "Adds clarifying context and specificity",
        "decomposition": "Breaks complex queries into sub-queries"
    }
    
    print("Available Expansion Strategies:")
    print()
    
    for strategy, description in strategies.items():
        print(f"{strategy}:")
        print(f"  Description: {description}")
        
        # Create query expander with this strategy
        expander = QueryExpander(expansion_strategy=strategy)
        
        # Test with sample query
        sample_query = "How does the system handle load?"
        expanded = expander.expand_query(sample_query)
        
        print(f"  Example:")
        print(f"    Original: {sample_query}")
        print(f"    Expanded: {expanded}")
        print()


def example_6_complete_custom_setup():
    """Example 6: Complete custom setup with all components."""
    print("=" * 80)
    print("Example 6: Complete Custom Setup")
    print("=" * 80)
    print()
    
    # Create custom configuration
    config = RAGConfig(
        embedding_model="all-MiniLM-L6-v2",
        vector_store_type="numpy",
        similarity_metric="cosine",
        top_k=5,
        chunk_size=800,
        chunk_overlap=80,
        expansion_strategy="synonym_addition"
    )
    
    print("Step 1: Configuration")
    print(f"  [OK] Custom configuration created")
    print()
    
    # Initialize components
    print("Step 2: Component Initialization")
    
    embedding_generator = EmbeddingGenerator(model_name=config.embedding_model)
    print(f"  [OK] Embedding generator: {config.embedding_model}")
    
    vector_store = NumpyVectorStore(similarity_metric=config.similarity_metric)
    print(f"  [OK] Vector store: {config.vector_store_type}")
    
    query_expander = QueryExpander(expansion_strategy=config.expansion_strategy)
    print(f"  [OK] Query expander: {config.expansion_strategy}")
    
    # Create strategies
    strategies = {
        "raw": RawVectorSearch(embedding_generator, vector_store),
        "enhanced": AIEnhancedRetrieval(embedding_generator, vector_store, query_expander)
    }
    print(f"  [OK] Retrieval strategies: {', '.join(strategies.keys())}")
    print()
    
    # Create orchestrator
    print("Step 3: Orchestrator Creation")
    orchestrator = RAGOrchestrator(
        embedding_generator=embedding_generator,
        vector_store=vector_store,
        strategies=strategies
    )
    print(f"  [OK] Orchestrator ready")
    print()
    
    # Display system info
    print("Step 4: System Information")
    stats = orchestrator.get_statistics()
    print(f"  Total Chunks: {stats['total_chunks']}")
    print(f"  Embedding Dimension: {stats['embedding_dimension']}")
    print(f"  Available Strategies: {', '.join(stats['available_strategies'])}")
    print()
    
    print("[OK] Custom setup complete and ready for use!")
    print()


def main():
    """Run all configuration examples."""
    
    print("\n")
    print("*" * 80)
    print("Context-Aware Retrieval Engine - Configuration Examples")
    print("*" * 80)
    print("\n")
    
    # Run examples
    example_1_default_config()
    input("Press Enter to continue to Example 2...")
    print("\n")
    
    example_2_custom_config()
    input("Press Enter to continue to Example 3...")
    print("\n")
    
    example_3_save_load_config()
    input("Press Enter to continue to Example 4...")
    print("\n")
    
    example_4_vector_store_comparison()
    input("Press Enter to continue to Example 5...")
    print("\n")
    
    example_5_expansion_strategies()
    input("Press Enter to continue to Example 6...")
    print("\n")
    
    example_6_complete_custom_setup()
    
    print("*" * 80)
    print("All Configuration Examples Complete!")
    print("*" * 80)
    print()
    print("Key Takeaways:")
    print("  1. RAGConfig provides flexible configuration for all system components")
    print("  2. Configuration can be saved/loaded as JSON for reproducibility")
    print("  3. Different vector stores suit different use cases and scales")
    print("  4. Query expansion strategies affect retrieval quality differently")
    print("  5. All configuration values are validated automatically")
    print()
    print("Next Steps:")
    print("  - Create your own configuration file for your use case")
    print("  - Experiment with different parameter combinations")
    print("  - Use the CLI with --config flag to load custom configurations")
    print("  - Run benchmarks to compare configuration effectiveness")


if __name__ == "__main__":
    main()
