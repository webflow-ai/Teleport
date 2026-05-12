"""Data Models Module for Context-Aware Retrieval Engine.

This module consolidates all data models used throughout the RAG system,
providing a central location for data structure definitions. These models
are also available from their original modules for backward compatibility.

Data Models:
    - SearchResult: Single search result from vector store
    - RetrievalResult: Complete retrieval result with metadata
    - BenchmarkMetrics: Aggregated benchmark results
    - IngestionStats: Statistics from document ingestion
"""

from dataclasses import dataclass
from typing import List, Optional, Dict


@dataclass
class SearchResult:
    """Single search result from vector store.
    
    Represents a single retrieved item from a vector similarity search,
    including the original text, similarity score, and optional metadata.
    
    Attributes:
        text: The original text associated with the embedding
        score: Similarity score (higher is more similar for cosine,
               lower is more similar for euclidean distance)
        metadata: Optional metadata dictionary containing additional information
                 about the result (e.g., source document, chunk index)
    
    Example:
        >>> result = SearchResult(
        ...     text="The system handles peak load by scaling horizontally.",
        ...     score=0.87,
        ...     metadata={"chunk_index": 5, "source": "architecture_doc"}
        ... )
    """
    text: str
    score: float
    metadata: Optional[Dict] = None


@dataclass
class RetrievalResult:
    """Complete retrieval result with metadata.
    
    Represents the complete result of a retrieval operation, including
    the original query, any query expansion, retrieved chunks, similarity
    scores, latency metrics, and the strategy used.
    
    Attributes:
        query: The original user query string
        expanded_query: The expanded query (None for raw search, populated
                       for AI-enhanced retrieval)
        chunks: List of retrieved text chunks, ordered by similarity
        scores: List of similarity scores corresponding to each chunk
        latency_ms: Retrieval latency in milliseconds
        strategy_name: Name of the retrieval strategy used
                      (e.g., "RawVectorSearch", "AIEnhancedRetrieval")
    
    Example:
        >>> result = RetrievalResult(
        ...     query="How does the system handle peak load?",
        ...     expanded_query="How does the system handle peak load? process manage traffic",
        ...     chunks=["The system scales horizontally...", "Load balancing is used..."],
        ...     scores=[0.87, 0.82],
        ...     latency_ms=45.3,
        ...     strategy_name="AIEnhancedRetrieval"
        ... )
    """
    query: str
    expanded_query: Optional[str]
    chunks: List[str]
    scores: List[float]
    latency_ms: float
    strategy_name: str


@dataclass
class BenchmarkMetrics:
    """Aggregated benchmark results for a retrieval strategy.
    
    Represents the aggregated performance metrics for a retrieval strategy
    across multiple queries, including quality metrics (similarity scores,
    diversity) and performance metrics (latency).
    
    Attributes:
        strategy_name: Name of the retrieval strategy being evaluated
        avg_similarity_score: Average similarity score across all queries
                             and all retrieved chunks
        unique_chunks_retrieved: Number of unique chunks retrieved across
                                all queries (measures diversity)
        avg_latency_ms: Average retrieval latency in milliseconds across
                       all queries
        query_results: List of individual RetrievalResult objects for each
                      query in the benchmark
    
    Example:
        >>> metrics = BenchmarkMetrics(
        ...     strategy_name="RawVectorSearch",
        ...     avg_similarity_score=0.78,
        ...     unique_chunks_retrieved=12,
        ...     avg_latency_ms=38.5,
        ...     query_results=[result1, result2, result3]
        ... )
    """
    strategy_name: str
    avg_similarity_score: float
    unique_chunks_retrieved: int
    avg_latency_ms: float
    query_results: List[RetrievalResult]


@dataclass
class IngestionStats:
    """Statistics from document ingestion.
    
    Represents metrics collected during the document ingestion process,
    including chunk counts, embedding dimensions, token estimates, and
    processing time.
    
    Attributes:
        total_chunks: Total number of text chunks created from documents
        embedding_dimension: Dimensionality of generated embeddings
                            (e.g., 384 for all-MiniLM-L6-v2)
        total_tokens: Approximate total token count (estimated as
                     total_characters / 4)
        ingestion_time_ms: Total ingestion time in milliseconds, including
                          chunking, embedding generation, and storage
    
    Example:
        >>> stats = IngestionStats(
        ...     total_chunks=47,
        ...     embedding_dimension=384,
        ...     total_tokens=5823,
        ...     ingestion_time_ms=1234.5
        ... )
    """
    total_chunks: int
    embedding_dimension: int
    total_tokens: int
    ingestion_time_ms: float


# Re-export note:
# These models are also available from their original modules:
# - SearchResult: from src.storage import SearchResult
# - RetrievalResult: from src.retrieval import RetrievalResult
# - BenchmarkMetrics: from src.benchmark import BenchmarkMetrics
# - IngestionStats: from src.orchestrator import IngestionStats
#
# This module provides a convenient central import location:
# from src.models import SearchResult, RetrievalResult, BenchmarkMetrics, IngestionStats
