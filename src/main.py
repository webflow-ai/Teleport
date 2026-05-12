"""Main CLI Entry Point for Context-Aware Retrieval Engine.

This module provides a command-line interface for the RAG system,
supporting document ingestion, retrieval, and benchmarking operations.

Commands:
    ingest: Ingest documents into the vector store
    retrieve: Retrieve relevant chunks for a query
    benchmark: Run benchmark comparison across strategies

Usage:
    python -m src.main ingest --documents doc1.txt doc2.txt
    python -m src.main retrieve --query "How does the system handle load?"
    python -m src.main benchmark --queries queries.txt
"""

import argparse
import sys
import json
from pathlib import Path
from typing import List, Optional

from src.config import RAGConfig
from src.embedding import EmbeddingGenerator
from src.storage import FAISSVectorStore, ChromaDBVectorStore, NumpyVectorStore
from src.mocks import QueryExpander
from src.retrieval import RawVectorSearch, AIEnhancedRetrieval
from src.orchestrator import RAGOrchestrator
from src.benchmark import BenchmarkEngine


def create_vector_store(config: RAGConfig, embedding_dimension: int):
    """Create vector store based on configuration.
    
    Args:
        config: RAG configuration
        embedding_dimension: Dimensionality of embeddings
    
    Returns:
        VectorStore instance
    
    Raises:
        ValueError: If vector store type is invalid
    """
    if config.vector_store_type == "faiss":
        return FAISSVectorStore(
            dimension=embedding_dimension,
            similarity_metric=config.similarity_metric
        )
    elif config.vector_store_type == "chromadb":
        return ChromaDBVectorStore(
            collection_name="rag_collection",
            persist_directory="./chroma_db"
        )
    elif config.vector_store_type == "numpy":
        return NumpyVectorStore(similarity_metric=config.similarity_metric)
    else:
        raise ValueError(
            f"Invalid vector_store_type: {config.vector_store_type}. "
            f"Must be one of: faiss, chromadb, numpy"
        )


def create_orchestrator(config: RAGConfig) -> RAGOrchestrator:
    """Create RAGOrchestrator with configured components.
    
    Args:
        config: RAG configuration
    
    Returns:
        Configured RAGOrchestrator instance
    """
    # Initialize embedding generator
    embedding_generator = EmbeddingGenerator(model_name=config.embedding_model)
    
    # Initialize vector store
    embedding_dimension = embedding_generator.get_embedding_dimension()
    vector_store = create_vector_store(config, embedding_dimension)
    
    # Initialize query expander
    query_expander = QueryExpander(expansion_strategy=config.expansion_strategy)
    
    # Initialize retrieval strategies
    strategies = {
        "raw": RawVectorSearch(embedding_generator, vector_store),
        "enhanced": AIEnhancedRetrieval(embedding_generator, vector_store, query_expander)
    }
    
    # Create orchestrator
    orchestrator = RAGOrchestrator(
        embedding_generator=embedding_generator,
        vector_store=vector_store,
        strategies=strategies
    )
    
    return orchestrator


def load_config(config_path: Optional[str] = None) -> RAGConfig:
    """Load configuration from file or use defaults.
    
    Args:
        config_path: Path to JSON configuration file (optional)
    
    Returns:
        RAGConfig instance
    
    Raises:
        FileNotFoundError: If config_path is provided but file doesn't exist
        ValueError: If configuration is invalid
    """
    if config_path:
        config_file = Path(config_path)
        if not config_file.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_path}")
        
        with open(config_file, 'r', encoding='utf-8') as f:
            config_dict = json.load(f)
        
        return RAGConfig(**config_dict)
    else:
        # Use default configuration
        return RAGConfig()


def read_documents_from_files(file_paths: List[str]) -> List[str]:
    """Read document content from files.
    
    Args:
        file_paths: List of file paths to read
    
    Returns:
        List of document strings
    
    Raises:
        FileNotFoundError: If any file doesn't exist
    """
    documents = []
    for file_path in file_paths:
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"Document file not found: {file_path}")
        
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
            documents.append(content)
    
    return documents


def read_queries_from_file(file_path: str) -> List[str]:
    """Read queries from file (one per line).
    
    Args:
        file_path: Path to queries file
    
    Returns:
        List of query strings
    
    Raises:
        FileNotFoundError: If file doesn't exist
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"Queries file not found: {file_path}")
    
    with open(path, 'r', encoding='utf-8') as f:
        queries = [line.strip() for line in f if line.strip()]
    
    return queries


def cmd_ingest(args, config: RAGConfig):
    """Execute ingest command.
    
    Args:
        args: Parsed command-line arguments
        config: RAG configuration
    """
    print("=" * 80)
    print("Context-Aware Retrieval Engine - Document Ingestion")
    print("=" * 80)
    print()
    
    # Read documents
    print(f"Reading {len(args.documents)} document file(s)...")
    try:
        documents = read_documents_from_files(args.documents)
        print(f"[OK] Loaded {len(documents)} documents")
    except FileNotFoundError as e:
        print(f"[ERROR] Error: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Create orchestrator
    print("\nInitializing RAG system...")
    try:
        orchestrator = create_orchestrator(config)
        print(f"[OK] Using embedding model: {config.embedding_model}")
        print(f"[OK] Using vector store: {config.vector_store_type}")
        print(f"[OK] Using similarity metric: {config.similarity_metric}")
    except Exception as e:
        print(f"[ERROR] Error initializing system: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Ingest documents
    print(f"\nIngesting documents (chunk_size={config.chunk_size})...")
    try:
        stats = orchestrator.ingest_documents(documents, chunk_size=config.chunk_size)
        print(f"[OK] Ingestion complete!")
        print(f"\nIngestion Statistics:")
        print(f"  Total Chunks: {stats.total_chunks}")
        print(f"  Embedding Dimension: {stats.embedding_dimension}")
        print(f"  Total Tokens (approx): {stats.total_tokens}")
        print(f"  Ingestion Time: {stats.ingestion_time_ms:.2f}ms")
    except Exception as e:
        print(f"[ERROR] Error during ingestion: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Save vector store if persistence is supported
    if args.save:
        print(f"\nSaving vector store to: {args.save}")
        try:
            orchestrator.vector_store.save(args.save)
            print(f"[OK] Vector store saved successfully")
        except Exception as e:
            print(f"[ERROR] Error saving vector store: {e}", file=sys.stderr)
            sys.exit(1)
    
    print("\n" + "=" * 80)
    print("Ingestion Complete!")
    print("=" * 80)


def cmd_retrieve(args, config: RAGConfig):
    """Execute retrieve command.
    
    Args:
        args: Parsed command-line arguments
        config: RAG configuration
    """
    print("=" * 80)
    print("Context-Aware Retrieval Engine - Retrieval")
    print("=" * 80)
    print()
    
    # Create orchestrator
    print("Initializing RAG system...")
    try:
        orchestrator = create_orchestrator(config)
        print(f"[OK] Using embedding model: {config.embedding_model}")
        print(f"[OK] Using vector store: {config.vector_store_type}")
    except Exception as e:
        print(f"[ERROR] Error initializing system: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Load vector store if specified
    if args.load:
        print(f"\nLoading vector store from: {args.load}")
        try:
            orchestrator.vector_store.load(args.load)
            stats = orchestrator.get_statistics()
            print(f"[OK] Vector store loaded successfully")
            print(f"  Total Chunks: {stats['total_chunks']}")
        except Exception as e:
            print(f"[ERROR] Error loading vector store: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        print("\n[WARNING] Warning: No vector store loaded. Results may be empty.")
        print("  Use --load to load a saved vector store, or run 'ingest' first.")
    
    # Determine strategy
    strategy = args.strategy if args.strategy else "raw"
    if strategy not in orchestrator.strategies:
        print(f"[ERROR] Error: Unknown strategy '{strategy}'", file=sys.stderr)
        print(f"  Available strategies: {', '.join(orchestrator.strategies.keys())}")
        sys.exit(1)
    
    # Execute retrieval
    print(f"\nQuery: {args.query}")
    print(f"Strategy: {strategy}")
    print(f"Top-K: {config.top_k}")
    print()
    
    try:
        result = orchestrator.retrieve(args.query, strategy, k=config.top_k)
        
        print("-" * 80)
        print(f"Original Query: {result.query}")
        if result.expanded_query and result.expanded_query != result.query:
            print(f"Expanded Query: {result.expanded_query}")
        print(f"Latency: {result.latency_ms:.2f}ms")
        print(f"Strategy: {result.strategy_name}")
        print("-" * 80)
        print()
        
        if len(result.chunks) > 0:
            print(f"Retrieved {len(result.chunks)} chunk(s):")
            print()
            for i, (chunk, score) in enumerate(zip(result.chunks, result.scores), 1):
                print(f"{i}. [Score: {score:.4f}]")
                print(f"   {chunk}")
                print()
        else:
            print("No results found.")
            print()
        
    except Exception as e:
        print(f"[ERROR] Error during retrieval: {e}", file=sys.stderr)
        sys.exit(1)
    
    print("=" * 80)
    print("Retrieval Complete!")
    print("=" * 80)


def cmd_benchmark(args, config: RAGConfig):
    """Execute benchmark command.
    
    Args:
        args: Parsed command-line arguments
        config: RAG configuration
    """
    print("=" * 80)
    print("Context-Aware Retrieval Engine - Benchmark")
    print("=" * 80)
    print()
    
    # Read queries
    if args.queries_file:
        print(f"Reading queries from: {args.queries_file}")
        try:
            queries = read_queries_from_file(args.queries_file)
            print(f"[OK] Loaded {len(queries)} queries")
        except FileNotFoundError as e:
            print(f"[ERROR] Error: {e}", file=sys.stderr)
            sys.exit(1)
    elif config.benchmark_queries:
        queries = config.benchmark_queries
        print(f"Using {len(queries)} queries from configuration")
    else:
        print("[ERROR] Error: No queries provided", file=sys.stderr)
        print("  Use --queries-file or add benchmark_queries to config")
        sys.exit(1)
    
    # Create orchestrator
    print("\nInitializing RAG system...")
    try:
        orchestrator = create_orchestrator(config)
        print(f"[OK] Using embedding model: {config.embedding_model}")
        print(f"[OK] Using vector store: {config.vector_store_type}")
        print(f"[OK] Strategies: {', '.join(orchestrator.strategies.keys())}")
    except Exception as e:
        print(f"[ERROR] Error initializing system: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Load vector store if specified
    if args.load:
        print(f"\nLoading vector store from: {args.load}")
        try:
            orchestrator.vector_store.load(args.load)
            stats = orchestrator.get_statistics()
            print(f"[OK] Vector store loaded successfully")
            print(f"  Total Chunks: {stats['total_chunks']}")
        except Exception as e:
            print(f"[ERROR] Error loading vector store: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        print("\n[WARNING] Warning: No vector store loaded. Results may be empty.")
        print("  Use --load to load a saved vector store, or run 'ingest' first.")
    
    # Create benchmark engine
    benchmark_engine = BenchmarkEngine(orchestrator)
    
    # Run benchmark
    output_path = args.output if args.output else "retrieval_benchmark.md"
    print(f"\nRunning benchmark with {len(queries)} queries...")
    print(f"Output will be saved to: {output_path}")
    print()
    
    try:
        metrics_by_strategy = benchmark_engine.run_benchmark(queries, output_path)
        
        print("[OK] Benchmark complete!")
        print()
        print("-" * 80)
        print("Summary Metrics:")
        print("-" * 80)
        print()
        
        for strategy_name, metrics in metrics_by_strategy.items():
            print(f"Strategy: {strategy_name}")
            print(f"  Avg Similarity Score: {metrics.avg_similarity_score:.4f}")
            print(f"  Unique Chunks Retrieved: {metrics.unique_chunks_retrieved}")
            print(f"  Avg Latency: {metrics.avg_latency_ms:.2f}ms")
            print()
        
        print(f"[OK] Detailed report saved to: {output_path}")
        
    except Exception as e:
        print(f"[ERROR] Error during benchmark: {e}", file=sys.stderr)
        sys.exit(1)
    
    print("\n" + "=" * 80)
    print("Benchmark Complete!")
    print("=" * 80)


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Context-Aware Retrieval Engine - RAG System CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Ingest documents
  python -m src.main ingest --documents doc1.txt doc2.txt --save vector_store

  # Retrieve with raw search
  python -m src.main retrieve --query "How does the system handle load?" --load vector_store

  # Retrieve with AI-enhanced search
  python -m src.main retrieve --query "What is ML?" --strategy enhanced --load vector_store

  # Run benchmark
  python -m src.main benchmark --queries-file queries.txt --load vector_store --output results.md

  # Use custom configuration
  python -m src.main ingest --documents doc.txt --config my_config.json
        """
    )
    
    # Global arguments
    parser.add_argument(
        '--config',
        type=str,
        help='Path to JSON configuration file (optional)'
    )
    
    # Subcommands
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    
    # Ingest command
    ingest_parser = subparsers.add_parser(
        'ingest',
        help='Ingest documents into the vector store'
    )
    ingest_parser.add_argument(
        '--documents',
        nargs='+',
        required=True,
        help='Paths to document files to ingest'
    )
    ingest_parser.add_argument(
        '--save',
        type=str,
        help='Path to save the vector store after ingestion'
    )
    
    # Retrieve command
    retrieve_parser = subparsers.add_parser(
        'retrieve',
        help='Retrieve relevant chunks for a query'
    )
    retrieve_parser.add_argument(
        '--query',
        type=str,
        required=True,
        help='Query string to search for'
    )
    retrieve_parser.add_argument(
        '--strategy',
        type=str,
        choices=['raw', 'enhanced'],
        default='raw',
        help='Retrieval strategy to use (default: raw)'
    )
    retrieve_parser.add_argument(
        '--load',
        type=str,
        help='Path to load the vector store from'
    )
    
    # Benchmark command
    benchmark_parser = subparsers.add_parser(
        'benchmark',
        help='Run benchmark comparison across strategies'
    )
    benchmark_parser.add_argument(
        '--queries-file',
        type=str,
        help='Path to file containing queries (one per line)'
    )
    benchmark_parser.add_argument(
        '--load',
        type=str,
        help='Path to load the vector store from'
    )
    benchmark_parser.add_argument(
        '--output',
        type=str,
        default='retrieval_benchmark.md',
        help='Path to save benchmark report (default: retrieval_benchmark.md)'
    )
    
    # Parse arguments
    args = parser.parse_args()
    
    # Check if command was provided
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    # Load configuration
    try:
        config = load_config(args.config)
    except Exception as e:
        print(f"[ERROR] Error loading configuration: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Execute command
    try:
        if args.command == 'ingest':
            cmd_ingest(args, config)
        elif args.command == 'retrieve':
            cmd_retrieve(args, config)
        elif args.command == 'benchmark':
            cmd_benchmark(args, config)
    except KeyboardInterrupt:
        print("\n\n[ERROR] Operation cancelled by user", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERROR] Unexpected error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

