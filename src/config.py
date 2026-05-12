"""Configuration Module for Context-Aware Retrieval Engine.

This module provides configuration management for the RAG system,
including settings for embeddings, vector storage, retrieval, chunking,
and benchmarking.
"""

from dataclasses import dataclass, field
from typing import List


@dataclass
class RAGConfig:
    """System configuration for the Context-Aware Retrieval Engine.
    
    This dataclass defines all configurable parameters for the RAG system,
    including embedding model selection, vector store configuration,
    retrieval settings, chunking parameters, and query expansion strategy.
    
    Attributes:
        embedding_model: Name of the sentence-transformers model to use
                        (default: "all-MiniLM-L6-v2")
        vector_store_type: Type of vector store backend
                          Options: "faiss", "chromadb", "numpy"
                          (default: "faiss")
        similarity_metric: Similarity metric for vector comparison
                          Options: "cosine", "euclidean"
                          (default: "cosine")
        top_k: Number of results to return from retrieval
              (default: 3)
        chunk_size: Maximum size of text chunks in characters
                   (default: 500)
        chunk_overlap: Number of overlapping characters between chunks
                      (default: 50)
        expansion_strategy: Query expansion strategy for AI-enhanced retrieval
                           Options: "synonym_addition", "clarification", "decomposition"
                           (default: "synonym_addition")
        benchmark_queries: List of queries to use for benchmarking
                          (default: empty list)
    
    Example:
        >>> config = RAGConfig(
        ...     embedding_model="all-MiniLM-L6-v2",
        ...     vector_store_type="faiss",
        ...     similarity_metric="cosine",
        ...     top_k=5
        ... )
        >>> config.validate()
    """
    
    # Embedding settings
    embedding_model: str = "all-MiniLM-L6-v2"
    
    # Vector store settings
    vector_store_type: str = "faiss"  # "faiss", "chromadb", "numpy"
    similarity_metric: str = "cosine"  # "cosine", "euclidean"
    
    # Retrieval settings
    top_k: int = 3
    
    # Chunking settings
    chunk_size: int = 500  # characters
    chunk_overlap: int = 50  # characters
    
    # Query expansion settings
    expansion_strategy: str = "synonym_addition"  # "synonym_addition", "clarification", "decomposition"
    
    # Benchmark settings
    benchmark_queries: List[str] = field(default_factory=list)
    
    def validate(self) -> None:
        """Validate configuration values.
        
        This method checks that all configuration values are valid and
        within acceptable ranges. It raises ValueError with descriptive
        messages if any validation fails.
        
        Raises:
            ValueError: If any configuration value is invalid
        
        Example:
            >>> config = RAGConfig(top_k=-1)
            >>> config.validate()
            ValueError: top_k must be positive, got -1
        """
        # Validate embedding model (basic check - model existence checked at runtime)
        if not self.embedding_model or not isinstance(self.embedding_model, str):
            raise ValueError(
                f"embedding_model must be a non-empty string, got: {self.embedding_model}"
            )
        
        # Validate vector store type
        valid_store_types = ["faiss", "chromadb", "numpy"]
        if self.vector_store_type not in valid_store_types:
            raise ValueError(
                f"vector_store_type must be one of {valid_store_types}, "
                f"got: {self.vector_store_type}"
            )
        
        # Validate similarity metric
        valid_metrics = ["cosine", "euclidean"]
        if self.similarity_metric not in valid_metrics:
            raise ValueError(
                f"similarity_metric must be one of {valid_metrics}, "
                f"got: {self.similarity_metric}"
            )
        
        # Validate top_k
        if not isinstance(self.top_k, int) or self.top_k <= 0:
            raise ValueError(
                f"top_k must be a positive integer, got: {self.top_k}"
            )
        
        # Validate chunk_size
        if not isinstance(self.chunk_size, int) or self.chunk_size <= 0:
            raise ValueError(
                f"chunk_size must be a positive integer, got: {self.chunk_size}"
            )
        
        # Validate chunk_overlap
        if not isinstance(self.chunk_overlap, int) or self.chunk_overlap < 0:
            raise ValueError(
                f"chunk_overlap must be a non-negative integer, got: {self.chunk_overlap}"
            )
        
        # Validate chunk_overlap is less than chunk_size
        if self.chunk_overlap >= self.chunk_size:
            raise ValueError(
                f"chunk_overlap ({self.chunk_overlap}) must be less than "
                f"chunk_size ({self.chunk_size})"
            )
        
        # Validate expansion strategy
        valid_strategies = ["synonym_addition", "clarification", "decomposition"]
        if self.expansion_strategy not in valid_strategies:
            raise ValueError(
                f"expansion_strategy must be one of {valid_strategies}, "
                f"got: {self.expansion_strategy}"
            )
        
        # Validate benchmark_queries
        if not isinstance(self.benchmark_queries, list):
            raise ValueError(
                f"benchmark_queries must be a list, got: {type(self.benchmark_queries).__name__}"
            )
        
        # Validate each query in benchmark_queries
        for i, query in enumerate(self.benchmark_queries):
            if not isinstance(query, str):
                raise ValueError(
                    f"benchmark_queries[{i}] must be a string, "
                    f"got: {type(query).__name__}"
                )
            if not query.strip():
                raise ValueError(
                    f"benchmark_queries[{i}] cannot be empty or whitespace only"
                )
    
    def __post_init__(self):
        """Automatically validate configuration after initialization.
        
        This method is called automatically by the dataclass after __init__.
        It ensures that all configuration values are valid immediately upon
        object creation.
        """
        self.validate()
