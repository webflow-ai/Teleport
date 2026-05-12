import pytest
import numpy as np
from src.embedding import EmbeddingGenerator

def test_basic():
    generator = EmbeddingGenerator()
    assert generator.model_name == "all-MiniLM-L6-v2"
    assert generator.get_embedding_dimension() == 384
