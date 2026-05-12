
"""Embedding Generator Module for Context-Aware Retrieval Engine."""

from typing import Union, List
import numpy as np
from sentence_transformers import SentenceTransformer


class ModelNotFoundError(Exception):
    """Raised when a specified sentence-transformers model cannot be found."""
    pass


class EmbeddingGenerator:
    """Generates vector embeddings from text using sentence-transformers."""
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """Initialize the EmbeddingGenerator with a sentence-transformers model."""
        self.model_name = model_name
        
        try:
            self.model = SentenceTransformer(model_name)
            # Use the newer method name to avoid deprecation warning
            if hasattr(self.model, 'get_embedding_dimension'):
                self._embedding_dimension = self.model.get_embedding_dimension()
            else:
                self._embedding_dimension = self.model.get_sentence_embedding_dimension()
        except Exception as e:
            if "not found" in str(e).lower() or "does not exist" in str(e).lower():
                raise ModelNotFoundError(
                    f"Model '{model_name}' not found."
                ) from e
            elif "memory" in str(e).lower():
                raise MemoryError(
                    f"Insufficient memory to load model '{model_name}'."
                ) from e
            else:
                raise RuntimeError(f"Failed to load model: {str(e)}") from e
    
    def encode(self, texts: Union[str, List[str]]) -> np.ndarray:
        """Generate embeddings for input text(s)."""
        if isinstance(texts, str):
            if not texts or texts.strip() == "":
                raise ValueError("Cannot generate embeddings for empty strings.")
            
            if len(texts) > 10000:
                import warnings
                warnings.warn(
                    f"Input text length ({len(texts)}) exceeds 10,000 characters.",
                    UserWarning
                )
            
            texts = [texts]
        
        elif isinstance(texts, list):
            if len(texts) == 0:
                raise ValueError("Cannot generate embeddings for empty list.")
            
            for i, text in enumerate(texts):
                if not isinstance(text, str):
                    raise TypeError(
                        f"All elements must be strings. "
                        f"Element at index {i} has type {type(text).__name__}."
                    )
                
                if not text or text.strip() == "":
                    raise ValueError(f"Element at index {i} is empty.")
                
                if len(text) > 10000:
                    import warnings
                    warnings.warn(
                        f"Text at index {i} exceeds 10,000 characters.",
                        UserWarning
                    )
        
        else:
            raise TypeError(
                f"Input must be a string or list of strings. "
                f"Got type {type(texts).__name__}."
            )
        
        embeddings = self.model.encode(
            texts,
            convert_to_numpy=True,
            show_progress_bar=False,
            normalize_embeddings=False
        )
        
        if embeddings.ndim == 1:
            embeddings = embeddings.reshape(1, -1)
        
        return embeddings
    
    def get_embedding_dimension(self) -> int:
        """Return the dimensionality of generated embeddings."""
        return self._embedding_dimension
