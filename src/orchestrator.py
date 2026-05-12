"""Orchestrator Module for Context-Aware Retrieval Engine.

This module provides the RAGOrchestrator class that coordinates the complete
ingestion and retrieval pipeline, managing document processing, embedding
generation, vector storage, and retrieval strategy execution.
"""

from dataclasses import dataclass
from typing import List, Dict, Optional
import time
import re

from src.embedding import EmbeddingGenerator
from src.storage import VectorStore
from src.retrieval import RetrievalStrategy, RetrievalResult


@dataclass
class IngestionStats:
    """Statistics from document ingestion.
    
    Attributes:
        total_chunks: Total number of text chunks created
        embedding_dimension: Dimensionality of generated embeddings
        total_tokens: Approximate total token count (estimated)
        ingestion_time_ms: Total ingestion time in milliseconds
    """
    total_chunks: int
    embedding_dimension: int
    total_tokens: int
    ingestion_time_ms: float


class StrategyNotFoundError(Exception):
    """Raised when an unknown retrieval strategy name is requested."""
    pass


class RAGOrchestrator:
    """Coordinates ingestion and retrieval pipeline.
    
    The RAGOrchestrator manages the complete RAG pipeline, including:
    - Document ingestion with chunking and embedding generation
    - Vector storage management
    - Retrieval strategy coordination
    - Statistics and monitoring
    
    This class serves as the main entry point for using the retrieval engine.
    """
    
    def __init__(self, 
                 embedding_generator: EmbeddingGenerator,
                 vector_store: VectorStore,
                 strategies: Dict[str, RetrievalStrategy]):
        """Initialize RAGOrchestrator with required dependencies.
        
        Args:
            embedding_generator: Component for generating text embeddings
            vector_store: Component for storing and searching embeddings
            strategies: Dictionary mapping strategy names to RetrievalStrategy instances
                       Example: {"raw": RawVectorSearch(...), "enhanced": AIEnhancedRetrieval(...)}
        
        Raises:
            ValueError: If strategies dictionary is empty
        """
        if not strategies:
            raise ValueError("At least one retrieval strategy must be provided.")
        
        self.embedding_generator = embedding_generator
        self.vector_store = vector_store
        self.strategies = strategies
        
        # Statistics tracking
        self._total_chunks = 0
        self._embedding_dimension = embedding_generator.get_embedding_dimension()
    
    def ingest_documents(self, documents: List[str], chunk_size: int = 500) -> IngestionStats:
        """Process documents through ingestion pipeline.
        
        This method performs the following steps:
        1. Split documents into chunks (by paragraph or fixed size)
        2. Generate embeddings for all chunks
        3. Store embeddings and text in the vector store
        4. Track and return ingestion statistics
        
        Args:
            documents: List of document strings to ingest
            chunk_size: Maximum size of each chunk in characters (default: 500)
        
        Returns:
            IngestionStats containing ingestion metrics
        
        Raises:
            ValueError: If documents list is empty or chunk_size is invalid
        """
        # Validate inputs
        if not documents or len(documents) == 0:
            raise ValueError("Documents list cannot be empty.")
        
        if chunk_size <= 0:
            raise ValueError(f"chunk_size must be positive, got {chunk_size}")
        
        # Start timing
        start_time = time.time()
        
        # Split documents into chunks
        all_chunks = []
        for doc in documents:
            if not doc or not isinstance(doc, str):
                import warnings
                warnings.warn(
                    f"Skipping invalid document (type: {type(doc).__name__})",
                    UserWarning
                )
                continue
            
            chunks = self._chunk_document(doc, chunk_size)
            all_chunks.extend(chunks)
        
        if len(all_chunks) == 0:
            raise ValueError("No valid chunks were created from the provided documents.")
        
        # Generate embeddings for all chunks
        embeddings = self.embedding_generator.encode(all_chunks)
        
        # Store embeddings and text in vector store
        # Create metadata for each chunk
        metadata = [{"chunk_index": i, "source": "document"} for i in range(len(all_chunks))]
        self.vector_store.add(embeddings, all_chunks, metadata)
        
        # Update statistics
        self._total_chunks += len(all_chunks)
        
        # Calculate approximate token count (rough estimate: 1 token ≈ 4 characters)
        total_chars = sum(len(chunk) for chunk in all_chunks)
        total_tokens = total_chars // 4
        
        # Calculate ingestion time
        end_time = time.time()
        ingestion_time_ms = (end_time - start_time) * 1000
        
        # Return statistics
        return IngestionStats(
            total_chunks=len(all_chunks),
            embedding_dimension=self._embedding_dimension,
            total_tokens=total_tokens,
            ingestion_time_ms=ingestion_time_ms
        )
    
    def _chunk_document(self, document: str, chunk_size: int) -> List[str]:
        """Split a document into chunks by paragraph or fixed size.
        
        This method first attempts to split by paragraphs (double newlines).
        If paragraphs are larger than chunk_size, they are further split
        into fixed-size chunks with some overlap.
        
        Args:
            document: The document text to chunk
            chunk_size: Maximum size of each chunk in characters
        
        Returns:
            List of text chunks
        """
        # First, split by paragraphs (double newlines or single newlines)
        # Try double newlines first
        paragraphs = re.split(r'\n\s*\n', document)
        
        # If no double newlines found, try single newlines
        if len(paragraphs) == 1:
            paragraphs = document.split('\n')
        
        # If still only one paragraph, treat the whole document as one paragraph
        if len(paragraphs) == 1:
            paragraphs = [document]
        
        # Process each paragraph
        chunks = []
        for paragraph in paragraphs:
            paragraph = paragraph.strip()
            
            # Skip empty paragraphs
            if not paragraph:
                continue
            
            # If paragraph fits within chunk_size, add it as-is
            if len(paragraph) <= chunk_size:
                chunks.append(paragraph)
            else:
                # Split large paragraph into fixed-size chunks with overlap
                overlap = min(50, chunk_size // 10)  # 10% overlap or 50 chars
                
                start = 0
                while start < len(paragraph):
                    end = start + chunk_size
                    
                    # If this is not the last chunk, try to break at a word boundary
                    if end < len(paragraph):
                        # Look for the last space before the end
                        last_space = paragraph.rfind(' ', start, end)
                        if last_space > start:
                            end = last_space
                    
                    chunk = paragraph[start:end].strip()
                    if chunk:
                        chunks.append(chunk)
                    
                    # Move start position with overlap
                    start = end - overlap if end < len(paragraph) else end
        
        return chunks
    
    def retrieve(self, query: str, strategy_name: str, k: int = 3) -> RetrievalResult:
        """Execute retrieval using specified strategy.
        
        This method routes the query to the appropriate retrieval strategy
        and returns the results.
        
        Args:
            query: The user query string
            strategy_name: Name of the retrieval strategy to use
                          (must match a key in the strategies dictionary)
            k: Number of results to return (default: 3)
        
        Returns:
            RetrievalResult containing chunks, scores, and metadata
        
        Raises:
            StrategyNotFoundError: If strategy_name is not found in available strategies
            ValueError: If query is empty or k is invalid
        """
        # Validate strategy name
        if strategy_name not in self.strategies:
            available = ", ".join(self.strategies.keys())
            raise StrategyNotFoundError(
                f"Unknown strategy '{strategy_name}'. "
                f"Available strategies: {available}"
            )
        
        # Get the strategy and execute retrieval
        strategy = self.strategies[strategy_name]
        return strategy.retrieve(query, k)
    
    def get_statistics(self) -> Dict:
        """Return ingestion statistics and system information.
        
        Returns:
            Dictionary containing:
            - total_chunks: Total number of chunks stored
            - embedding_dimension: Dimensionality of embeddings
            - available_strategies: List of available retrieval strategy names
        """
        return {
            "total_chunks": self._total_chunks,
            "embedding_dimension": self._embedding_dimension,
            "available_strategies": list(self.strategies.keys())
        }
