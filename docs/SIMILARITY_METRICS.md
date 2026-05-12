# Similarity Metrics Guide

This guide explains the different similarity metrics available in the Context-Aware Retrieval Engine and provides recommendations for when to use each one.

## Table of Contents

- [Overview](#overview)
- [Cosine Similarity](#cosine-similarity)
- [Euclidean Distance](#euclidean-distance)
- [Comparison](#comparison)
- [Recommendations](#recommendations)
- [Implementation Examples](#implementation-examples)
- [Performance Considerations](#performance-considerations)

## Overview

Similarity metrics determine how the system measures the "closeness" between vectors in the embedding space. The choice of metric significantly impacts retrieval quality and performance.

### Available Metrics

The Context-Aware Retrieval Engine supports two similarity metrics:

1. **Cosine Similarity**: Measures the angle between vectors (directional alignment)
2. **Euclidean Distance**: Measures the straight-line distance between vectors (geometric distance)

### Why It Matters

Different metrics capture different notions of similarity:
- **Cosine** focuses on direction, ignoring magnitude
- **Euclidean** considers both direction and magnitude

For semantic search with normalized embeddings, **cosine similarity is typically preferred**.

## Cosine Similarity

### Mathematical Definition

Cosine similarity measures the cosine of the angle between two vectors:

```
cosine_similarity(A, B) = (A · B) / (||A|| × ||B||)
```

Where:
- `A · B` is the dot product of vectors A and B
- `||A||` and `||B||` are the magnitudes (L2 norms) of the vectors

**Range**: [-1, 1] for general vectors, [0, 1] for normalized vectors
- 1 = identical direction (most similar)
- 0 = orthogonal (unrelated)
- -1 = opposite direction (most dissimilar)

### Visual Intuition

```
        Vector B
          ↗
         /
        /  θ (small angle = high similarity)
       /
      /
     ↗ Vector A
```

Cosine similarity measures the angle θ between vectors. Smaller angles mean higher similarity, regardless of vector length.

### Key Properties

1. **Magnitude Invariant**: Only direction matters, not length
   ```
   cosine_similarity([1, 2, 3], [2, 4, 6]) = 1.0
   # Same direction, different magnitudes → identical similarity
   ```

2. **Normalized Range**: For normalized vectors, scores are in [0, 1]
   ```
   # After L2 normalization
   A_norm = A / ||A||
   B_norm = B / ||B||
   similarity = A_norm · B_norm  # Dot product = cosine for normalized vectors
   ```

3. **Efficient Computation**: For normalized vectors, cosine = dot product
   ```python
   # No need to compute magnitudes if vectors are pre-normalized
   similarity = np.dot(A_normalized, B_normalized)
   ```

### When to Use Cosine Similarity

✅ **Use cosine similarity when**:
- Embeddings are normalized (sentence-transformers normalizes by default)
- You care about semantic alignment, not absolute magnitude
- Working with text embeddings from pre-trained models
- Following standard semantic search practices
- Migrating to cloud services (Vertex AI uses cosine)

❌ **Don't use cosine similarity when**:
- Vector magnitude carries semantic meaning
- Working with count-based features (TF-IDF without normalization)
- Specific model was trained with Euclidean distance

### Implementation

#### FAISS with Cosine Similarity

```python
import faiss
import numpy as np

# Create index for inner product (cosine with normalized vectors)
dimension = 384
index = faiss.IndexFlatIP(dimension)  # IP = Inner Product

# Normalize embeddings before adding
embeddings = np.random.randn(100, dimension).astype('float32')
faiss.normalize_L2(embeddings)  # Normalize to unit length
index.add(embeddings)

# Normalize query before searching
query = np.random.randn(1, dimension).astype('float32')
faiss.normalize_L2(query)

# Search (higher scores = more similar)
scores, indices = index.search(query, k=5)
```

#### NumPy with Cosine Similarity

```python
import numpy as np

def cosine_similarity(query: np.ndarray, embeddings: np.ndarray) -> np.ndarray:
    """Compute cosine similarity between query and all embeddings.
    
    Args:
        query: Query vector of shape (embedding_dim,)
        embeddings: Matrix of shape (n_vectors, embedding_dim)
    
    Returns:
        Similarity scores of shape (n_vectors,)
    """
    # Normalize query
    query_norm = query / np.linalg.norm(query)
    
    # Normalize embeddings
    embeddings_norm = embeddings / np.linalg.norm(embeddings, axis=1, keepdims=True)
    
    # Compute dot product (= cosine for normalized vectors)
    similarities = np.dot(embeddings_norm, query_norm)
    
    return similarities

# Example usage
query = np.array([1.0, 2.0, 3.0])
embeddings = np.array([
    [1.0, 2.0, 3.0],
    [4.0, 5.0, 6.0],
    [-1.0, -2.0, -3.0]
])

scores = cosine_similarity(query, embeddings)
print(scores)  # [1.0, 0.974, -1.0]
```

## Euclidean Distance

### Mathematical Definition

Euclidean distance measures the straight-line distance between two points:

```
euclidean_distance(A, B) = √(Σ(A_i - B_i)²)
```

Or equivalently:
```
euclidean_distance(A, B) = ||A - B||
```

**Range**: [0, ∞)
- 0 = identical vectors (most similar)
- ∞ = infinitely far apart (most dissimilar)

**Note**: Lower distances mean higher similarity (inverse of cosine).

### Visual Intuition

```
    B •
      |\
      | \
      |  \ d (Euclidean distance)
      |   \
      |    \
    A •─────•
```

Euclidean distance measures the straight-line distance between points. Shorter distances mean higher similarity.

### Key Properties

1. **Magnitude Sensitive**: Both direction and length matter
   ```
   euclidean_distance([1, 2, 3], [2, 4, 6]) = 3.74
   euclidean_distance([1, 2, 3], [1.1, 2.1, 3.1]) = 0.17
   # Different magnitudes → different distances
   ```

2. **Unbounded Range**: No upper limit on distance
   ```
   # Distance can be arbitrarily large
   euclidean_distance([0, 0], [1000, 1000]) = 1414.2
   ```

3. **Geometric Interpretation**: Actual distance in embedding space
   ```python
   # Distance between points in n-dimensional space
   distance = np.linalg.norm(A - B)
   ```

### When to Use Euclidean Distance

✅ **Use Euclidean distance when**:
- Vector magnitude carries semantic meaning
- Working with clustering algorithms (K-means, DBSCAN)
- Embeddings are not normalized
- Specific model was trained with Euclidean distance
- Working with spatial or geometric data

❌ **Don't use Euclidean distance when**:
- Embeddings are normalized (cosine is more appropriate)
- Working with text embeddings from sentence-transformers
- Following standard semantic search practices

### Implementation

#### FAISS with Euclidean Distance

```python
import faiss
import numpy as np

# Create index for L2 distance
dimension = 384
index = faiss.IndexFlatL2(dimension)  # L2 = Euclidean distance

# Add embeddings (no normalization needed)
embeddings = np.random.randn(100, dimension).astype('float32')
index.add(embeddings)

# Search (lower scores = more similar)
query = np.random.randn(1, dimension).astype('float32')
distances, indices = index.search(query, k=5)
```

#### NumPy with Euclidean Distance

```python
import numpy as np

def euclidean_distance(query: np.ndarray, embeddings: np.ndarray) -> np.ndarray:
    """Compute Euclidean distance between query and all embeddings.
    
    Args:
        query: Query vector of shape (embedding_dim,)
        embeddings: Matrix of shape (n_vectors, embedding_dim)
    
    Returns:
        Distance scores of shape (n_vectors,)
    """
    # Compute L2 distance
    distances = np.linalg.norm(embeddings - query, axis=1)
    
    return distances

# Example usage
query = np.array([1.0, 2.0, 3.0])
embeddings = np.array([
    [1.0, 2.0, 3.0],
    [4.0, 5.0, 6.0],
    [-1.0, -2.0, -3.0]
])

distances = euclidean_distance(query, embeddings)
print(distances)  # [0.0, 5.196, 7.483]
```

## Comparison

### Side-by-Side Comparison

| Aspect | Cosine Similarity | Euclidean Distance |
|--------|------------------|-------------------|
| **Measures** | Angle between vectors | Distance between points |
| **Range** | [0, 1] (normalized) | [0, ∞) |
| **Magnitude** | Ignores magnitude | Considers magnitude |
| **Interpretation** | Higher = more similar | Lower = more similar |
| **Normalization** | Requires normalization | No normalization needed |
| **Use case** | Semantic search | Clustering, spatial data |
| **Standard for** | Text embeddings | Geometric data |

### Example Comparison

```python
import numpy as np
from numpy.linalg import norm

# Three vectors
A = np.array([1, 2, 3])
B = np.array([2, 4, 6])  # Same direction as A, 2x magnitude
C = np.array([1, 2, 4])  # Similar to A, slightly different

# Cosine similarity
def cosine_sim(x, y):
    return np.dot(x, y) / (norm(x) * norm(y))

print("Cosine Similarity:")
print(f"A vs B: {cosine_sim(A, B):.4f}")  # 1.0000 (same direction)
print(f"A vs C: {cosine_sim(A, C):.4f}")  # 0.9923 (very similar)

# Euclidean distance
def euclidean_dist(x, y):
    return norm(x - y)

print("\nEuclidean Distance:")
print(f"A vs B: {euclidean_dist(A, B):.4f}")  # 3.7417 (different magnitude)
print(f"A vs C: {euclidean_dist(A, C):.4f}")  # 1.0000 (closer in space)
```

**Output**:
```
Cosine Similarity:
A vs B: 1.0000  # Identical direction → maximum similarity
A vs C: 0.9923  # Slightly different direction

Euclidean Distance:
A vs B: 3.7417  # Far apart due to magnitude difference
A vs C: 1.0000  # Closer in absolute space
```

**Interpretation**:
- **Cosine**: A and B are identical (same direction), C is slightly different
- **Euclidean**: C is closer to A than B is (considers magnitude)

### When Results Differ

Cosine and Euclidean can produce different rankings:

```python
query = np.array([1, 1])

candidates = [
    np.array([2, 2]),    # Same direction, 2x magnitude
    np.array([1, 1.1]),  # Very close in space
    np.array([10, 10])   # Same direction, 10x magnitude
]

# Cosine similarity (higher = better)
cosine_scores = [cosine_sim(query, c) for c in candidates]
print("Cosine ranking:", np.argsort(cosine_scores)[::-1])  # [0, 2, 1]

# Euclidean distance (lower = better)
euclidean_scores = [euclidean_dist(query, c) for c in candidates]
print("Euclidean ranking:", np.argsort(euclidean_scores))  # [1, 0, 2]
```

**Result**: Different metrics produce different rankings!

## Recommendations

### For This RAG System: Use Cosine Similarity

**Reasons**:

1. **Model Training**: sentence-transformers models are trained with cosine similarity
   ```python
   # Models optimize for cosine similarity during training
   model = SentenceTransformer('all-MiniLM-L6-v2')
   # Embeddings are designed for cosine comparison
   ```

2. **Normalization**: sentence-transformers normalizes embeddings by default
   ```python
   embeddings = model.encode(texts, normalize_embeddings=True)
   # Already normalized → cosine is appropriate
   ```

3. **Semantic Search Standard**: Industry standard for text retrieval
   - Pinecone, Weaviate, Qdrant all default to cosine
   - Vertex AI Vector Search uses cosine
   - Most RAG systems use cosine

4. **Interpretability**: Scores in [0, 1] are easier to interpret
   ```python
   score = 0.85  # 85% similar (intuitive)
   vs.
   distance = 3.74  # What does this mean? (less intuitive)
   ```

### Configuration

```python
from src.config import RAGConfig

# Recommended configuration
config = RAGConfig(
    similarity_metric="cosine",  # ← Use cosine
    vector_store_type="faiss",
    embedding_model="all-MiniLM-L6-v2"
)
```

### When to Consider Euclidean

Consider Euclidean distance if:
- You're using custom embeddings where magnitude matters
- You're implementing clustering (K-means, DBSCAN)
- You have specific domain knowledge that magnitude is important
- You're comparing against a baseline that uses Euclidean

## Implementation Examples

### Complete Example: Cosine Similarity

```python
from src.embedding import EmbeddingGenerator
from src.storage import FAISSVectorStore
from src.retrieval import RawVectorSearch
from src.orchestrator import RAGOrchestrator

# Initialize with cosine similarity
embedding_gen = EmbeddingGenerator(model_name="all-MiniLM-L6-v2")
vector_store = FAISSVectorStore(
    dimension=384,
    similarity_metric="cosine"  # ← Cosine similarity
)

# Create retrieval strategy
raw_strategy = RawVectorSearch(embedding_gen, vector_store)

# Create orchestrator
orchestrator = RAGOrchestrator(
    embedding_generator=embedding_gen,
    vector_store=vector_store,
    strategies={"raw": raw_strategy}
)

# Ingest documents
documents = [
    "Machine learning is a subset of artificial intelligence.",
    "Deep learning uses neural networks with multiple layers.",
    "Natural language processing enables computers to understand text."
]
orchestrator.ingest_documents(documents)

# Retrieve with cosine similarity
result = orchestrator.retrieve(
    query="What is deep learning?",
    strategy_name="raw",
    k=3
)

print(f"Top result: {result.chunks[0]}")
print(f"Similarity score: {result.scores[0]:.4f}")  # 0.0 to 1.0
```

### Complete Example: Euclidean Distance

```python
from src.embedding import EmbeddingGenerator
from src.storage import FAISSVectorStore
from src.retrieval import RawVectorSearch
from src.orchestrator import RAGOrchestrator

# Initialize with Euclidean distance
embedding_gen = EmbeddingGenerator(model_name="all-MiniLM-L6-v2")
vector_store = FAISSVectorStore(
    dimension=384,
    similarity_metric="euclidean"  # ← Euclidean distance
)

# Create retrieval strategy
raw_strategy = RawVectorSearch(embedding_gen, vector_store)

# Create orchestrator
orchestrator = RAGOrchestrator(
    embedding_generator=embedding_gen,
    vector_store=vector_store,
    strategies={"raw": raw_strategy}
)

# Ingest documents
documents = [
    "Machine learning is a subset of artificial intelligence.",
    "Deep learning uses neural networks with multiple layers.",
    "Natural language processing enables computers to understand text."
]
orchestrator.ingest_documents(documents)

# Retrieve with Euclidean distance
result = orchestrator.retrieve(
    query="What is deep learning?",
    strategy_name="raw",
    k=3
)

print(f"Top result: {result.chunks[0]}")
print(f"Distance score: {result.scores[0]:.4f}")  # Lower = more similar
```

## Performance Considerations

### Computational Complexity

Both metrics have similar complexity for brute-force search:

| Operation | Cosine | Euclidean |
|-----------|--------|-----------|
| **Single comparison** | O(d) | O(d) |
| **Search n vectors** | O(n×d) | O(n×d) |
| **Normalization** | O(d) | Not needed |

Where d = embedding dimension, n = number of vectors

### FAISS Optimization

FAISS provides optimized implementations:

```python
# Cosine (with normalization)
index = faiss.IndexFlatIP(dimension)
faiss.normalize_L2(embeddings)  # One-time cost
index.add(embeddings)

# Euclidean
index = faiss.IndexFlatL2(dimension)
index.add(embeddings)  # No normalization needed
```

**Performance**: Nearly identical for flat indices. Cosine has small overhead for normalization.

### Memory Usage

Both metrics use the same memory:
- Embeddings: `n × d × 4 bytes` (float32)
- Index overhead: Minimal for flat indices

### Recommendation

For this system, the performance difference is negligible. **Choose based on correctness, not performance.**

## Summary

### Quick Decision Guide

**Use Cosine Similarity if**:
- ✅ Using sentence-transformers or similar models
- ✅ Building a semantic search system
- ✅ Embeddings are normalized
- ✅ Following industry best practices

**Use Euclidean Distance if**:
- ✅ Vector magnitude is semantically meaningful
- ✅ Implementing clustering algorithms
- ✅ Working with spatial/geometric data
- ✅ Specific model requires it

### For This RAG System

**Recommendation: Use Cosine Similarity**

This is the correct choice because:
1. sentence-transformers models are trained with cosine
2. Embeddings are normalized by default
3. Industry standard for semantic search
4. Compatible with Vertex AI migration path

## References

- [Cosine Similarity Explained](https://www.pinecone.io/learn/vector-similarity/)
- [Distance Metrics in Machine Learning](https://machinelearningmastery.com/distance-measures-for-machine-learning/)
- [FAISS Documentation](https://github.com/facebookresearch/faiss/wiki)
- [Sentence-Transformers Documentation](https://www.sbert.net/)
