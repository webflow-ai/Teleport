# Migration Guide: Local to Vertex AI

This guide provides a comprehensive path for migrating the Context-Aware Retrieval Engine from local execution to Google Cloud's Vertex AI services.

## Table of Contents

- [Overview](#overview)
- [Migration Strategy](#migration-strategy)
- [Component Migration](#component-migration)
- [Cost Analysis](#cost-analysis)
- [Performance Comparison](#performance-comparison)
- [Step-by-Step Migration](#step-by-step-migration)
- [Testing and Validation](#testing-and-validation)
- [Rollback Strategy](#rollback-strategy)

## Overview

### Current Local Implementation

The system currently runs entirely on local infrastructure:

| Component | Local Implementation | Purpose |
|-----------|---------------------|---------|
| **Embeddings** | sentence-transformers (`all-MiniLM-L6-v2`) | Convert text to 384-dim vectors |
| **Vector Store** | FAISS/ChromaDB/NumPy | Store and search embeddings |
| **Query Expansion** | Rule-based mock | Enhance queries with synonyms |
| **Infrastructure** | Single Python process | Local compute and storage |

### Target Cloud Implementation

Migration to Vertex AI provides managed, scalable services:

| Component | Vertex AI Service | Benefits |
|-----------|------------------|----------|
| **Embeddings** | Text Embedding API (`textembedding-gecko@003`) | Better accuracy, managed scaling |
| **Vector Store** | Vector Search (Matching Engine) | Distributed, auto-scaling, managed |
| **Query Expansion** | Generative AI (`gemini-pro`) | True LLM-based expansion |
| **Infrastructure** | Managed services | Auto-scaling, high availability |

### Why Migrate?

**Advantages of Cloud Migration**:
- **Scalability**: Handle 1000s of queries per second
- **Accuracy**: Better embedding models optimized for semantic search
- **Reliability**: Managed services with SLAs
- **Features**: Advanced capabilities (hybrid search, reranking)
- **Maintenance**: No infrastructure management

**When to Stay Local**:
- Data privacy requirements (on-premises only)
- Cost constraints (high query volume)
- Development and testing
- Proof-of-concept projects

## Migration Strategy

### Three-Phase Approach

#### Phase 1: Interface Compatibility (Current)

The system is already designed with Vertex AI compatibility:

```python
# Current mock interfaces match Vertex AI
class EmbeddingGenerator:
    def encode(self, texts: Union[str, List[str]]) -> np.ndarray:
        # Matches TextEmbeddingModel.get_embeddings()
        pass

class QueryExpander:
    def expand_query(self, query: str) -> str:
        # Matches GenerativeModel.generate_content()
        pass
```

**Status**: ✅ Complete (current implementation)

#### Phase 2: Hybrid Deployment

Run local and cloud components side-by-side for validation:

```python
# Configuration-based switching
config = RAGConfig(
    embedding_provider="vertex_ai",  # or "local"
    vector_store_type="matching_engine",  # or "faiss"
    query_expander="vertex_ai"  # or "mock"
)

# Factory pattern for provider selection
embedding_generator = EmbeddingFactory.create(config.embedding_provider)
vector_store = VectorStoreFactory.create(config.vector_store_type)
query_expander = QueryExpanderFactory.create(config.query_expander)
```

**Duration**: 2-4 weeks

**Goals**:
- Validate cloud components work correctly
- Compare performance and accuracy
- Identify migration issues early

#### Phase 3: Full Cloud Migration

Replace all local components with Vertex AI services:

```python
from google.cloud import aiplatform
from vertexai.language_models import TextEmbeddingModel, GenerativeModel

# Initialize Vertex AI
aiplatform.init(project="your-project", location="us-central1")

# Use Vertex AI services
embedding_model = TextEmbeddingModel.from_pretrained("textembedding-gecko@003")
vector_search = aiplatform.MatchingEngineIndexEndpoint(endpoint_name)
generative_model = GenerativeModel("gemini-pro")
```

**Duration**: 4-6 weeks

**Goals**:
- Complete migration to cloud services
- Decommission local infrastructure
- Optimize for cost and performance

## Component Migration

### 1. Embedding Generation

#### Current Implementation (Local)

```python
from sentence_transformers import SentenceTransformer
import numpy as np

class EmbeddingGenerator:
    """Local embedding generation using sentence-transformers."""
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)
    
    def encode(self, texts: Union[str, List[str]]) -> np.ndarray:
        """Generate embeddings locally."""
        if isinstance(texts, str):
            texts = [texts]
        return self.model.encode(texts)
    
    def get_embedding_dimension(self) -> int:
        return self.model.get_sentence_embedding_dimension()
```

**Characteristics**:
- Embedding dimension: 384
- Latency: ~50ms per chunk (CPU)
- Cost: Zero (local compute)
- Accuracy: Good for general text

#### Migrated Implementation (Vertex AI)

```python
from vertexai.language_models import TextEmbeddingModel
import numpy as np
from typing import Union, List

class VertexAIEmbeddingGenerator:
    """Cloud embedding generation using Vertex AI."""
    
    def __init__(self, model_name: str = "textembedding-gecko@003"):
        self.model = TextEmbeddingModel.from_pretrained(model_name)
        self._dimension = 768  # gecko model dimension
    
    def encode(self, texts: Union[str, List[str]]) -> np.ndarray:
        """Generate embeddings via Vertex AI API."""
        if isinstance(texts, str):
            texts = [texts]
        
        # Batch API call
        embeddings = self.model.get_embeddings(texts)
        
        # Convert to numpy array
        return np.array([emb.values for emb in embeddings])
    
    def get_embedding_dimension(self) -> int:
        return self._dimension
```

**Characteristics**:
- Embedding dimension: 768 (higher quality)
- Latency: ~100-200ms per batch (network + API)
- Cost: ~$0.0001 per 1000 characters
- Accuracy: Optimized for semantic search

#### Migration Steps

1. **Install Vertex AI SDK**:
```bash
pip install google-cloud-aiplatform
```

2. **Set up authentication**:
```bash
gcloud auth application-default login
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/service-account-key.json"
```

3. **Update configuration**:
```python
config = RAGConfig(
    embedding_model="textembedding-gecko@003",
    embedding_provider="vertex_ai"
)
```

4. **Test compatibility**:
```python
# Test both implementations produce valid embeddings
local_gen = EmbeddingGenerator()
cloud_gen = VertexAIEmbeddingGenerator()

test_text = "This is a test sentence."
local_emb = local_gen.encode(test_text)
cloud_emb = cloud_gen.encode(test_text)

assert local_emb.shape[0] == cloud_emb.shape[0]  # Same batch size
print(f"Local dimension: {local_emb.shape[1]}")  # 384
print(f"Cloud dimension: {cloud_emb.shape[1]}")  # 768
```

5. **Re-index documents**: Embeddings have different dimensions, so you must re-ingest all documents with the new model.

### 2. Vector Store

#### Current Implementation (FAISS)

```python
import faiss
import numpy as np
import json
from typing import List, Dict, Optional

class FAISSVectorStore:
    """Local vector store using FAISS."""
    
    def __init__(self, dimension: int, similarity_metric: str = "cosine"):
        self.dimension = dimension
        self.similarity_metric = similarity_metric
        
        # Create FAISS index
        if similarity_metric == "cosine":
            self.index = faiss.IndexFlatIP(dimension)  # Inner product
        else:
            self.index = faiss.IndexFlatL2(dimension)  # L2 distance
        
        self.texts = []
        self.metadata = []
    
    def add(self, embeddings: np.ndarray, texts: List[str], 
            metadata: Optional[List[Dict]] = None):
        """Add embeddings to local index."""
        if self.similarity_metric == "cosine":
            faiss.normalize_L2(embeddings)  # Normalize for cosine
        
        self.index.add(embeddings)
        self.texts.extend(texts)
        self.metadata.extend(metadata or [{}] * len(texts))
    
    def search(self, query_embedding: np.ndarray, k: int = 3):
        """Search local index."""
        if self.similarity_metric == "cosine":
            faiss.normalize_L2(query_embedding)
        
        scores, indices = self.index.search(query_embedding, k)
        
        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx < len(self.texts):
                results.append(SearchResult(
                    text=self.texts[idx],
                    score=float(score),
                    metadata=self.metadata[idx]
                ))
        return results
```

**Characteristics**:
- Storage: In-memory or local disk
- Latency: 10-50ms for 1000 chunks
- Scalability: Limited by single machine
- Cost: Zero (local storage)

#### Migrated Implementation (Vertex AI Matching Engine)

```python
from google.cloud import aiplatform
from google.cloud.aiplatform import MatchingEngineIndex, MatchingEngineIndexEndpoint
import numpy as np
from typing import List, Dict, Optional

class MatchingEngineVectorStore:
    """Cloud vector store using Vertex AI Matching Engine."""
    
    def __init__(self, 
                 project_id: str,
                 location: str,
                 index_endpoint_name: str,
                 deployed_index_id: str):
        aiplatform.init(project=project_id, location=location)
        
        self.endpoint = MatchingEngineIndexEndpoint(index_endpoint_name)
        self.deployed_index_id = deployed_index_id
        self._id_counter = 0
    
    def add(self, embeddings: np.ndarray, texts: List[str], 
            metadata: Optional[List[Dict]] = None):
        """Add embeddings to Matching Engine."""
        datapoints = []
        
        for i, (emb, text) in enumerate(zip(embeddings, texts)):
            datapoint_id = f"doc_{self._id_counter}"
            self._id_counter += 1
            
            # Store text in restricts for retrieval
            restricts = [{"namespace": "text", "allow_list": [text]}]
            
            # Add metadata if provided
            if metadata and i < len(metadata):
                for key, value in metadata[i].items():
                    restricts.append({
                        "namespace": key,
                        "allow_list": [str(value)]
                    })
            
            datapoints.append(
                aiplatform.MatchingEngineIndexDatapoint(
                    datapoint_id=datapoint_id,
                    feature_vector=emb.tolist(),
                    restricts=restricts
                )
            )
        
        # Batch upsert to Matching Engine
        self.endpoint.upsert_datapoints(datapoints)
    
    def search(self, query_embedding: np.ndarray, k: int = 3):
        """Search Matching Engine."""
        response = self.endpoint.find_neighbors(
            deployed_index_id=self.deployed_index_id,
            queries=[query_embedding.tolist()],
            num_neighbors=k
        )
        
        results = []
        for neighbor in response[0]:
            # Extract text from restricts
            text = neighbor.restricts[0]["allow_list"][0]
            
            # Extract metadata
            metadata = {}
            for restrict in neighbor.restricts[1:]:
                namespace = restrict["namespace"]
                value = restrict["allow_list"][0]
                metadata[namespace] = value
            
            results.append(SearchResult(
                text=text,
                score=neighbor.distance,
                metadata=metadata
            ))
        
        return results
```

**Characteristics**:
- Storage: Distributed, managed
- Latency: 50-150ms (network overhead)
- Scalability: Auto-scaling to millions of vectors
- Cost: ~$0.50/hour per node + storage

#### Migration Steps

1. **Create Matching Engine Index**:
```bash
# Create index
gcloud ai indexes create \
  --display-name="rag-index" \
  --description="RAG vector index" \
  --metadata-file=index-metadata.json \
  --project=your-project \
  --region=us-central1
```

2. **Create Index Endpoint**:
```bash
# Create endpoint
gcloud ai index-endpoints create \
  --display-name="rag-endpoint" \
  --project=your-project \
  --region=us-central1
```

3. **Deploy Index to Endpoint**:
```bash
# Deploy index
gcloud ai index-endpoints deploy-index INDEX_ENDPOINT_ID \
  --deployed-index-id=rag_deployed \
  --index=INDEX_ID \
  --project=your-project \
  --region=us-central1
```

4. **Migrate data**: Re-ingest all documents using the new vector store.

### 3. Query Expansion

#### Current Implementation (Mock)

```python
class QueryExpander:
    """Rule-based query expansion mock."""
    
    def __init__(self, expansion_strategy: str = "synonym_addition"):
        self.expansion_strategy = expansion_strategy
        self.interaction_log = []
        
        # Simple synonym dictionary
        self.synonyms = {
            "system": "application software platform",
            "handle": "process manage deal",
            "load": "traffic requests workload",
            "performance": "speed efficiency throughput",
            "database": "datastore storage repository"
        }
    
    def expand_query(self, query: str) -> str:
        """Expand query using rule-based logic."""
        expanded = query
        
        if self.expansion_strategy == "synonym_addition":
            # Add synonyms for matching terms
            for term, synonyms in self.synonyms.items():
                if term in query.lower():
                    expanded += f" {synonyms}"
        
        elif self.expansion_strategy == "clarification":
            # Add clarifying context
            expanded = f"{query} (specifically regarding technical implementation)"
        
        elif self.expansion_strategy == "decomposition":
            # Break into sub-queries
            expanded = f"{query} AND related concepts"
        
        # Log interaction
        self.interaction_log.append({
            "original": query,
            "expanded": expanded,
            "strategy": self.expansion_strategy
        })
        
        return expanded
```

**Characteristics**:
- Quality: Basic, rule-based
- Latency: <1ms
- Cost: Zero
- Flexibility: Limited to predefined rules

#### Migrated Implementation (Vertex AI Gemini)

```python
from vertexai.generative_models import GenerativeModel

class VertexAIQueryExpander:
    """LLM-based query expansion using Vertex AI Gemini."""
    
    def __init__(self, model_name: str = "gemini-pro"):
        self.model = GenerativeModel(model_name)
        self.interaction_log = []
    
    def expand_query(self, query: str) -> str:
        """Expand query using Gemini LLM."""
        prompt = f"""You are a query expansion assistant for a semantic search system.
        
Your task: Expand the following search query by adding relevant synonyms, related terms, 
and clarifications that would help retrieve more comprehensive results.

Rules:
1. Keep the expansion concise (under 100 words)
2. Add synonyms for key technical terms
3. Include related concepts
4. Maintain the original query intent
5. Do not add unrelated information

Original query: {query}

Expanded query:"""
        
        try:
            response = self.model.generate_content(prompt)
            expanded = response.text.strip()
            
            # Log interaction
            self.interaction_log.append({
                "original": query,
                "expanded": expanded,
                "model": "gemini-pro"
            })
            
            return expanded
            
        except Exception as e:
            # Fallback to original query on error
            print(f"Query expansion failed: {e}")
            return query
    
    def get_interaction_log(self) -> List[Dict]:
        """Return interaction log."""
        return self.interaction_log
```

**Characteristics**:
- Quality: High, context-aware
- Latency: 200-500ms
- Cost: ~$0.00025 per 1000 characters
- Flexibility: Adapts to any query type

#### Migration Steps

1. **Install Vertex AI SDK** (if not already done):
```bash
pip install google-cloud-aiplatform
```

2. **Enable Generative AI API**:
```bash
gcloud services enable aiplatform.googleapis.com
```

3. **Update configuration**:
```python
config = RAGConfig(
    query_expander="vertex_ai",
    expansion_model="gemini-pro"
)
```

4. **Test expansion quality**:
```python
# Compare expansions
mock_expander = QueryExpander()
gemini_expander = VertexAIQueryExpander()

test_query = "How does the system handle peak load?"

mock_result = mock_expander.expand_query(test_query)
gemini_result = gemini_expander.expand_query(test_query)

print(f"Original: {test_query}")
print(f"Mock: {mock_result}")
print(f"Gemini: {gemini_result}")
```

## Cost Analysis

### Local Implementation Costs

| Component | Cost |
|-----------|------|
| Compute | $0 (local hardware) |
| Storage | $0 (local disk) |
| API calls | $0 |
| **Total** | **$0/month** |

**Considerations**:
- Hardware depreciation not included
- Electricity costs not included
- Maintenance time not included

### Vertex AI Implementation Costs

#### Embedding API

- **Pricing**: $0.0001 per 1000 characters
- **Example**: 10,000 queries × 100 chars = 1M characters = $0.10

#### Vector Search (Matching Engine)

- **Index storage**: $0.30 per GB per month
- **Query serving**: $0.50 per hour per node
- **Example**: 2 nodes × 24 hours × 30 days = $720/month

#### Generative AI (Gemini)

- **Pricing**: $0.00025 per 1000 characters (input + output)
- **Example**: 10,000 queries × 200 chars = 2M characters = $0.50

#### Total Monthly Cost Estimate

| Scenario | Queries/Month | Estimated Cost |
|----------|---------------|----------------|
| **Development** | 1,000 | $50-100 |
| **Small Production** | 10,000 | $100-300 |
| **Medium Production** | 100,000 | $500-1,500 |
| **Large Production** | 1,000,000 | $3,000-10,000 |

**Cost Optimization Tips**:
1. Use batch API calls to reduce overhead
2. Cache frequent queries
3. Scale down during off-peak hours
4. Use committed use discounts for predictable workloads

## Performance Comparison

### Latency

| Operation | Local | Vertex AI | Difference |
|-----------|-------|-----------|------------|
| Embedding generation | 50ms | 150ms | +100ms (network) |
| Vector search | 20ms | 80ms | +60ms (network) |
| Query expansion | 1ms | 300ms | +299ms (LLM) |
| **Total retrieval** | **71ms** | **530ms** | **+459ms** |

**Note**: Vertex AI latency includes network overhead. Actual latency varies by region and load.

### Accuracy

| Metric | Local | Vertex AI | Improvement |
|--------|-------|-----------|-------------|
| Embedding quality | Good | Excellent | +15-20% |
| Query expansion | Basic | Advanced | +30-40% |
| Retrieval relevance | 0.75 | 0.85 | +13% |

**Note**: Accuracy improvements based on typical semantic search benchmarks.

### Scalability

| Aspect | Local | Vertex AI |
|--------|-------|-----------|
| Max QPS | 10-50 | 1,000+ |
| Max vectors | 100K | 10M+ |
| Concurrent users | 1-10 | 1,000+ |
| Availability | Single point of failure | 99.9% SLA |

## Step-by-Step Migration

### Week 1-2: Preparation

1. **Set up GCP project**:
```bash
gcloud projects create your-project-id
gcloud config set project your-project-id
```

2. **Enable required APIs**:
```bash
gcloud services enable aiplatform.googleapis.com
gcloud services enable storage.googleapis.com
```

3. **Create service account**:
```bash
gcloud iam service-accounts create rag-service-account
gcloud projects add-iam-policy-binding your-project-id \
  --member="serviceAccount:rag-service-account@your-project-id.iam.gserviceaccount.com" \
  --role="roles/aiplatform.user"
```

4. **Install dependencies**:
```bash
pip install google-cloud-aiplatform
```

### Week 3-4: Hybrid Deployment

1. **Implement factory pattern**:
```python
class EmbeddingFactory:
    @staticmethod
    def create(provider: str, **kwargs):
        if provider == "local":
            return EmbeddingGenerator(**kwargs)
        elif provider == "vertex_ai":
            return VertexAIEmbeddingGenerator(**kwargs)
        else:
            raise ValueError(f"Unknown provider: {provider}")
```

2. **Deploy hybrid system**:
```python
# Configuration
config = RAGConfig(
    embedding_provider="vertex_ai",  # Use cloud embeddings
    vector_store_type="faiss",       # Keep local storage
    query_expander="mock"            # Keep local expansion
)

# Create components
embedding_gen = EmbeddingFactory.create(config.embedding_provider)
vector_store = VectorStoreFactory.create(config.vector_store_type)
query_expander = QueryExpanderFactory.create(config.query_expander)
```

3. **Run A/B tests**: Compare local vs. cloud embeddings

### Week 5-6: Full Migration

1. **Create Matching Engine resources** (see Component Migration section)

2. **Migrate data**:
```python
# Re-ingest all documents with cloud embeddings
orchestrator = RAGOrchestrator(
    embedding_generator=VertexAIEmbeddingGenerator(),
    vector_store=MatchingEngineVectorStore(...),
    strategies={...}
)

orchestrator.ingest_documents(all_documents)
```

3. **Update all components to cloud**:
```python
config = RAGConfig(
    embedding_provider="vertex_ai",
    vector_store_type="matching_engine",
    query_expander="vertex_ai"
)
```

4. **Deploy to production**

### Week 7-8: Optimization

1. **Monitor performance**: Track latency, cost, accuracy
2. **Optimize batch sizes**: Find optimal batch size for API calls
3. **Implement caching**: Cache frequent queries
4. **Fine-tune configuration**: Adjust k, chunk size, etc.

## Testing and Validation

### Validation Checklist

- [ ] Embeddings have correct dimensionality
- [ ] Vector search returns relevant results
- [ ] Query expansion improves retrieval quality
- [ ] Latency meets requirements
- [ ] Cost within budget
- [ ] Error handling works correctly
- [ ] Monitoring and logging in place

### Test Scenarios

1. **Functional Tests**:
```python
def test_cloud_embedding_generation():
    gen = VertexAIEmbeddingGenerator()
    emb = gen.encode("test text")
    assert emb.shape == (1, 768)

def test_matching_engine_search():
    store = MatchingEngineVectorStore(...)
    results = store.search(query_embedding, k=3)
    assert len(results) <= 3
```

2. **Performance Tests**:
```python
def test_latency():
    start = time.time()
    result = orchestrator.retrieve("test query", "enhanced", k=3)
    latency = (time.time() - start) * 1000
    assert latency < 1000  # < 1 second
```

3. **Accuracy Tests**:
```python
def test_retrieval_quality():
    # Compare local vs. cloud retrieval
    local_results = local_orchestrator.retrieve(query, "raw", k=3)
    cloud_results = cloud_orchestrator.retrieve(query, "raw", k=3)
    
    # Cloud should have equal or better scores
    assert np.mean(cloud_results.scores) >= np.mean(local_results.scores)
```

## Rollback Strategy

### Rollback Triggers

- Latency exceeds 2x local performance
- Cost exceeds budget by 50%
- Accuracy degrades by >10%
- Critical bugs in production

### Rollback Steps

1. **Switch configuration**:
```python
# Revert to local configuration
config = RAGConfig(
    embedding_provider="local",
    vector_store_type="faiss",
    query_expander="mock"
)
```

2. **Restore local data**: Load FAISS index from backup

3. **Redeploy local version**: Deploy previous working version

4. **Monitor**: Verify system returns to normal operation

### Backup Strategy

- Keep local FAISS indices for 30 days after migration
- Maintain local codebase in separate branch
- Document rollback procedures
- Test rollback process before migration

## Troubleshooting

### Common Issues

#### Issue: High Latency

**Symptoms**: Queries take >2 seconds

**Solutions**:
- Check network connectivity to GCP
- Verify region selection (use closest region)
- Implement caching for frequent queries
- Use batch API calls

#### Issue: High Costs

**Symptoms**: Monthly bill exceeds budget

**Solutions**:
- Reduce Matching Engine node count during off-peak
- Implement query caching
- Use committed use discounts
- Optimize batch sizes

#### Issue: Authentication Errors

**Symptoms**: "Permission denied" errors

**Solutions**:
```bash
# Verify authentication
gcloud auth application-default login

# Check service account permissions
gcloud projects get-iam-policy your-project-id
```

#### Issue: Dimension Mismatch

**Symptoms**: "Dimension mismatch" errors

**Solutions**:
- Verify embedding model dimension (768 for gecko)
- Re-create Matching Engine index with correct dimension
- Re-ingest all documents

## Next Steps

After successful migration:

1. **Monitor and optimize**: Track metrics, optimize costs
2. **Implement advanced features**: Hybrid search, reranking
3. **Scale infrastructure**: Add more nodes as needed
4. **Continuous improvement**: Fine-tune models, update strategies

## Resources

- [Vertex AI Documentation](https://cloud.google.com/vertex-ai/docs)
- [Matching Engine Guide](https://cloud.google.com/vertex-ai/docs/matching-engine/overview)
- [Text Embedding API](https://cloud.google.com/vertex-ai/docs/generative-ai/embeddings/get-text-embeddings)
- [Gemini API](https://cloud.google.com/vertex-ai/docs/generative-ai/model-reference/gemini)
- [GCP Pricing Calculator](https://cloud.google.com/products/calculator)
