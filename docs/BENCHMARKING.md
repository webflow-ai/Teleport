# Benchmarking Guide

This guide explains how to run benchmarks, interpret results, and create custom query sets for the Context-Aware Retrieval Engine.

## Table of Contents

- [Overview](#overview)
- [Quick Start](#quick-start)
- [Running Benchmarks](#running-benchmarks)
- [Interpreting Results](#interpreting-results)
- [Creating Custom Query Sets](#creating-custom-query-sets)
- [Metrics Explained](#metrics-explained)
- [Best Practices](#best-practices)
- [Troubleshooting](#troubleshooting)

## Overview

### What is Benchmarking?

Benchmarking compares different retrieval strategies across a set of queries to determine which approach works better for your use case. The system measures:

- **Quality**: Similarity scores and relevance
- **Diversity**: Unique chunks retrieved
- **Consistency**: Overlap between strategies
- **Performance**: Retrieval latency

### Why Benchmark?

- **Strategy Selection**: Determine if query expansion improves results
- **Performance Tuning**: Identify bottlenecks and optimization opportunities
- **Quality Assessment**: Measure retrieval relevance quantitatively
- **Regression Testing**: Ensure changes don't degrade performance

### Available Strategies

The system includes two retrieval strategies:

1. **RawVectorSearch**: Direct embedding-based similarity search
   - Fast, straightforward
   - Best for well-formed queries

2. **AIEnhancedRetrieval**: Query expansion + similarity search
   - Adds synonyms and clarifications
   - Best for ambiguous or exploratory queries

## Quick Start

### Basic Benchmark

```python
from src.embedding import EmbeddingGenerator
from src.storage import NumpyVectorStore
from src.retrieval import RawVectorSearch, AIEnhancedRetrieval
from src.mocks import QueryExpander
from src.orchestrator import RAGOrchestrator
from src.benchmark import BenchmarkEngine

# Initialize components
embedding_gen = EmbeddingGenerator()
vector_store = NumpyVectorStore(similarity_metric="cosine")

# Create strategies
raw_strategy = RawVectorSearch(embedding_gen, vector_store)
query_expander = QueryExpander(expansion_strategy="synonym_addition")
enhanced_strategy = AIEnhancedRetrieval(embedding_gen, vector_store, query_expander)

# Create orchestrator
orchestrator = RAGOrchestrator(
    embedding_generator=embedding_gen,
    vector_store=vector_store,
    strategies={
        "raw": raw_strategy,
        "enhanced": enhanced_strategy
    }
)

# Ingest documents
documents = [
    "Microservices architecture is a design pattern...",
    "Load balancing distributes incoming network traffic...",
    "Caching is a technique used to store frequently accessed data..."
]
orchestrator.ingest_documents(documents)

# Run benchmark
benchmark = BenchmarkEngine(orchestrator)
queries = [
    "How does the system handle peak load?",
    "What is caching?",
    "How to improve database performance?"
]

metrics = benchmark.run_benchmark(
    queries=queries,
    output_path="retrieval_benchmark.md"
)

print("Benchmark complete! Results saved to retrieval_benchmark.md")
```

### Output

The benchmark generates a Markdown report with:
- Summary metrics table
- Result overlap analysis
- Per-query results with chunks and scores

## Running Benchmarks

### Step 1: Prepare Your Data

Ingest documents into the system:

```python
# Load your documents
documents = [
    "Document 1 content...",
    "Document 2 content...",
    "Document 3 content..."
]

# Ingest with appropriate chunk size
stats = orchestrator.ingest_documents(
    documents=documents,
    chunk_size=500  # Adjust based on your content
)

print(f"Ingested {stats.total_chunks} chunks")
```

### Step 2: Define Query Set

Create a list of representative queries:

```python
queries = [
    "Simple factual query",
    "Complex multi-part query with multiple concepts",
    "Ambiguous query that could mean different things",
    "Technical query with specific terminology",
    "Exploratory query seeking broad information"
]
```

**Tips**:
- Include 5-10 queries minimum
- Mix simple and complex queries
- Cover different query types (factual, exploratory, technical)
- Use queries representative of real user needs

### Step 3: Run Benchmark

```python
benchmark = BenchmarkEngine(orchestrator)

metrics = benchmark.run_benchmark(
    queries=queries,
    output_path="retrieval_benchmark.md"
)
```

### Step 4: Review Results

Open `retrieval_benchmark.md` to see the full report, or access metrics programmatically:

```python
for strategy_name, strategy_metrics in metrics.items():
    print(f"\n{strategy_name}:")
    print(f"  Avg Similarity: {strategy_metrics.avg_similarity_score:.4f}")
    print(f"  Unique Chunks: {strategy_metrics.unique_chunks_retrieved}")
    print(f"  Avg Latency: {strategy_metrics.avg_latency_ms:.2f}ms")
```

## Interpreting Results

### Summary Metrics Table

```markdown
| Strategy | Avg Similarity Score | Unique Chunks | Avg Latency (ms) |
|----------|---------------------|---------------|------------------|
| raw      | 0.7234              | 12            | 38.45            |
| enhanced | 0.7891              | 15            | 342.67           |
```

**How to Read**:

1. **Avg Similarity Score** (higher is better)
   - Range: 0.0 to 1.0 for cosine similarity
   - Measures average relevance of retrieved chunks
   - **Good**: > 0.70
   - **Excellent**: > 0.85

2. **Unique Chunks** (context-dependent)
   - Total unique chunks retrieved across all queries
   - Higher = more diverse results
   - Compare to total chunks in store
   - **Interpretation**: Enhanced strategy retrieved 3 more unique chunks (25% increase)

3. **Avg Latency** (lower is better)
   - Average time to complete retrieval
   - **Target**: < 500ms for good user experience
   - **Note**: Enhanced strategy is slower due to query expansion

### Result Overlap Analysis

```markdown
**raw ∩ enhanced**: 8 common chunks
```

**Interpretation**:
- 8 chunks retrieved by both strategies
- High overlap (>70%) = strategies agree on relevance
- Low overlap (<30%) = strategies find different content
- **Example**: 8/12 = 67% overlap suggests reasonable agreement

### Per-Query Results

```markdown
### Query 1: "How does the system handle peak load?"

#### raw
**Latency**: 35.23 ms
**Retrieved Chunks**:
1. **Score: 0.8234**
   ```
   Load balancing distributes incoming network traffic...
   ```
```

**How to Read**:

1. **Latency**: Time for this specific query
   - Compare across strategies
   - Identify slow queries

2. **Score**: Similarity score for each chunk
   - Higher = more relevant
   - Compare top scores across strategies

3. **Chunks**: Actual retrieved content
   - Manually assess relevance
   - Check if results answer the query

### Making Decisions

#### When Raw Search is Better

- Similar or better similarity scores
- Much faster latency
- Sufficient result quality
- Well-formed queries

**Action**: Use raw search for production

#### When Enhanced Retrieval is Better

- Significantly better similarity scores (+10% or more)
- More diverse results
- Better handles ambiguous queries
- Latency is acceptable

**Action**: Use enhanced retrieval, or use raw for simple queries and enhanced for complex ones

#### When Results are Mixed

- Some queries better with raw, others with enhanced
- Significant latency difference
- Similar overall quality

**Action**: Implement hybrid approach (route based on query complexity)

## Creating Custom Query Sets

### Query Set Design Principles

1. **Representative**: Reflect actual user queries
2. **Diverse**: Cover different query types and complexities
3. **Challenging**: Include edge cases and difficult queries
4. **Measurable**: Enable clear comparison between strategies

### Query Types to Include

#### 1. Factual Queries

Simple, direct questions with clear answers:

```python
factual_queries = [
    "What is caching?",
    "Define microservices architecture",
    "What is load balancing?"
]
```

**Purpose**: Test basic retrieval accuracy

#### 2. Complex Queries

Multi-part questions with multiple concepts:

```python
complex_queries = [
    "How does the system handle peak load and ensure high availability?",
    "What are the trade-offs between caching and database indexing?",
    "How to implement authentication and authorization in microservices?"
]
```

**Purpose**: Test query expansion effectiveness

#### 3. Ambiguous Queries

Queries with multiple possible interpretations:

```python
ambiguous_queries = [
    "How to improve performance?",  # Performance of what?
    "What about security?",  # Which aspect of security?
    "Tell me about scaling"  # Horizontal? Vertical? What component?
]
```

**Purpose**: Test query clarification capabilities

#### 4. Technical Queries

Domain-specific terminology:

```python
technical_queries = [
    "How does eventual consistency work in distributed systems?",
    "What is the CAP theorem?",
    "Explain ACID properties in databases"
]
```

**Purpose**: Test handling of specialized vocabulary

#### 5. Exploratory Queries

Broad, open-ended questions:

```python
exploratory_queries = [
    "What are best practices for system design?",
    "How to build scalable applications?",
    "What should I know about cloud architecture?"
]
```

**Purpose**: Test result diversity and coverage

### Complete Query Set Example

```python
# Comprehensive benchmark query set
benchmark_queries = [
    # Factual (2 queries)
    "What is load balancing?",
    "Define microservices architecture",
    
    # Complex (2 queries)
    "How does the system handle peak load and ensure availability?",
    "What are the trade-offs between caching and database indexing?",
    
    # Ambiguous (2 queries)
    "How to improve performance?",
    "What about security?",
    
    # Technical (2 queries)
    "How does eventual consistency work in distributed systems?",
    "Explain ACID properties in databases",
    
    # Exploratory (2 queries)
    "What are best practices for system design?",
    "How to build scalable applications?"
]

# Run benchmark
metrics = benchmark.run_benchmark(
    queries=benchmark_queries,
    output_path="comprehensive_benchmark.md"
)
```

### Query Set Size Recommendations

| Use Case | Recommended Size | Rationale |
|----------|-----------------|-----------|
| **Quick Test** | 3-5 queries | Fast feedback during development |
| **Standard Benchmark** | 10-20 queries | Good balance of coverage and speed |
| **Comprehensive Evaluation** | 50-100 queries | Thorough assessment for production |
| **Continuous Testing** | 20-30 queries | Regular regression testing |

## Metrics Explained

### Average Similarity Score

**Definition**: Mean of all similarity scores across all queries and all retrieved chunks.

**Calculation**:
```python
all_scores = []
for result in query_results:
    all_scores.extend(result.scores)

avg_similarity = sum(all_scores) / len(all_scores)
```

**Interpretation**:
- **0.0 - 0.5**: Poor relevance, results not matching queries
- **0.5 - 0.7**: Moderate relevance, some good results
- **0.7 - 0.85**: Good relevance, most results are relevant
- **0.85 - 1.0**: Excellent relevance, highly accurate retrieval

**Limitations**:
- Doesn't account for result ranking
- Sensitive to outliers
- Doesn't measure diversity

### Unique Chunks Retrieved

**Definition**: Total number of distinct chunks retrieved across all queries.

**Calculation**:
```python
unique_chunks = set()
for result in query_results:
    unique_chunks.update(result.chunks)

count = len(unique_chunks)
```

**Interpretation**:
- **Low** (< 30% of total chunks): Strategy retrieves similar content repeatedly
- **Medium** (30-70% of total chunks): Balanced coverage
- **High** (> 70% of total chunks): Strategy explores diverse content

**Use Cases**:
- Measure result diversity
- Identify if strategy is too narrow or too broad
- Compare coverage between strategies

### Average Latency

**Definition**: Mean retrieval time across all queries.

**Calculation**:
```python
total_latency = sum(result.latency_ms for result in query_results)
avg_latency = total_latency / len(query_results)
```

**Interpretation**:
- **< 100ms**: Excellent, near-instant response
- **100-500ms**: Good, acceptable for most applications
- **500-1000ms**: Moderate, noticeable delay
- **> 1000ms**: Poor, needs optimization

**Factors Affecting Latency**:
- Vector store size
- Query expansion (adds 200-300ms)
- Embedding generation
- Hardware (CPU vs GPU)

### Result Overlap

**Definition**: Number of chunks retrieved by multiple strategies.

**Calculation**:
```python
chunks_strategy1 = set(all_chunks_from_strategy1)
chunks_strategy2 = set(all_chunks_from_strategy2)

overlap = chunks_strategy1.intersection(chunks_strategy2)
overlap_count = len(overlap)
```

**Interpretation**:
- **High overlap** (> 70%): Strategies agree on relevance
- **Medium overlap** (30-70%): Some agreement, some divergence
- **Low overlap** (< 30%): Strategies find different content

**Implications**:
- High overlap + high scores = both strategies work well
- High overlap + low scores = both strategies struggle
- Low overlap = strategies complement each other (consider hybrid)

## Best Practices

### 1. Establish Baselines

Run initial benchmark before making changes:

```python
# Baseline benchmark
baseline_metrics = benchmark.run_benchmark(
    queries=standard_queries,
    output_path="baseline_benchmark.md"
)

# Save baseline scores
baseline_scores = {
    name: metrics.avg_similarity_score 
    for name, metrics in baseline_metrics.items()
}
```

### 2. Use Consistent Query Sets

Maintain a standard query set for regression testing:

```python
# tests/fixtures/benchmark_queries.py
STANDARD_QUERIES = [
    "Query 1...",
    "Query 2...",
    # ... 10-20 queries
]

# Use in all benchmarks
from tests.fixtures.benchmark_queries import STANDARD_QUERIES
metrics = benchmark.run_benchmark(queries=STANDARD_QUERIES)
```

### 3. Benchmark After Changes

Run benchmarks after:
- Changing embedding models
- Modifying chunking strategy
- Updating query expansion logic
- Adjusting similarity metrics

```python
# Before change
before_metrics = benchmark.run_benchmark(queries, "before.md")

# Make changes...

# After change
after_metrics = benchmark.run_benchmark(queries, "after.md")

# Compare
for strategy in before_metrics:
    before_score = before_metrics[strategy].avg_similarity_score
    after_score = after_metrics[strategy].avg_similarity_score
    improvement = ((after_score - before_score) / before_score) * 100
    print(f"{strategy}: {improvement:+.2f}% change")
```

### 4. Manual Relevance Assessment

Quantitative metrics don't tell the whole story. Manually review results:

```python
# Review top results for each query
for query_idx, query in enumerate(queries):
    print(f"\nQuery: {query}")
    
    for strategy_name, metrics in benchmark_metrics.items():
        result = metrics.query_results[query_idx]
        print(f"\n{strategy_name}:")
        print(f"  Top chunk: {result.chunks[0][:100]}...")
        print(f"  Score: {result.scores[0]:.4f}")
        
        # Manual assessment
        relevant = input("  Relevant? (y/n): ")
        # Track manual relevance scores
```

### 5. Track Metrics Over Time

Maintain a log of benchmark results:

```python
import json
from datetime import datetime

# Save metrics
benchmark_log = {
    "timestamp": datetime.now().isoformat(),
    "metrics": {
        name: {
            "avg_similarity": metrics.avg_similarity_score,
            "unique_chunks": metrics.unique_chunks_retrieved,
            "avg_latency": metrics.avg_latency_ms
        }
        for name, metrics in benchmark_metrics.items()
    }
}

with open("benchmark_history.jsonl", "a") as f:
    f.write(json.dumps(benchmark_log) + "\n")
```

### 6. Test with Real User Queries

If possible, use actual user queries:

```python
# Load real queries from logs
with open("user_queries.log") as f:
    real_queries = [line.strip() for line in f.readlines()]

# Sample representative queries
import random
sample_queries = random.sample(real_queries, 20)

# Benchmark with real queries
metrics = benchmark.run_benchmark(queries=sample_queries)
```

## Troubleshooting

### Issue: All Scores Are Low (< 0.5)

**Possible Causes**:
- Documents and queries are semantically different
- Chunk size too large or too small
- Wrong similarity metric
- Embedding model not suitable for domain

**Solutions**:
```python
# Try different chunk size
stats = orchestrator.ingest_documents(documents, chunk_size=300)

# Verify similarity metric
config = RAGConfig(similarity_metric="cosine")  # Recommended

# Try different embedding model
embedding_gen = EmbeddingGenerator(model_name="all-mpnet-base-v2")
```

### Issue: Enhanced Strategy Not Improving Results

**Possible Causes**:
- Query expansion not effective
- Queries already well-formed
- Expansion strategy not appropriate

**Solutions**:
```python
# Try different expansion strategy
query_expander = QueryExpander(expansion_strategy="clarification")

# Check expansion log
print(query_expander.get_interaction_log())

# Compare expanded vs original queries
for log_entry in query_expander.get_interaction_log():
    print(f"Original: {log_entry['original']}")
    print(f"Expanded: {log_entry['expanded']}")
    print()
```

### Issue: High Latency

**Possible Causes**:
- Large vector store
- Slow embedding generation
- Query expansion overhead

**Solutions**:
```python
# Use FAISS for better performance
vector_store = FAISSVectorStore(dimension=384, similarity_metric="cosine")

# Profile latency components
import time

start = time.time()
embedding = embedding_gen.encode(query)
print(f"Embedding: {(time.time() - start) * 1000:.2f}ms")

start = time.time()
results = vector_store.search(embedding, k=3)
print(f"Search: {(time.time() - start) * 1000:.2f}ms")
```

### Issue: Inconsistent Results

**Possible Causes**:
- Non-deterministic query expansion
- Floating-point precision issues
- Random sampling in strategies

**Solutions**:
```python
# Set random seeds for reproducibility
import random
import numpy as np

random.seed(42)
np.random.seed(42)

# Run benchmark multiple times
results_list = []
for i in range(3):
    metrics = benchmark.run_benchmark(queries, f"run_{i}.md")
    results_list.append(metrics)

# Check consistency
for strategy in results_list[0]:
    scores = [r[strategy].avg_similarity_score for r in results_list]
    print(f"{strategy}: {scores}")
```

## Example: Complete Benchmark Workflow

```python
from src.embedding import EmbeddingGenerator
from src.storage import FAISSVectorStore
from src.retrieval import RawVectorSearch, AIEnhancedRetrieval
from src.mocks import QueryExpander
from src.orchestrator import RAGOrchestrator
from src.benchmark import BenchmarkEngine

# 1. Initialize system
embedding_gen = EmbeddingGenerator(model_name="all-MiniLM-L6-v2")
vector_store = FAISSVectorStore(dimension=384, similarity_metric="cosine")

raw_strategy = RawVectorSearch(embedding_gen, vector_store)
query_expander = QueryExpander(expansion_strategy="synonym_addition")
enhanced_strategy = AIEnhancedRetrieval(embedding_gen, vector_store, query_expander)

orchestrator = RAGOrchestrator(
    embedding_generator=embedding_gen,
    vector_store=vector_store,
    strategies={"raw": raw_strategy, "enhanced": enhanced_strategy}
)

# 2. Ingest documents
documents = [
    # Your documents here
]
stats = orchestrator.ingest_documents(documents, chunk_size=500)
print(f"Ingested {stats.total_chunks} chunks")

# 3. Define query set
queries = [
    "How does the system handle peak load?",
    "What is caching?",
    "How to improve database performance?",
    "What are microservices?",
    "Explain load balancing"
]

# 4. Run benchmark
benchmark = BenchmarkEngine(orchestrator)
metrics = benchmark.run_benchmark(
    queries=queries,
    output_path="retrieval_benchmark.md"
)

# 5. Analyze results
print("\n=== Benchmark Results ===\n")
for strategy_name, strategy_metrics in metrics.items():
    print(f"{strategy_name}:")
    print(f"  Avg Similarity: {strategy_metrics.avg_similarity_score:.4f}")
    print(f"  Unique Chunks: {strategy_metrics.unique_chunks_retrieved}")
    print(f"  Avg Latency: {strategy_metrics.avg_latency_ms:.2f}ms")
    print()

# 6. Make decision
raw_score = metrics["raw"].avg_similarity_score
enhanced_score = metrics["enhanced"].avg_similarity_score

if enhanced_score > raw_score * 1.1:  # 10% improvement
    print("✓ Enhanced retrieval shows significant improvement")
    print("  Recommendation: Use enhanced retrieval")
else:
    print("✓ Raw search performs well")
    print("  Recommendation: Use raw search for better latency")
```

## Resources

- [Benchmark Engine API](API.md#benchmark-engine)
- [Example Benchmark Script](../examples/demo_benchmark.py)
- [Test Fixtures](../tests/fixtures/benchmark_queries.py)
- [Architecture Documentation](ARCHITECTURE.md)
