"""Vector storage implementations for the Context-Aware Retrieval Engine.

This module provides abstract and concrete implementations of vector stores
for storing and retrieving embeddings with associated text and metadata.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Optional, Dict, Union
import numpy as np
import json
import os


@dataclass
class SearchResult:
    """Single search result from vector store.
    
    Attributes:
        text: The original text associated with the embedding
        score: Similarity score (higher is more similar)
        metadata: Optional metadata dictionary
    """
    text: str
    score: float
    metadata: Optional[Dict] = None


class VectorStore(ABC):
    """Abstract interface for vector storage backends.
    
    All vector store implementations must provide methods for adding embeddings,
    searching for similar embeddings, and persisting/loading the store.
    """
    
    @abstractmethod
    def add(self, embeddings: np.ndarray, texts: List[str], 
            metadata: Optional[List[Dict]] = None) -> None:
        """Store embeddings with associated text and metadata.
        
        Args:
            embeddings: numpy array of shape (n, embedding_dim)
            texts: List of text strings corresponding to each embedding
            metadata: Optional list of metadata dictionaries
            
        Raises:
            ValueError: If embeddings and texts have mismatched lengths
            DimensionMismatchError: If embeddings have wrong dimensionality
        """
        pass
    
    @abstractmethod
    def search(self, query_embedding: np.ndarray, k: int = 3) -> List[SearchResult]:
        """Find k most similar embeddings.
        
        Args:
            query_embedding: numpy array of shape (embedding_dim,) or (1, embedding_dim)
            k: Number of results to return
            
        Returns:
            List of SearchResult objects sorted by similarity (highest first)
            
        Raises:
            ValueError: If k <= 0
            DimensionMismatchError: If query_embedding has wrong dimensionality
        """
        pass
    
    @abstractmethod
    def save(self, path: str) -> None:
        """Persist vector store to disk.
        
        Args:
            path: Directory path where store should be saved
            
        Raises:
            IOError: If unable to write to path
        """
        pass
    
    @abstractmethod
    def load(self, path: str) -> None:
        """Load vector store from disk.
        
        Args:
            path: Directory path where store is saved
            
        Raises:
            IOError: If unable to read from path
            FileNotFoundError: If path does not exist
        """
        pass


class DimensionMismatchError(Exception):
    """Raised when embedding dimensions don't match expected dimensions."""
    pass


class FAISSVectorStore(VectorStore):
    """FAISS-based vector store implementation.
    
    Uses FAISS IndexFlatIP for cosine similarity with L2 normalization.
    Provides fast in-memory similarity search.
    """
    
    def __init__(self, dimension: int, similarity_metric: str = "cosine"):
        """Initialize FAISS vector store.
        
        Args:
            dimension: Dimensionality of embeddings
            similarity_metric: "cosine" or "euclidean"
            
        Raises:
            ValueError: If similarity_metric is not supported
            ImportError: If faiss is not installed
        """
        try:
            import faiss
        except ImportError:
            raise ImportError(
                "faiss-cpu is required for FAISSVectorStore. "
                "Install with: pip install faiss-cpu"
            )
        
        if similarity_metric not in ["cosine", "euclidean"]:
            raise ValueError(
                f"Unsupported similarity metric: {similarity_metric}. "
                f"Use 'cosine' or 'euclidean'"
            )
        
        self.dimension = dimension
        self.similarity_metric = similarity_metric
        self.texts: List[str] = []
        self.metadata_list: List[Optional[Dict]] = []
        
        # Use IndexFlatIP for cosine similarity (requires L2 normalization)
        # Use IndexFlatL2 for Euclidean distance
        if similarity_metric == "cosine":
            self.index = faiss.IndexFlatIP(dimension)
        else:
            self.index = faiss.IndexFlatL2(dimension)
    
    def add(self, embeddings: np.ndarray, texts: List[str], 
            metadata: Optional[List[Dict]] = None) -> None:
        """Store embeddings with associated text and metadata.
        
        Args:
            embeddings: numpy array of shape (n, embedding_dim)
            texts: List of text strings corresponding to each embedding
            metadata: Optional list of metadata dictionaries
        """
        import faiss
        
        # Validate inputs
        if len(embeddings.shape) == 1:
            embeddings = embeddings.reshape(1, -1)
        
        if embeddings.shape[0] != len(texts):
            raise ValueError(
                f"Number of embeddings ({embeddings.shape[0]}) must match "
                f"number of texts ({len(texts)})"
            )
        
        if embeddings.shape[1] != self.dimension:
            raise DimensionMismatchError(
                f"Expected embeddings with dimension {self.dimension}, "
                f"got {embeddings.shape[1]}"
            )
        
        # Prepare metadata
        if metadata is None:
            metadata = [None] * len(texts)
        elif len(metadata) != len(texts):
            raise ValueError(
                f"Number of metadata entries ({len(metadata)}) must match "
                f"number of texts ({len(texts)})"
            )
        
        # Normalize embeddings for cosine similarity
        embeddings_to_add = embeddings.astype('float32')
        if self.similarity_metric == "cosine":
            faiss.normalize_L2(embeddings_to_add)
        
        # Add to index
        self.index.add(embeddings_to_add)
        self.texts.extend(texts)
        self.metadata_list.extend(metadata)
    
    def search(self, query_embedding: np.ndarray, k: int = 3) -> List[SearchResult]:
        """Find k most similar embeddings.
        
        Args:
            query_embedding: numpy array of shape (embedding_dim,) or (1, embedding_dim)
            k: Number of results to return
            
        Returns:
            List of SearchResult objects sorted by similarity (highest first)
        """
        import faiss
        
        if k <= 0:
            raise ValueError(f"k must be positive, got {k}")
        
        # Handle empty store
        if self.index.ntotal == 0:
            return []
        
        # Reshape query if needed
        if len(query_embedding.shape) == 1:
            query_embedding = query_embedding.reshape(1, -1)
        
        if query_embedding.shape[1] != self.dimension:
            raise DimensionMismatchError(
                f"Expected query embedding with dimension {self.dimension}, "
                f"got {query_embedding.shape[1]}"
            )
        
        # Normalize query for cosine similarity
        query_to_search = query_embedding.astype('float32')
        if self.similarity_metric == "cosine":
            faiss.normalize_L2(query_to_search)
        
        # Search
        actual_k = min(k, self.index.ntotal)
        distances, indices = self.index.search(query_to_search, actual_k)
        
        # Convert to SearchResult objects
        results = []
        for i in range(actual_k):
            idx = indices[0][i]
            score = float(distances[0][i])
            
            # Convert distance to similarity score
            # For cosine: IndexFlatIP returns dot product (already similarity)
            # For euclidean: IndexFlatL2 returns squared distance (lower is better)
            if self.similarity_metric == "euclidean":
                # Convert squared distance to similarity (inverse)
                score = 1.0 / (1.0 + score)
            
            results.append(SearchResult(
                text=self.texts[idx],
                score=score,
                metadata=self.metadata_list[idx]
            ))
        
        return results
    
    def save(self, path: str) -> None:
        """Persist vector store to disk.
        
        Args:
            path: Directory path where store should be saved
        """
        import faiss
        
        os.makedirs(path, exist_ok=True)
        
        # Save FAISS index
        index_path = os.path.join(path, "vector_store.faiss")
        faiss.write_index(self.index, index_path)
        
        # Save metadata
        metadata_path = os.path.join(path, "metadata.json")
        metadata = {
            "dimension": self.dimension,
            "similarity_metric": self.similarity_metric,
            "texts": self.texts,
            "metadata_list": self.metadata_list
        }
        
        try:
            with open(metadata_path, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2)
        except IOError as e:
            raise IOError(f"Failed to save metadata to {metadata_path}: {e}")
    
    def load(self, path: str) -> None:
        """Load vector store from disk.
        
        Args:
            path: Directory path where store is saved
        """
        import faiss
        
        if not os.path.exists(path):
            raise FileNotFoundError(f"Path does not exist: {path}")
        
        # Load FAISS index
        index_path = os.path.join(path, "vector_store.faiss")
        if not os.path.exists(index_path):
            raise FileNotFoundError(f"Index file not found: {index_path}")
        
        try:
            self.index = faiss.read_index(index_path)
        except Exception as e:
            raise IOError(f"Failed to load FAISS index from {index_path}: {e}")
        
        # Load metadata
        metadata_path = os.path.join(path, "metadata.json")
        if not os.path.exists(metadata_path):
            raise FileNotFoundError(f"Metadata file not found: {metadata_path}")
        
        try:
            with open(metadata_path, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
            
            self.dimension = metadata["dimension"]
            self.similarity_metric = metadata["similarity_metric"]
            self.texts = metadata["texts"]
            self.metadata_list = metadata["metadata_list"]
        except (IOError, json.JSONDecodeError) as e:
            raise IOError(f"Failed to load metadata from {metadata_path}: {e}")


class ChromaDBVectorStore(VectorStore):
    """ChromaDB-based vector store implementation.
    
    Uses ChromaDB for persistent vector storage with built-in similarity search.
    """
    
    def __init__(self, collection_name: str = "rag_collection", 
                 persist_directory: str = "./chroma_db"):
        """Initialize ChromaDB vector store.
        
        Args:
            collection_name: Name of the ChromaDB collection
            persist_directory: Directory for persistent storage
            
        Raises:
            ImportError: If chromadb is not installed
        """
        try:
            import chromadb
        except ImportError:
            raise ImportError(
                "chromadb is required for ChromaDBVectorStore. "
                "Install with: pip install chromadb"
            )
        
        self.collection_name = collection_name
        self.persist_directory = persist_directory
        
        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(path=persist_directory)
        
        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"}  # Use cosine similarity
        )
        
        self.next_id = 0
    
    def add(self, embeddings: np.ndarray, texts: List[str], 
            metadata: Optional[List[Dict]] = None) -> None:
        """Store embeddings with associated text and metadata.
        
        Args:
            embeddings: numpy array of shape (n, embedding_dim)
            texts: List of text strings corresponding to each embedding
            metadata: Optional list of metadata dictionaries
        """
        # Validate inputs
        if len(embeddings.shape) == 1:
            embeddings = embeddings.reshape(1, -1)
        
        if embeddings.shape[0] != len(texts):
            raise ValueError(
                f"Number of embeddings ({embeddings.shape[0]}) must match "
                f"number of texts ({len(texts)})"
            )
        
        # Prepare metadata
        if metadata is None:
            metadata = [{}] * len(texts)
        elif len(metadata) != len(texts):
            raise ValueError(
                f"Number of metadata entries ({len(metadata)}) must match "
                f"number of texts ({len(texts)})"
            )
        
        # Convert None metadata entries to empty dicts
        metadata = [m if m is not None else {} for m in metadata]
        
        # Generate IDs
        ids = [f"doc_{self.next_id + i}" for i in range(len(texts))]
        self.next_id += len(texts)
        
        # Add to collection
        self.collection.add(
            embeddings=embeddings.tolist(),
            documents=texts,
            metadatas=metadata,
            ids=ids
        )
    
    def search(self, query_embedding: np.ndarray, k: int = 3) -> List[SearchResult]:
        """Find k most similar embeddings.
        
        Args:
            query_embedding: numpy array of shape (embedding_dim,) or (1, embedding_dim)
            k: Number of results to return
            
        Returns:
            List of SearchResult objects sorted by similarity (highest first)
        """
        if k <= 0:
            raise ValueError(f"k must be positive, got {k}")
        
        # Handle empty store
        if self.collection.count() == 0:
            return []
        
        # Reshape query if needed
        if len(query_embedding.shape) == 1:
            query_embedding = query_embedding.reshape(1, -1)
        
        # Query collection
        actual_k = min(k, self.collection.count())
        results = self.collection.query(
            query_embeddings=query_embedding.tolist(),
            n_results=actual_k
        )
        
        # Convert to SearchResult objects
        search_results = []
        for i in range(len(results['documents'][0])):
            # ChromaDB returns distances (lower is better for cosine)
            # Convert to similarity score (1 - distance)
            distance = results['distances'][0][i]
            score = 1.0 - distance
            
            search_results.append(SearchResult(
                text=results['documents'][0][i],
                score=score,
                metadata=results['metadatas'][0][i] if results['metadatas'][0][i] else None
            ))
        
        return search_results
    
    def save(self, path: str) -> None:
        """Persist vector store to disk.
        
        ChromaDB automatically persists data, so this is a no-op.
        Included for interface compatibility.
        
        Args:
            path: Ignored (ChromaDB uses persist_directory from __init__)
        """
        # ChromaDB automatically persists, no action needed
        pass
    
    def load(self, path: str) -> None:
        """Load vector store from disk.
        
        ChromaDB automatically loads persisted data, so this is a no-op.
        Included for interface compatibility.
        
        Args:
            path: Ignored (ChromaDB uses persist_directory from __init__)
        """
        # ChromaDB automatically loads persisted data, no action needed
        pass


class NumpyVectorStore(VectorStore):
    """Simple NumPy-based vector store implementation.
    
    Uses pure NumPy operations for similarity search. Suitable for small datasets
    and testing purposes.
    """
    
    def __init__(self, similarity_metric: str = "cosine"):
        """Initialize NumPy vector store.
        
        Args:
            similarity_metric: "cosine" or "euclidean"
            
        Raises:
            ValueError: If similarity_metric is not supported
        """
        if similarity_metric not in ["cosine", "euclidean"]:
            raise ValueError(
                f"Unsupported similarity metric: {similarity_metric}. "
                f"Use 'cosine' or 'euclidean'"
            )
        
        self.similarity_metric = similarity_metric
        self.embeddings: Optional[np.ndarray] = None
        self.texts: List[str] = []
        self.metadata_list: List[Optional[Dict]] = []
        self.dimension: Optional[int] = None
    
    def add(self, embeddings: np.ndarray, texts: List[str], 
            metadata: Optional[List[Dict]] = None) -> None:
        """Store embeddings with associated text and metadata.
        
        Args:
            embeddings: numpy array of shape (n, embedding_dim)
            texts: List of text strings corresponding to each embedding
            metadata: Optional list of metadata dictionaries
        """
        # Validate inputs
        if len(embeddings.shape) == 1:
            embeddings = embeddings.reshape(1, -1)
        
        if embeddings.shape[0] != len(texts):
            raise ValueError(
                f"Number of embeddings ({embeddings.shape[0]}) must match "
                f"number of texts ({len(texts)})"
            )
        
        # Set dimension on first add
        if self.dimension is None:
            self.dimension = embeddings.shape[1]
        elif embeddings.shape[1] != self.dimension:
            raise DimensionMismatchError(
                f"Expected embeddings with dimension {self.dimension}, "
                f"got {embeddings.shape[1]}"
            )
        
        # Prepare metadata
        if metadata is None:
            metadata = [None] * len(texts)
        elif len(metadata) != len(texts):
            raise ValueError(
                f"Number of metadata entries ({len(metadata)}) must match "
                f"number of texts ({len(texts)})"
            )
        
        # Append to storage
        if self.embeddings is None:
            self.embeddings = embeddings.astype('float32')
        else:
            self.embeddings = np.vstack([self.embeddings, embeddings.astype('float32')])
        
        self.texts.extend(texts)
        self.metadata_list.extend(metadata)
    
    def search(self, query_embedding: np.ndarray, k: int = 3) -> List[SearchResult]:
        """Find k most similar embeddings using NumPy operations.
        
        Args:
            query_embedding: numpy array of shape (embedding_dim,) or (1, embedding_dim)
            k: Number of results to return
            
        Returns:
            List of SearchResult objects sorted by similarity (highest first)
        """
        if k <= 0:
            raise ValueError(f"k must be positive, got {k}")
        
        # Handle empty store
        if self.embeddings is None or len(self.embeddings) == 0:
            return []
        
        # Reshape query if needed
        if len(query_embedding.shape) == 1:
            query_embedding = query_embedding.reshape(1, -1)
        
        if query_embedding.shape[1] != self.dimension:
            raise DimensionMismatchError(
                f"Expected query embedding with dimension {self.dimension}, "
                f"got {query_embedding.shape[1]}"
            )
        
        # Calculate similarities
        if self.similarity_metric == "cosine":
            # Cosine similarity: (A · B) / (||A|| * ||B||)
            query_norm = np.linalg.norm(query_embedding, axis=1, keepdims=True)
            embeddings_norm = np.linalg.norm(self.embeddings, axis=1, keepdims=True)
            
            # Avoid division by zero
            query_norm = np.maximum(query_norm, 1e-10)
            embeddings_norm = np.maximum(embeddings_norm, 1e-10)
            
            similarities = np.dot(query_embedding, self.embeddings.T) / (query_norm * embeddings_norm.T)
            similarities = similarities.flatten()
        else:
            # Euclidean distance: ||A - B||
            distances = np.linalg.norm(self.embeddings - query_embedding, axis=1)
            # Convert to similarity (inverse)
            similarities = 1.0 / (1.0 + distances)
        
        # Get top-k indices
        actual_k = min(k, len(self.embeddings))
        top_k_indices = np.argsort(similarities)[-actual_k:][::-1]
        
        # Convert to SearchResult objects
        results = []
        for idx in top_k_indices:
            results.append(SearchResult(
                text=self.texts[idx],
                score=float(similarities[idx]),
                metadata=self.metadata_list[idx]
            ))
        
        return results
    
    def save(self, path: str) -> None:
        """Persist vector store to disk using NumPy save.
        
        Args:
            path: Directory path where store should be saved
        """
        os.makedirs(path, exist_ok=True)
        
        # Save embeddings
        if self.embeddings is not None:
            embeddings_path = os.path.join(path, "embeddings.npy")
            try:
                np.save(embeddings_path, self.embeddings)
            except IOError as e:
                raise IOError(f"Failed to save embeddings to {embeddings_path}: {e}")
        
        # Save metadata
        metadata_path = os.path.join(path, "metadata.json")
        metadata = {
            "similarity_metric": self.similarity_metric,
            "dimension": self.dimension,
            "texts": self.texts,
            "metadata_list": self.metadata_list
        }
        
        try:
            with open(metadata_path, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2)
        except IOError as e:
            raise IOError(f"Failed to save metadata to {metadata_path}: {e}")
    
    def load(self, path: str) -> None:
        """Load vector store from disk using NumPy load.
        
        Args:
            path: Directory path where store is saved
        """
        if not os.path.exists(path):
            raise FileNotFoundError(f"Path does not exist: {path}")
        
        # Load embeddings
        embeddings_path = os.path.join(path, "embeddings.npy")
        if os.path.exists(embeddings_path):
            try:
                self.embeddings = np.load(embeddings_path)
            except IOError as e:
                raise IOError(f"Failed to load embeddings from {embeddings_path}: {e}")
        else:
            self.embeddings = None
        
        # Load metadata
        metadata_path = os.path.join(path, "metadata.json")
        if not os.path.exists(metadata_path):
            raise FileNotFoundError(f"Metadata file not found: {metadata_path}")
        
        try:
            with open(metadata_path, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
            
            self.similarity_metric = metadata["similarity_metric"]
            self.dimension = metadata["dimension"]
            self.texts = metadata["texts"]
            self.metadata_list = metadata["metadata_list"]
        except (IOError, json.JSONDecodeError) as e:
            raise IOError(f"Failed to load metadata from {metadata_path}: {e}")
