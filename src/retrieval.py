"""Retrieval Strategies Module for Context-Aware Retrieval Engine.

This module provides retrieval strategy implementations for semantic search,
including raw vector search and AI-enhanced retrieval with query expansion.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Optional
import time
import numpy as np

from src.embedding import EmbeddingGenerator
from src.storage import VectorStore, SearchResult
from src.mocks import QueryExpander


@dataclass
class RetrievalResult:
    """Complete retrieval result with metadata.
    
    Attributes:
        query: The original user query string
        expanded_query: The expanded query (None for raw search)
        chunks: List of retrieved text chunks
        scores: List of similarity scores corresponding to chunks
        latency_ms: Retrieval latency in milliseconds
        strategy_name: Name of the retrieval strategy used
    """
    query: str
    expanded_query: Optional[str]
    chunks: List[str]
    scores: List[float]
    latency_ms: float
    strategy_name: str


class RetrievalStrategy(ABC):
    """Abstract interface for retrieval strategies.
    
    All retrieval strategy implementations must provide a retrieve method
    that takes a query and returns a RetrievalResult.
    """
    
    @abstractmethod
    def retrieve(self, query: str, k: int = 3) -> RetrievalResult:
        """Execute retrieval strategy.
        
        Args:
            query: The user query string
            k: Number of results to return (default: 3)
        
        Returns:
            RetrievalResult containing chunks, scores, and metadata
        
        Raises:
            ValueError: If query is empty or k is invalid
        """
        pass


class RawVectorSearch(RetrievalStrategy):
    """Direct embedding-based similarity search.
    
    This strategy performs straightforward semantic search by:
    1. Generating an embedding for the user query
    2. Searching the vector store for the most similar embeddings
    3. Returning the associated text chunks with similarity scores
    
    No query modification or expansion is performed.
    """
    
    def __init__(self, embedding_generator: EmbeddingGenerator, vector_store: VectorStore):
        """Initialize RawVectorSearch with required dependencies.
        
        Args:
            embedding_generator: Component for generating text embeddings
            vector_store: Component for storing and searching embeddings
        """
        self.embedding_generator = embedding_generator
        self.vector_store = vector_store
        self.strategy_name = "RawVectorSearch"
    
    def retrieve(self, query: str, k: int = 3) -> RetrievalResult:
        """Execute raw vector search retrieval.
        
        Args:
            query: The user query string
            k: Number of results to return (default: 3)
        
        Returns:
            RetrievalResult with original query and top-k similar chunks
        
        Raises:
            ValueError: If query is empty or k is invalid
        """
        # Validate inputs
        if not query or not isinstance(query, str):
            raise ValueError("Query must be a non-empty string.")
        
        if query.strip() == "":
            raise ValueError("Query cannot be empty or whitespace only.")
        
        if k <= 0:
            raise ValueError(f"k must be positive, got {k}")
        
        # Start timing
        start_time = time.time()
        
        # Generate query embedding
        query_embedding = self.embedding_generator.encode(query)
        
        # Search vector store for top-k results
        search_results: List[SearchResult] = self.vector_store.search(query_embedding, k=k)
        
        # Extract chunks and scores
        chunks = [result.text for result in search_results]
        scores = [result.score for result in search_results]
        
        # Calculate latency
        end_time = time.time()
        latency_ms = (end_time - start_time) * 1000
        
        # Return result with original query (no expansion)
        return RetrievalResult(
            query=query,
            expanded_query=None,
            chunks=chunks,
            scores=scores,
            latency_ms=latency_ms,
            strategy_name=self.strategy_name
        )


class AIEnhancedRetrieval(RetrievalStrategy):
    """Query expansion followed by similarity search.
    
    This strategy enhances retrieval by:
    1. Expanding the user query using a query expander (mock LLM)
    2. Generating an embedding for the expanded query
    3. Searching the vector store for the most similar embeddings
    4. Returning the associated text chunks with both original and expanded queries
    
    Query expansion helps address query-document mismatch by adding synonyms,
    clarifications, or decomposing complex queries.
    """
    
    def __init__(self, 
                 embedding_generator: EmbeddingGenerator, 
                 vector_store: VectorStore,
                 query_expander: QueryExpander):
        """Initialize AIEnhancedRetrieval with required dependencies.
        
        Args:
            embedding_generator: Component for generating text embeddings
            vector_store: Component for storing and searching embeddings
            query_expander: Component for expanding/rewriting queries
        """
        self.embedding_generator = embedding_generator
        self.vector_store = vector_store
        self.query_expander = query_expander
        self.strategy_name = "AIEnhancedRetrieval"
    
    def retrieve(self, query: str, k: int = 3) -> RetrievalResult:
        """Execute AI-enhanced retrieval with query expansion.
        
        Args:
            query: The user query string
            k: Number of results to return (default: 3)
        
        Returns:
            RetrievalResult with both original and expanded queries, plus top-k chunks
        
        Raises:
            ValueError: If query is empty or k is invalid
        """
        # Validate inputs
        if not query or not isinstance(query, str):
            raise ValueError("Query must be a non-empty string.")
        
        if query.strip() == "":
            raise ValueError("Query cannot be empty or whitespace only.")
        
        if k <= 0:
            raise ValueError(f"k must be positive, got {k}")
        
        # Start timing
        start_time = time.time()
        
        # Expand query using query expander
        expanded_query = self.query_expander.expand_query(query)
        
        # Generate embedding for expanded query
        query_embedding = self.embedding_generator.encode(expanded_query)
        
        # Search vector store for top-k results
        search_results: List[SearchResult] = self.vector_store.search(query_embedding, k=k)
        
        # Extract chunks and scores
        chunks = [result.text for result in search_results]
        scores = [result.score for result in search_results]
        
        # Calculate latency
        end_time = time.time()
        latency_ms = (end_time - start_time) * 1000
        
        # Return result with both original and expanded query
        return RetrievalResult(
            query=query,
            expanded_query=expanded_query,
            chunks=chunks,
            scores=scores,
            latency_ms=latency_ms,
            strategy_name=self.strategy_name
        )
