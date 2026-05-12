"""Unit tests for the Orchestrator module."""

import pytest
import numpy as np
from src.orchestrator import RAGOrchestrator, IngestionStats, StrategyNotFoundError
from src.embedding import EmbeddingGenerator
from src.storage import NumpyVectorStore
from src.retrieval import RawVectorSearch, AIEnhancedRetrieval
from src.mocks import QueryExpander


@pytest.fixture
def embedding_generator():
    """Create an EmbeddingGenerator instance for testing."""
    return EmbeddingGenerator(model_name="all-MiniLM-L6-v2")


@pytest.fixture
def vector_store():
    """Create a NumpyVectorStore instance for testing."""
    return NumpyVectorStore(similarity_metric="cosine")


@pytest.fixture
def raw_strategy(embedding_generator, vector_store):
    """Create a RawVectorSearch strategy for testing."""
    return RawVectorSearch(embedding_generator, vector_store)


@pytest.fixture
def enhanced_strategy(embedding_generator, vector_store):
    """Create an AIEnhancedRetrieval strategy for testing."""
    query_expander = QueryExpander(expansion_strategy="synonym_addition")
    return AIEnhancedRetrieval(embedding_generator, vector_store, query_expander)


@pytest.fixture
def orchestrator(embedding_generator, vector_store, raw_strategy, enhanced_strategy):
    """Create a RAGOrchestrator instance for testing."""
    strategies = {
        "raw": raw_strategy,
        "enhanced": enhanced_strategy
    }
    return RAGOrchestrator(embedding_generator, vector_store, strategies)


class TestRAGOrchestratorInitialization:
    """Tests for RAGOrchestrator initialization."""
    
    def test_initialization_success(self, embedding_generator, vector_store, raw_strategy):
        """Test successful orchestrator initialization."""
        strategies = {"raw": raw_strategy}
        orchestrator = RAGOrchestrator(embedding_generator, vector_store, strategies)
        
        assert orchestrator.embedding_generator == embedding_generator
        assert orchestrator.vector_store == vector_store
        assert orchestrator.strategies == strategies
        assert orchestrator._total_chunks == 0
        assert orchestrator._embedding_dimension == embedding_generator.get_embedding_dimension()
    
    def test_initialization_empty_strategies(self, embedding_generator, vector_store):
        """Test that initialization fails with empty strategies dictionary."""
        with pytest.raises(ValueError, match="At least one retrieval strategy must be provided"):
            RAGOrchestrator(embedding_generator, vector_store, {})


class TestDocumentIngestion:
    """Tests for document ingestion functionality."""
    
    def test_ingest_single_document(self, orchestrator):
        """Test ingesting a single document."""
        documents = ["This is a test document for ingestion."]
        
        stats = orchestrator.ingest_documents(documents, chunk_size=500)
        
        assert isinstance(stats, IngestionStats)
        assert stats.total_chunks >= 1
        assert stats.embedding_dimension == orchestrator._embedding_dimension
        assert stats.total_tokens > 0
        assert stats.ingestion_time_ms > 0
    
    def test_ingest_multiple_documents(self, orchestrator):
        """Test ingesting multiple documents."""
        documents = [
            "First document about software architecture.",
            "Second document about system design.",
            "Third document about performance optimization."
        ]
        
        stats = orchestrator.ingest_documents(documents, chunk_size=500)
        
        assert stats.total_chunks >= 3
        assert stats.embedding_dimension == orchestrator._embedding_dimension
        assert stats.total_tokens > 0
        assert stats.ingestion_time_ms > 0
    
    def test_ingest_with_paragraphs(self, orchestrator):
        """Test ingesting documents with multiple paragraphs."""
        documents = [
            "First paragraph of the document.\n\nSecond paragraph of the document.\n\nThird paragraph."
        ]
        
        stats = orchestrator.ingest_documents(documents, chunk_size=500)
        
        # Should create at least 3 chunks (one per paragraph)
        assert stats.total_chunks >= 3
    
    def test_ingest_large_document_chunking(self, orchestrator):
        """Test that large documents are properly chunked."""
        # Create a document larger than chunk_size
        large_text = "This is a sentence. " * 100  # ~2000 characters
        documents = [large_text]
        
        stats = orchestrator.ingest_documents(documents, chunk_size=500)
        
        # Should create multiple chunks
        assert stats.total_chunks > 1
    
    def test_ingest_empty_documents_list(self, orchestrator):
        """Test that ingestion fails with empty documents list."""
        with pytest.raises(ValueError, match="Documents list cannot be empty"):
            orchestrator.ingest_documents([], chunk_size=500)
    
    def test_ingest_invalid_chunk_size(self, orchestrator):
        """Test that ingestion fails with invalid chunk_size."""
        documents = ["Test document"]
        
        with pytest.raises(ValueError, match="chunk_size must be positive"):
            orchestrator.ingest_documents(documents, chunk_size=0)
        
        with pytest.raises(ValueError, match="chunk_size must be positive"):
            orchestrator.ingest_documents(documents, chunk_size=-100)
    
    def test_ingest_updates_statistics(self, orchestrator):
        """Test that ingestion updates orchestrator statistics."""
        initial_chunks = orchestrator._total_chunks
        
        documents = ["First document.", "Second document."]
        stats = orchestrator.ingest_documents(documents, chunk_size=500)
        
        assert orchestrator._total_chunks == initial_chunks + stats.total_chunks
    
    def test_ingest_with_different_chunk_sizes(self, orchestrator):
        """Test ingestion with different chunk sizes."""
        document = "This is a test document. " * 50  # ~1250 characters
        
        # Ingest with large chunk size
        stats_large = orchestrator.ingest_documents([document], chunk_size=1000)
        
        # Create new orchestrator for comparison
        embedding_generator = EmbeddingGenerator()
        vector_store = NumpyVectorStore()
        raw_strategy = RawVectorSearch(embedding_generator, vector_store)
        orchestrator2 = RAGOrchestrator(embedding_generator, vector_store, {"raw": raw_strategy})
        
        # Ingest with small chunk size
        stats_small = orchestrator2.ingest_documents([document], chunk_size=200)
        
        # Smaller chunk size should create more chunks
        assert stats_small.total_chunks > stats_large.total_chunks
    
    def test_ingest_skips_invalid_documents(self, orchestrator):
        """Test that ingestion skips invalid documents with warning."""
        documents = [
            "Valid document.",
            None,  # Invalid
            "Another valid document."
        ]
        
        with pytest.warns(UserWarning, match="Skipping invalid document"):
            stats = orchestrator.ingest_documents(documents, chunk_size=500)
        
        # Should still process valid documents
        assert stats.total_chunks >= 2


class TestRetrievalCoordination:
    """Tests for retrieval coordination functionality."""
    
    def test_retrieve_with_raw_strategy(self, orchestrator):
        """Test retrieval using raw vector search strategy."""
        # First ingest some documents
        documents = [
            "Python is a programming language.",
            "Machine learning uses algorithms.",
            "Data science involves statistics."
        ]
        orchestrator.ingest_documents(documents, chunk_size=500)
        
        # Retrieve using raw strategy
        result = orchestrator.retrieve("programming", strategy_name="raw", k=2)
        
        assert result.strategy_name == "RawVectorSearch"
        assert result.query == "programming"
        assert result.expanded_query is None
        assert len(result.chunks) <= 2
        assert len(result.scores) == len(result.chunks)
    
    def test_retrieve_with_enhanced_strategy(self, orchestrator):
        """Test retrieval using AI-enhanced strategy."""
        # First ingest some documents
        documents = [
            "Python is a programming language.",
            "Machine learning uses algorithms.",
            "Data science involves statistics."
        ]
        orchestrator.ingest_documents(documents, chunk_size=500)
        
        # Retrieve using enhanced strategy
        result = orchestrator.retrieve("programming", strategy_name="enhanced", k=2)
        
        assert result.strategy_name == "AIEnhancedRetrieval"
        assert result.query == "programming"
        assert result.expanded_query is not None
        assert result.expanded_query != result.query
        assert len(result.chunks) <= 2
        assert len(result.scores) == len(result.chunks)
    
    def test_retrieve_unknown_strategy(self, orchestrator):
        """Test that retrieval fails with unknown strategy name."""
        documents = ["Test document."]
        orchestrator.ingest_documents(documents, chunk_size=500)
        
        with pytest.raises(StrategyNotFoundError, match="Unknown strategy 'unknown'"):
            orchestrator.retrieve("test query", strategy_name="unknown", k=3)
    
    def test_retrieve_empty_query(self, orchestrator):
        """Test that retrieval fails with empty query."""
        documents = ["Test document."]
        orchestrator.ingest_documents(documents, chunk_size=500)
        
        with pytest.raises(ValueError, match="Query"):
            orchestrator.retrieve("", strategy_name="raw", k=3)
    
    def test_retrieve_invalid_k(self, orchestrator):
        """Test that retrieval fails with invalid k value."""
        documents = ["Test document."]
        orchestrator.ingest_documents(documents, chunk_size=500)
        
        with pytest.raises(ValueError, match="k must be positive"):
            orchestrator.retrieve("test query", strategy_name="raw", k=0)


class TestStatisticsAndMonitoring:
    """Tests for statistics and monitoring functionality."""
    
    def test_get_statistics_initial(self, orchestrator):
        """Test getting statistics before any ingestion."""
        stats = orchestrator.get_statistics()
        
        assert isinstance(stats, dict)
        assert stats["total_chunks"] == 0
        assert stats["embedding_dimension"] == orchestrator._embedding_dimension
        assert "raw" in stats["available_strategies"]
        assert "enhanced" in stats["available_strategies"]
    
    def test_get_statistics_after_ingestion(self, orchestrator):
        """Test getting statistics after document ingestion."""
        documents = ["First document.", "Second document.", "Third document."]
        ingestion_stats = orchestrator.ingest_documents(documents, chunk_size=500)
        
        stats = orchestrator.get_statistics()
        
        assert stats["total_chunks"] == ingestion_stats.total_chunks
        assert stats["embedding_dimension"] == orchestrator._embedding_dimension
        assert len(stats["available_strategies"]) == 2
    
    def test_statistics_accumulate_across_ingestions(self, orchestrator):
        """Test that statistics accumulate across multiple ingestions."""
        # First ingestion
        documents1 = ["First batch document."]
        stats1 = orchestrator.ingest_documents(documents1, chunk_size=500)
        
        # Second ingestion
        documents2 = ["Second batch document."]
        stats2 = orchestrator.ingest_documents(documents2, chunk_size=500)
        
        # Get final statistics
        final_stats = orchestrator.get_statistics()
        
        assert final_stats["total_chunks"] == stats1.total_chunks + stats2.total_chunks


class TestChunkingBehavior:
    """Tests for document chunking behavior."""
    
    def test_chunk_by_double_newlines(self, orchestrator):
        """Test chunking by double newlines (paragraphs)."""
        document = "First paragraph.\n\nSecond paragraph.\n\nThird paragraph."
        chunks = orchestrator._chunk_document(document, chunk_size=500)
        
        assert len(chunks) == 3
        assert "First paragraph" in chunks[0]
        assert "Second paragraph" in chunks[1]
        assert "Third paragraph" in chunks[2]
    
    def test_chunk_by_single_newlines(self, orchestrator):
        """Test chunking by single newlines when no double newlines exist."""
        document = "First line.\nSecond line.\nThird line."
        chunks = orchestrator._chunk_document(document, chunk_size=500)
        
        assert len(chunks) == 3
    
    def test_chunk_large_paragraph(self, orchestrator):
        """Test that large paragraphs are split into smaller chunks."""
        # Create a paragraph larger than chunk_size
        large_paragraph = "This is a sentence. " * 100  # ~2000 characters
        chunks = orchestrator._chunk_document(large_paragraph, chunk_size=500)
        
        # Should create multiple chunks
        assert len(chunks) > 1
        
        # Each chunk should be approximately chunk_size or smaller
        for chunk in chunks:
            assert len(chunk) <= 600  # Allow some flexibility
    
    def test_chunk_skips_empty_paragraphs(self, orchestrator):
        """Test that empty paragraphs are skipped."""
        document = "First paragraph.\n\n\n\nSecond paragraph."
        chunks = orchestrator._chunk_document(document, chunk_size=500)
        
        assert len(chunks) == 2
        assert all(chunk.strip() for chunk in chunks)
    
    def test_chunk_single_paragraph_document(self, orchestrator):
        """Test chunking a document with no paragraph breaks."""
        document = "This is a single paragraph document without any breaks."
        chunks = orchestrator._chunk_document(document, chunk_size=500)
        
        assert len(chunks) == 1
        assert chunks[0] == document


class TestEndToEndIntegration:
    """End-to-end integration tests for the orchestrator."""
    
    def test_complete_pipeline(self, orchestrator):
        """Test complete ingestion and retrieval pipeline."""
        # Ingest documents
        documents = [
            "Python is a high-level programming language known for its simplicity.",
            "Machine learning is a subset of artificial intelligence.",
            "Data science combines statistics, programming, and domain knowledge."
        ]
        
        ingestion_stats = orchestrator.ingest_documents(documents, chunk_size=500)
        
        # Verify ingestion
        assert ingestion_stats.total_chunks >= 3
        
        # Retrieve with raw strategy
        raw_result = orchestrator.retrieve("programming language", strategy_name="raw", k=2)
        assert len(raw_result.chunks) > 0
        assert raw_result.expanded_query is None
        
        # Retrieve with enhanced strategy
        enhanced_result = orchestrator.retrieve("programming language", strategy_name="enhanced", k=2)
        assert len(enhanced_result.chunks) > 0
        assert enhanced_result.expanded_query is not None
        
        # Verify statistics
        stats = orchestrator.get_statistics()
        assert stats["total_chunks"] == ingestion_stats.total_chunks
    
    def test_multiple_ingestion_and_retrieval_cycles(self, orchestrator):
        """Test multiple cycles of ingestion and retrieval."""
        # First cycle
        documents1 = ["First batch of documents about Python programming."]
        orchestrator.ingest_documents(documents1, chunk_size=500)
        result1 = orchestrator.retrieve("Python", strategy_name="raw", k=1)
        assert len(result1.chunks) > 0
        
        # Second cycle
        documents2 = ["Second batch of documents about machine learning."]
        orchestrator.ingest_documents(documents2, chunk_size=500)
        result2 = orchestrator.retrieve("machine learning", strategy_name="raw", k=1)
        assert len(result2.chunks) > 0
        
        # Verify both document sets are searchable
        stats = orchestrator.get_statistics()
        assert stats["total_chunks"] >= 2
