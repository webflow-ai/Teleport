"""Tests for vector storage implementations.

This module tests the VectorStore interface and its implementations:
- FAISSVectorStore
- ChromaDBVectorStore
- NumpyVectorStore
"""

import pytest
import numpy as np
import tempfile
import shutil
import sys
from pathlib import Path

from src.storage import (
    VectorStore,
    FAISSVectorStore,
    ChromaDBVectorStore,
    NumpyVectorStore,
    SearchResult,
    DimensionMismatchError,
)


# Skip ChromaDB tests on Windows due to file locking issues
skip_chromadb_on_windows = pytest.mark.skipif(
    sys.platform == "win32",
    reason="ChromaDB has file locking issues on Windows in tests"
)


class TestFAISSVectorStore:
    """Tests for FAISS vector store implementation."""

    def test_initialization_cosine(self):
        """Test FAISS initialization with cosine similarity."""
        store = FAISSVectorStore(dimension=384, similarity_metric="cosine")
        assert store.dimension == 384
        assert store.similarity_metric == "cosine"
        assert len(store.texts) == 0

    def test_initialization_euclidean(self):
        """Test FAISS initialization with Euclidean distance."""
        store = FAISSVectorStore(dimension=384, similarity_metric="euclidean")
        assert store.dimension == 384
        assert store.similarity_metric == "euclidean"

    def test_add_single_embedding(self):
        """Test adding a single embedding."""
        store = FAISSVectorStore(dimension=384, similarity_metric="cosine")
        embedding = np.random.rand(1, 384).astype(np.float32)
        texts = ["Test document"]
        
        store.add(embedding, texts)
        assert len(store.texts) == 1
        assert store.texts[0] == "Test document"

    def test_add_multiple_embeddings(self):
        """Test adding multiple embeddings."""
        store = FAISSVectorStore(dimension=384, similarity_metric="cosine")
        embeddings = np.random.rand(5, 384).astype(np.float32)
        texts = [f"Document {i}" for i in range(5)]
        
        store.add(embeddings, texts)
        assert len(store.texts) == 5

    def test_search_returns_top_k(self):
        """Test search returns correct number of results."""
        store = FAISSVectorStore(dimension=384, similarity_metric="cosine")
        embeddings = np.random.rand(10, 384).astype(np.float32)
        texts = [f"Document {i}" for i in range(10)]
        
        store.add(embeddings, texts)
        
        query = np.random.rand(1, 384).astype(np.float32)
        results = store.search(query, k=3)
        
        assert len(results) == 3
        assert all(isinstance(r, SearchResult) for r in results)

    def test_search_k_greater_than_store_size(self):
        """Test search when k > number of stored items."""
        store = FAISSVectorStore(dimension=384, similarity_metric="cosine")
        embeddings = np.random.rand(3, 384).astype(np.float32)
        texts = [f"Document {i}" for i in range(3)]
        
        store.add(embeddings, texts)
        
        query = np.random.rand(1, 384).astype(np.float32)
        results = store.search(query, k=10)
        
        assert len(results) == 3  # Should return all available

    def test_search_empty_store(self):
        """Test search on empty store returns empty list."""
        store = FAISSVectorStore(dimension=384, similarity_metric="cosine")
        query = np.random.rand(1, 384).astype(np.float32)
        results = store.search(query, k=3)
        
        assert len(results) == 0

    def test_save_and_load(self):
        """Test saving and loading FAISS index."""
        with tempfile.TemporaryDirectory() as tmpdir:
            store = FAISSVectorStore(dimension=384, similarity_metric="cosine")
            embeddings = np.random.rand(5, 384).astype(np.float32)
            texts = [f"Document {i}" for i in range(5)]
            
            store.add(embeddings, texts)
            
            # Save
            save_path = Path(tmpdir) / "test_store"
            store.save(str(save_path))
            
            # Load into new store
            new_store = FAISSVectorStore(dimension=384, similarity_metric="cosine")
            new_store.load(str(save_path))
            
            assert len(new_store.texts) == 5
            assert new_store.texts == texts

    def test_dimension_mismatch_raises_error(self):
        """Test that dimension mismatch raises error."""
        store = FAISSVectorStore(dimension=384, similarity_metric="cosine")
        embeddings = np.random.rand(5, 256).astype(np.float32)  # Wrong dimension
        texts = [f"Document {i}" for i in range(5)]
        
        with pytest.raises(DimensionMismatchError):
            store.add(embeddings, texts)


class TestChromaDBVectorStore:
    """Tests for ChromaDB vector store implementation."""

    @skip_chromadb_on_windows
    def test_initialization(self):
        """Test ChromaDB initialization."""
        with tempfile.TemporaryDirectory() as tmpdir:
            store = ChromaDBVectorStore(
                collection_name="test_collection",
                persist_directory=tmpdir
            )
            assert store.collection_name == "test_collection"

    @skip_chromadb_on_windows
    def test_add_single_embedding(self):
        """Test adding a single embedding."""
        with tempfile.TemporaryDirectory() as tmpdir:
            store = ChromaDBVectorStore(
                collection_name="test_collection",
                persist_directory=tmpdir
            )
            embedding = np.random.rand(1, 384).astype(np.float32)
            texts = ["Test document"]
            
            store.add(embedding, texts)
            # ChromaDB should have stored the document

    @skip_chromadb_on_windows
    def test_add_multiple_embeddings(self):
        """Test adding multiple embeddings."""
        with tempfile.TemporaryDirectory() as tmpdir:
            store = ChromaDBVectorStore(
                collection_name="test_collection",
                persist_directory=tmpdir
            )
            embeddings = np.random.rand(5, 384).astype(np.float32)
            texts = [f"Document {i}" for i in range(5)]
            
            store.add(embeddings, texts)

    @skip_chromadb_on_windows
    def test_search_returns_top_k(self):
        """Test search returns correct number of results."""
        with tempfile.TemporaryDirectory() as tmpdir:
            store = ChromaDBVectorStore(
                collection_name="test_collection",
                persist_directory=tmpdir
            )
            embeddings = np.random.rand(10, 384).astype(np.float32)
            texts = [f"Document {i}" for i in range(10)]
            
            store.add(embeddings, texts)
            
            query = np.random.rand(1, 384).astype(np.float32)
            results = store.search(query, k=3)
            
            assert len(results) == 3
            assert all(isinstance(r, SearchResult) for r in results)

    @skip_chromadb_on_windows
    def test_search_empty_store(self):
        """Test search on empty store returns empty list."""
        with tempfile.TemporaryDirectory() as tmpdir:
            store = ChromaDBVectorStore(
                collection_name="test_collection",
                persist_directory=tmpdir
            )
            query = np.random.rand(1, 384).astype(np.float32)
            results = store.search(query, k=3)
            
            assert len(results) == 0

    @skip_chromadb_on_windows
    def test_persistence(self):
        """Test ChromaDB automatic persistence."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create and populate store
            store = ChromaDBVectorStore(
                collection_name="test_collection",
                persist_directory=tmpdir
            )
            embeddings = np.random.rand(5, 384).astype(np.float32)
            texts = [f"Document {i}" for i in range(5)]
            store.add(embeddings, texts)
            
            # Create new store with same directory
            new_store = ChromaDBVectorStore(
                collection_name="test_collection",
                persist_directory=tmpdir
            )
            
            # Should be able to search
            query = np.random.rand(1, 384).astype(np.float32)
            results = new_store.search(query, k=3)
            assert len(results) == 3


class TestNumpyVectorStore:
    """Tests for NumPy vector store implementation."""

    def test_initialization_cosine(self):
        """Test NumPy store initialization with cosine similarity."""
        store = NumpyVectorStore(similarity_metric="cosine")
        assert store.similarity_metric == "cosine"
        assert len(store.texts) == 0

    def test_initialization_euclidean(self):
        """Test NumPy store initialization with Euclidean distance."""
        store = NumpyVectorStore(similarity_metric="euclidean")
        assert store.similarity_metric == "euclidean"

    def test_add_single_embedding(self):
        """Test adding a single embedding."""
        store = NumpyVectorStore(similarity_metric="cosine")
        embedding = np.random.rand(1, 384).astype(np.float32)
        texts = ["Test document"]
        
        store.add(embedding, texts)
        assert len(store.texts) == 1
        assert store.embeddings.shape == (1, 384)

    def test_add_multiple_embeddings(self):
        """Test adding multiple embeddings."""
        store = NumpyVectorStore(similarity_metric="cosine")
        embeddings = np.random.rand(5, 384).astype(np.float32)
        texts = [f"Document {i}" for i in range(5)]
        
        store.add(embeddings, texts)
        assert len(store.texts) == 5
        assert store.embeddings.shape == (5, 384)

    def test_search_cosine_similarity(self):
        """Test search with cosine similarity."""
        store = NumpyVectorStore(similarity_metric="cosine")
        embeddings = np.random.rand(10, 384).astype(np.float32)
        texts = [f"Document {i}" for i in range(10)]
        
        store.add(embeddings, texts)
        
        query = np.random.rand(1, 384).astype(np.float32)
        results = store.search(query, k=3)
        
        assert len(results) == 3
        assert all(isinstance(r, SearchResult) for r in results)
        # Scores should be in descending order
        assert results[0].score >= results[1].score >= results[2].score

    def test_search_euclidean_distance(self):
        """Test search with Euclidean distance."""
        store = NumpyVectorStore(similarity_metric="euclidean")
        embeddings = np.random.rand(10, 384).astype(np.float32)
        texts = [f"Document {i}" for i in range(10)]
        
        store.add(embeddings, texts)
        
        query = np.random.rand(1, 384).astype(np.float32)
        results = store.search(query, k=3)
        
        assert len(results) == 3
        # Scores are converted to similarity (1/(1+distance)), so higher is still better
        assert results[0].score >= results[1].score >= results[2].score

    def test_search_empty_store(self):
        """Test search on empty store returns empty list."""
        store = NumpyVectorStore(similarity_metric="cosine")
        query = np.random.rand(1, 384).astype(np.float32)
        results = store.search(query, k=3)
        
        assert len(results) == 0

    def test_search_k_greater_than_store_size(self):
        """Test search when k > number of stored items."""
        store = NumpyVectorStore(similarity_metric="cosine")
        embeddings = np.random.rand(3, 384).astype(np.float32)
        texts = [f"Document {i}" for i in range(3)]
        
        store.add(embeddings, texts)
        
        query = np.random.rand(1, 384).astype(np.float32)
        results = store.search(query, k=10)
        
        assert len(results) == 3

    def test_save_and_load(self):
        """Test saving and loading NumPy store."""
        with tempfile.TemporaryDirectory() as tmpdir:
            store = NumpyVectorStore(similarity_metric="cosine")
            embeddings = np.random.rand(5, 384).astype(np.float32)
            texts = [f"Document {i}" for i in range(5)]
            
            store.add(embeddings, texts)
            
            # Save
            save_path = Path(tmpdir) / "test_store"
            store.save(str(save_path))
            
            # Load into new store
            new_store = NumpyVectorStore(similarity_metric="cosine")
            new_store.load(str(save_path))
            
            assert len(new_store.texts) == 5
            assert new_store.texts == texts
            assert np.array_equal(new_store.embeddings, embeddings)

    def test_incremental_addition(self):
        """Test adding embeddings incrementally."""
        store = NumpyVectorStore(similarity_metric="cosine")
        
        # Add first batch
        embeddings1 = np.random.rand(3, 384).astype(np.float32)
        texts1 = [f"Document {i}" for i in range(3)]
        store.add(embeddings1, texts1)
        
        # Add second batch
        embeddings2 = np.random.rand(2, 384).astype(np.float32)
        texts2 = [f"Document {i}" for i in range(3, 5)]
        store.add(embeddings2, texts2)
        
        assert len(store.texts) == 5
        assert store.embeddings.shape == (5, 384)


class TestSearchResult:
    """Tests for SearchResult data model."""

    def test_search_result_creation(self):
        """Test creating a SearchResult."""
        result = SearchResult(
            text="Test document",
            score=0.95,
            metadata={"source": "test"}
        )
        assert result.text == "Test document"
        assert result.score == 0.95
        assert result.metadata == {"source": "test"}

    def test_search_result_without_metadata(self):
        """Test SearchResult without metadata."""
        result = SearchResult(text="Test", score=0.8)
        assert result.metadata is None
