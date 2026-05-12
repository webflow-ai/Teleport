"""Tests for retrieval strategies module."""

import pytest
import numpy as np
from src.retrieval import (
    RetrievalStrategy,
    RetrievalResult,
    RawVectorSearch,
    AIEnhancedRetrieval
)
from src.embedding import EmbeddingGenerator
from src.storage import NumpyVectorStore
from src.mocks import QueryExpander


class TestRetrievalResult:
    """Tests for RetrievalResult dataclass."""
    
    def test_retrieval_result_creation(self):
        """Test creating a RetrievalResult instance."""
        result = RetrievalResult(
            query="test query",
            expanded_query="expanded test query",
            chunks=["chunk1", "chunk2"],
            scores=[0.9, 0.8],
            latency_ms=50.5,
            strategy_name="TestStrategy"
        )
        
        assert result.query == "test query"
        assert result.expanded_query == "expanded test query"
        assert result.chunks == ["chunk1", "chunk2"]
        assert result.scores == [0.9, 0.8]
        assert result.latency_ms == 50.5
        assert result.strategy_name == "TestStrategy"
    
    def test_retrieval_result_with_none_expanded_query(self):
        """Test RetrievalResult with None expanded_query (for raw search)."""
        result = RetrievalResult(
            query="test query",
            expanded_query=None,
            chunks=["chunk1"],
            scores=[0.9],
            latency_ms=30.0,
            strategy_name="RawVectorSearch"
        )
        
        assert result.expanded_query is None


class TestRawVectorSearch:
    """Tests for RawVectorSearch strategy."""
    
    @pytest.fixture
    def setup_components(self):
        """Set up components for testing."""
        # Create embedding generator
        embedding_generator = EmbeddingGenerator()
        
        # Create vector store and add some sample data
        vector_store = NumpyVectorStore(similarity_metric="cosine")
        
        # Add sample documents
        sample_texts = [
            "Python is a high-level programming language.",
            "Machine learning uses algorithms to learn from data.",
            "Vector databases store embeddings for similarity search."
        ]
        
        embeddings = embedding_generator.encode(sample_texts)
        vector_store.add(embeddings, sample_texts)
        
        return embedding_generator, vector_store
    
    def test_raw_vector_search_initialization(self, setup_components):
        """Test RawVectorSearch initialization."""
        embedding_generator, vector_store = setup_components
        
        strategy = RawVectorSearch(embedding_generator, vector_store)
        
        assert strategy.embedding_generator is embedding_generator
        assert strategy.vector_store is vector_store
        assert strategy.strategy_name == "RawVectorSearch"
    
    def test_raw_vector_search_retrieve(self, setup_components):
        """Test basic retrieval with RawVectorSearch."""
        embedding_generator, vector_store = setup_components
        strategy = RawVectorSearch(embedding_generator, vector_store)
        
        result = strategy.retrieve("What is Python?", k=2)
        
        assert isinstance(result, RetrievalResult)
        assert result.query == "What is Python?"
        assert result.expanded_query is None  # Raw search doesn't expand
        assert len(result.chunks) <= 2
        assert len(result.scores) == len(result.chunks)
        assert result.latency_ms > 0
        assert result.strategy_name == "RawVectorSearch"
    
    def test_raw_vector_search_returns_top_k(self, setup_components):
        """Test that RawVectorSearch returns exactly k results."""
        embedding_generator, vector_store = setup_components
        strategy = RawVectorSearch(embedding_generator, vector_store)
        
        result = strategy.retrieve("programming", k=3)
        
        # Should return min(k, store_size) = min(3, 3) = 3
        assert len(result.chunks) == 3
        assert len(result.scores) == 3
    
    def test_raw_vector_search_k_greater_than_store_size(self, setup_components):
        """Test retrieval when k > number of stored items."""
        embedding_generator, vector_store = setup_components
        strategy = RawVectorSearch(embedding_generator, vector_store)
        
        result = strategy.retrieve("test query", k=10)
        
        # Should return all 3 items (store size)
        assert len(result.chunks) == 3
        assert len(result.scores) == 3
    
    def test_raw_vector_search_similarity_scores(self, setup_components):
        """Test that similarity scores are present and valid."""
        embedding_generator, vector_store = setup_components
        strategy = RawVectorSearch(embedding_generator, vector_store)
        
        result = strategy.retrieve("Python programming", k=3)
        
        # All scores should be present
        assert len(result.scores) == len(result.chunks)
        
        # Scores should be in valid range for cosine similarity
        for score in result.scores:
            assert isinstance(score, float)
            assert score >= -1.0 and score <= 1.0
    
    def test_raw_vector_search_query_immutability(self, setup_components):
        """Test that original query is not modified."""
        embedding_generator, vector_store = setup_components
        strategy = RawVectorSearch(embedding_generator, vector_store)
        
        original_query = "What is machine learning?"
        result = strategy.retrieve(original_query, k=2)
        
        # Query should remain unchanged
        assert result.query == original_query
        assert result.expanded_query is None
    
    def test_raw_vector_search_empty_query_raises_error(self, setup_components):
        """Test that empty query raises ValueError."""
        embedding_generator, vector_store = setup_components
        strategy = RawVectorSearch(embedding_generator, vector_store)
        
        with pytest.raises(ValueError, match="Query must be a non-empty string"):
            strategy.retrieve("", k=3)
    
    def test_raw_vector_search_invalid_k_raises_error(self, setup_components):
        """Test that invalid k value raises ValueError."""
        embedding_generator, vector_store = setup_components
        strategy = RawVectorSearch(embedding_generator, vector_store)
        
        with pytest.raises(ValueError, match="k must be positive"):
            strategy.retrieve("test query", k=0)
        
        with pytest.raises(ValueError, match="k must be positive"):
            strategy.retrieve("test query", k=-1)
    
    def test_raw_vector_search_latency_measurement(self, setup_components):
        """Test that latency is measured and recorded."""
        embedding_generator, vector_store = setup_components
        strategy = RawVectorSearch(embedding_generator, vector_store)
        
        result = strategy.retrieve("test query", k=3)
        
        # Latency should be positive
        assert result.latency_ms > 0
        # Latency should be reasonable (less than 5 seconds for this small test)
        assert result.latency_ms < 5000


class TestAIEnhancedRetrieval:
    """Tests for AIEnhancedRetrieval strategy."""
    
    @pytest.fixture
    def setup_components(self):
        """Set up components for testing."""
        # Create embedding generator
        embedding_generator = EmbeddingGenerator()
        
        # Create vector store and add some sample data
        vector_store = NumpyVectorStore(similarity_metric="cosine")
        
        # Add sample documents
        sample_texts = [
            "Python is a high-level programming language.",
            "Machine learning uses algorithms to learn from data.",
            "Vector databases store embeddings for similarity search."
        ]
        
        embeddings = embedding_generator.encode(sample_texts)
        vector_store.add(embeddings, sample_texts)
        
        # Create query expander
        query_expander = QueryExpander(expansion_strategy="synonym_addition")
        
        return embedding_generator, vector_store, query_expander
    
    def test_ai_enhanced_retrieval_initialization(self, setup_components):
        """Test AIEnhancedRetrieval initialization."""
        embedding_generator, vector_store, query_expander = setup_components
        
        strategy = AIEnhancedRetrieval(embedding_generator, vector_store, query_expander)
        
        assert strategy.embedding_generator is embedding_generator
        assert strategy.vector_store is vector_store
        assert strategy.query_expander is query_expander
        assert strategy.strategy_name == "AIEnhancedRetrieval"
    
    def test_ai_enhanced_retrieval_retrieve(self, setup_components):
        """Test basic retrieval with AIEnhancedRetrieval."""
        embedding_generator, vector_store, query_expander = setup_components
        strategy = AIEnhancedRetrieval(embedding_generator, vector_store, query_expander)
        
        result = strategy.retrieve("What is Python?", k=2)
        
        assert isinstance(result, RetrievalResult)
        assert result.query == "What is Python?"
        assert result.expanded_query is not None  # Should be expanded
        assert result.expanded_query != result.query  # Should differ from original
        assert len(result.chunks) <= 2
        assert len(result.scores) == len(result.chunks)
        assert result.latency_ms > 0
        assert result.strategy_name == "AIEnhancedRetrieval"
    
    def test_ai_enhanced_retrieval_query_expansion_occurs(self, setup_components):
        """Test that query expansion actually occurs."""
        embedding_generator, vector_store, query_expander = setup_components
        strategy = AIEnhancedRetrieval(embedding_generator, vector_store, query_expander)
        
        original_query = "How does the system handle load?"
        result = strategy.retrieve(original_query, k=3)
        
        # Expanded query should differ from original
        assert result.expanded_query != original_query
        # Both queries should be preserved
        assert result.query == original_query
    
    def test_ai_enhanced_retrieval_dual_query_preservation(self, setup_components):
        """Test that both original and expanded queries are preserved."""
        embedding_generator, vector_store, query_expander = setup_components
        strategy = AIEnhancedRetrieval(embedding_generator, vector_store, query_expander)
        
        result = strategy.retrieve("machine learning", k=2)
        
        # Both queries should be present
        assert result.query is not None
        assert result.expanded_query is not None
        # Original query should be unchanged
        assert result.query == "machine learning"
    
    def test_ai_enhanced_retrieval_returns_top_k(self, setup_components):
        """Test that AIEnhancedRetrieval returns exactly k results."""
        embedding_generator, vector_store, query_expander = setup_components
        strategy = AIEnhancedRetrieval(embedding_generator, vector_store, query_expander)
        
        result = strategy.retrieve("programming", k=3)
        
        # Should return min(k, store_size) = min(3, 3) = 3
        assert len(result.chunks) == 3
        assert len(result.scores) == 3
    
    def test_ai_enhanced_retrieval_similarity_scores(self, setup_components):
        """Test that similarity scores are present and valid."""
        embedding_generator, vector_store, query_expander = setup_components
        strategy = AIEnhancedRetrieval(embedding_generator, vector_store, query_expander)
        
        result = strategy.retrieve("Python programming", k=3)
        
        # All scores should be present
        assert len(result.scores) == len(result.chunks)
        
        # Scores should be in valid range for cosine similarity
        for score in result.scores:
            assert isinstance(score, float)
            assert score >= -1.0 and score <= 1.0
    
    def test_ai_enhanced_retrieval_empty_query_raises_error(self, setup_components):
        """Test that empty query raises ValueError."""
        embedding_generator, vector_store, query_expander = setup_components
        strategy = AIEnhancedRetrieval(embedding_generator, vector_store, query_expander)
        
        with pytest.raises(ValueError, match="Query must be a non-empty string"):
            strategy.retrieve("", k=3)
    
    def test_ai_enhanced_retrieval_invalid_k_raises_error(self, setup_components):
        """Test that invalid k value raises ValueError."""
        embedding_generator, vector_store, query_expander = setup_components
        strategy = AIEnhancedRetrieval(embedding_generator, vector_store, query_expander)
        
        with pytest.raises(ValueError, match="k must be positive"):
            strategy.retrieve("test query", k=0)
    
    def test_ai_enhanced_retrieval_latency_measurement(self, setup_components):
        """Test that latency is measured and recorded."""
        embedding_generator, vector_store, query_expander = setup_components
        strategy = AIEnhancedRetrieval(embedding_generator, vector_store, query_expander)
        
        result = strategy.retrieve("test query", k=3)
        
        # Latency should be positive
        assert result.latency_ms > 0
        # Latency should be reasonable (less than 5 seconds for this small test)
        assert result.latency_ms < 5000
    
    def test_ai_enhanced_retrieval_with_different_expansion_strategies(self):
        """Test AIEnhancedRetrieval with different expansion strategies."""
        embedding_generator = EmbeddingGenerator()
        vector_store = NumpyVectorStore(similarity_metric="cosine")
        
        # Add sample data
        sample_texts = ["Python programming language"]
        embeddings = embedding_generator.encode(sample_texts)
        vector_store.add(embeddings, sample_texts)
        
        # Test with different expansion strategies
        strategies_to_test = ["synonym_addition", "clarification", "decomposition"]
        
        for expansion_strategy in strategies_to_test:
            query_expander = QueryExpander(expansion_strategy=expansion_strategy)
            strategy = AIEnhancedRetrieval(embedding_generator, vector_store, query_expander)
            
            result = strategy.retrieve("What is Python?", k=1)
            
            # Should work with all strategies
            assert result.expanded_query is not None
            assert len(result.chunks) > 0


class TestRetrievalStrategyInterface:
    """Tests for RetrievalStrategy abstract interface."""
    
    def test_retrieval_strategy_is_abstract(self):
        """Test that RetrievalStrategy cannot be instantiated directly."""
        with pytest.raises(TypeError):
            RetrievalStrategy()
    
    def test_raw_vector_search_implements_interface(self):
        """Test that RawVectorSearch implements RetrievalStrategy interface."""
        embedding_generator = EmbeddingGenerator()
        vector_store = NumpyVectorStore()
        
        strategy = RawVectorSearch(embedding_generator, vector_store)
        
        assert isinstance(strategy, RetrievalStrategy)
        assert hasattr(strategy, 'retrieve')
        assert callable(strategy.retrieve)
    
    def test_ai_enhanced_retrieval_implements_interface(self):
        """Test that AIEnhancedRetrieval implements RetrievalStrategy interface."""
        embedding_generator = EmbeddingGenerator()
        vector_store = NumpyVectorStore()
        query_expander = QueryExpander()
        
        strategy = AIEnhancedRetrieval(embedding_generator, vector_store, query_expander)
        
        assert isinstance(strategy, RetrievalStrategy)
        assert hasattr(strategy, 'retrieve')
        assert callable(strategy.retrieve)
