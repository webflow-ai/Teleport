"""Unit tests for the configuration module.

Tests the RAGConfig dataclass including validation logic and default values.
"""

import pytest
from src.config import RAGConfig


class TestRAGConfigDefaults:
    """Test default configuration values."""
    
    def test_default_values(self):
        """Test that default configuration values are set correctly."""
        config = RAGConfig()
        
        assert config.embedding_model == "all-MiniLM-L6-v2"
        assert config.vector_store_type == "faiss"
        assert config.similarity_metric == "cosine"
        assert config.top_k == 3
        assert config.chunk_size == 500
        assert config.chunk_overlap == 50
        assert config.expansion_strategy == "synonym_addition"
        assert config.benchmark_queries == []
    
    def test_custom_values(self):
        """Test that custom configuration values are set correctly."""
        config = RAGConfig(
            embedding_model="custom-model",
            vector_store_type="chromadb",
            similarity_metric="euclidean",
            top_k=5,
            chunk_size=1000,
            chunk_overlap=100,
            expansion_strategy="clarification",
            benchmark_queries=["query1", "query2"]
        )
        
        assert config.embedding_model == "custom-model"
        assert config.vector_store_type == "chromadb"
        assert config.similarity_metric == "euclidean"
        assert config.top_k == 5
        assert config.chunk_size == 1000
        assert config.chunk_overlap == 100
        assert config.expansion_strategy == "clarification"
        assert config.benchmark_queries == ["query1", "query2"]


class TestRAGConfigValidation:
    """Test configuration validation logic."""
    
    def test_valid_config_passes_validation(self):
        """Test that a valid configuration passes validation."""
        config = RAGConfig()
        # Should not raise any exception
        config.validate()
    
    def test_invalid_embedding_model(self):
        """Test that invalid embedding model raises ValueError."""
        with pytest.raises(ValueError, match="embedding_model must be a non-empty string"):
            RAGConfig(embedding_model="")
    
    def test_invalid_vector_store_type(self):
        """Test that invalid vector store type raises ValueError."""
        with pytest.raises(ValueError, match="vector_store_type must be one of"):
            RAGConfig(vector_store_type="invalid")
    
    def test_invalid_similarity_metric(self):
        """Test that invalid similarity metric raises ValueError."""
        with pytest.raises(ValueError, match="similarity_metric must be one of"):
            RAGConfig(similarity_metric="invalid")
    
    def test_invalid_top_k_negative(self):
        """Test that negative top_k raises ValueError."""
        with pytest.raises(ValueError, match="top_k must be a positive integer"):
            RAGConfig(top_k=-1)
    
    def test_invalid_top_k_zero(self):
        """Test that zero top_k raises ValueError."""
        with pytest.raises(ValueError, match="top_k must be a positive integer"):
            RAGConfig(top_k=0)
    
    def test_invalid_chunk_size_negative(self):
        """Test that negative chunk_size raises ValueError."""
        with pytest.raises(ValueError, match="chunk_size must be a positive integer"):
            RAGConfig(chunk_size=-1)
    
    def test_invalid_chunk_size_zero(self):
        """Test that zero chunk_size raises ValueError."""
        with pytest.raises(ValueError, match="chunk_size must be a positive integer"):
            RAGConfig(chunk_size=0)
    
    def test_invalid_chunk_overlap_negative(self):
        """Test that negative chunk_overlap raises ValueError."""
        with pytest.raises(ValueError, match="chunk_overlap must be a non-negative integer"):
            RAGConfig(chunk_overlap=-1)
    
    def test_chunk_overlap_greater_than_chunk_size(self):
        """Test that chunk_overlap >= chunk_size raises ValueError."""
        with pytest.raises(ValueError, match="chunk_overlap .* must be less than chunk_size"):
            RAGConfig(chunk_size=100, chunk_overlap=100)
    
    def test_chunk_overlap_equal_to_chunk_size(self):
        """Test that chunk_overlap == chunk_size raises ValueError."""
        with pytest.raises(ValueError, match="chunk_overlap .* must be less than chunk_size"):
            RAGConfig(chunk_size=100, chunk_overlap=100)
    
    def test_invalid_expansion_strategy(self):
        """Test that invalid expansion strategy raises ValueError."""
        with pytest.raises(ValueError, match="expansion_strategy must be one of"):
            RAGConfig(expansion_strategy="invalid")
    
    def test_invalid_benchmark_queries_not_list(self):
        """Test that non-list benchmark_queries raises ValueError."""
        with pytest.raises(ValueError, match="benchmark_queries must be a list"):
            RAGConfig(benchmark_queries="not a list")
    
    def test_invalid_benchmark_queries_non_string_element(self):
        """Test that non-string elements in benchmark_queries raise ValueError."""
        with pytest.raises(ValueError, match="benchmark_queries\\[0\\] must be a string"):
            RAGConfig(benchmark_queries=[123])
    
    def test_invalid_benchmark_queries_empty_string(self):
        """Test that empty string in benchmark_queries raises ValueError."""
        with pytest.raises(ValueError, match="benchmark_queries\\[0\\] cannot be empty"):
            RAGConfig(benchmark_queries=[""])
    
    def test_invalid_benchmark_queries_whitespace_only(self):
        """Test that whitespace-only string in benchmark_queries raises ValueError."""
        with pytest.raises(ValueError, match="benchmark_queries\\[0\\] cannot be empty"):
            RAGConfig(benchmark_queries=["   "])


class TestRAGConfigEdgeCases:
    """Test edge cases for configuration."""
    
    def test_valid_vector_store_types(self):
        """Test all valid vector store types."""
        for store_type in ["faiss", "chromadb", "numpy"]:
            config = RAGConfig(vector_store_type=store_type)
            assert config.vector_store_type == store_type
    
    def test_valid_similarity_metrics(self):
        """Test all valid similarity metrics."""
        for metric in ["cosine", "euclidean"]:
            config = RAGConfig(similarity_metric=metric)
            assert config.similarity_metric == metric
    
    def test_valid_expansion_strategies(self):
        """Test all valid expansion strategies."""
        for strategy in ["synonym_addition", "clarification", "decomposition"]:
            config = RAGConfig(expansion_strategy=strategy)
            assert config.expansion_strategy == strategy
    
    def test_chunk_overlap_zero(self):
        """Test that chunk_overlap of 0 is valid."""
        config = RAGConfig(chunk_overlap=0)
        assert config.chunk_overlap == 0
    
    def test_chunk_overlap_one_less_than_chunk_size(self):
        """Test that chunk_overlap can be chunk_size - 1."""
        config = RAGConfig(chunk_size=100, chunk_overlap=99)
        assert config.chunk_overlap == 99
    
    def test_large_top_k(self):
        """Test that large top_k values are valid."""
        config = RAGConfig(top_k=1000)
        assert config.top_k == 1000
    
    def test_large_chunk_size(self):
        """Test that large chunk_size values are valid."""
        config = RAGConfig(chunk_size=10000)
        assert config.chunk_size == 10000
    
    def test_multiple_benchmark_queries(self):
        """Test configuration with multiple benchmark queries."""
        queries = [
            "How does the system handle peak load?",
            "What are the security features?",
            "How is data stored?"
        ]
        config = RAGConfig(benchmark_queries=queries)
        assert config.benchmark_queries == queries
        assert len(config.benchmark_queries) == 3


class TestRAGConfigPostInit:
    """Test that __post_init__ validation works correctly."""
    
    def test_post_init_validates_on_creation(self):
        """Test that validation happens automatically on object creation."""
        # This should raise ValueError during __init__ due to __post_init__
        with pytest.raises(ValueError, match="top_k must be a positive integer"):
            RAGConfig(top_k=-1)
    
    def test_post_init_allows_valid_config(self):
        """Test that valid config is created without errors."""
        # Should not raise any exception
        config = RAGConfig(
            embedding_model="test-model",
            vector_store_type="numpy",
            top_k=5
        )
        assert config.embedding_model == "test-model"
