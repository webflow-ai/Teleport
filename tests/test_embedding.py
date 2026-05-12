"""Unit tests for the Embedding Generator module."""

import pytest
import numpy as np
from src.embedding import EmbeddingGenerator, ModelNotFoundError


class TestEmbeddingGenerator:
    """Test suite for EmbeddingGenerator class."""
    
    def test_initialization_default_model(self):
        """Test that EmbeddingGenerator initializes with default model."""
        generator = EmbeddingGenerator()
        assert generator.model_name == "all-MiniLM-L6-v2"
        assert generator.model is not None
        assert generator.get_embedding_dimension() == 384
    
    def test_encode_single_string(self):
        """Test encoding a single string."""
        generator = EmbeddingGenerator()
        text = "This is a test sentence."
        embedding = generator.encode(text)
        
        assert isinstance(embedding, np.ndarray)
        assert embedding.shape == (1, 384)
    
    def test_encode_batch_strings(self):
        """Test encoding a batch of strings."""
        generator = EmbeddingGenerator()
        texts = ["First sentence.", "Second sentence.", "Third sentence."]
        embeddings = generator.encode(texts)
        
        assert isinstance(embeddings, np.ndarray)
        assert embeddings.shape == (3, 384)
    
    def test_encode_empty_string_raises_error(self):
        """Test that empty string raises ValueError."""
        generator = EmbeddingGenerator()
        
        with pytest.raises(ValueError, match="empty strings"):
            generator.encode("")
    
    def test_encode_non_string_raises_error(self):
        """Test that non-string input raises TypeError."""
        generator = EmbeddingGenerator()
        
        with pytest.raises(TypeError, match="string or list of strings"):
            generator.encode(123)
    
    def test_embedding_dimension_consistency(self):
        """Test that all embeddings have consistent dimensionality."""
        generator = EmbeddingGenerator()
        
        texts = [
            "Short",
            "A medium length sentence with more words.",
            "A very long sentence with many words."
        ]
        
        embeddings = generator.encode(texts)
        assert embeddings.shape[1] == 384
    
    def test_batch_processing_correspondence(self):
        """Test that number of embeddings equals number of input texts."""
        generator = EmbeddingGenerator()
        
        for batch_size in [1, 5, 10]:
            texts = [f"Text number {i}" for i in range(batch_size)]
            embeddings = generator.encode(texts)
            assert embeddings.shape[0] == batch_size
    
    def test_get_embedding_dimension(self):
        """Test get_embedding_dimension method."""
        generator = EmbeddingGenerator()
        dimension = generator.get_embedding_dimension()
        
        assert isinstance(dimension, int)
        assert dimension == 384
        
        embedding = generator.encode("test")
        assert embedding.shape[1] == dimension
