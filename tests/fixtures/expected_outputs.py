"""
Expected output formats and validation schemas for testing.
"""

from typing import Dict, Any

VALID_SEARCH_RESULT_EXAMPLE = {
    "text": "Microservices architecture is a design pattern...",
    "score": 0.85,
    "metadata": {"source": "doc_1", "chunk_id": 0}
}

VALID_RETRIEVAL_RESULT_EXAMPLE = {
    "query": "What is microservices architecture?",
    "expanded_query": "What is microservices architecture? Explain distributed services design patterns.",
    "chunks": [
        "Microservices architecture is a design pattern...",
        "Event-driven architecture promotes loose coupling...",
        "API Gateway acts as an entry point..."
    ],
    "scores": [0.92, 0.78, 0.65],
    "latency_ms": 145.3,
    "strategy_name": "AIEnhancedRetrieval"
}

VALID_BENCHMARK_METRICS_EXAMPLE = {
    "strategy_name": "RawVectorSearch",
    "avg_similarity_score": 0.78,
    "unique_chunks_retrieved": 15,
    "avg_latency_ms": 123.4,
    "query_results": [VALID_RETRIEVAL_RESULT_EXAMPLE]
}

VALID_INGESTION_STATS_EXAMPLE = {
    "total_chunks": 10,
    "embedding_dimension": 384,
    "total_tokens": 2500,
    "ingestion_time_ms": 1234.5
}

def validate_search_result(result: Dict[str, Any]) -> bool:
    """Validate search result format."""
    required_fields = ["text", "score"]
    return all(field in result for field in required_fields)

def validate_retrieval_result(result: Dict[str, Any]) -> bool:
    """Validate retrieval result format."""
    required_fields = ["query", "chunks", "scores", "latency_ms", "strategy_name"]
    
    if not all(field in result for field in required_fields):
        return False
    
    if not isinstance(result["chunks"], list) or not isinstance(result["scores"], list):
        return False
    
    if len(result["chunks"]) != len(result["scores"]):
        return False
    
    if not all(0 <= score <= 1 for score in result["scores"]):
        return False
    
    if result["latency_ms"] < 0:
        return False
    
    return True

def validate_benchmark_metrics(metrics: Dict[str, Any]) -> bool:
    """Validate benchmark metrics format."""
    required_fields = [
        "strategy_name",
        "avg_similarity_score",
        "unique_chunks_retrieved",
        "avg_latency_ms",
        "query_results"
    ]
    
    if not all(field in metrics for field in required_fields):
        return False
    
    if not (0 <= metrics["avg_similarity_score"] <= 1):
        return False
    
    if metrics["unique_chunks_retrieved"] < 0:
        return False
    
    if metrics["avg_latency_ms"] < 0:
        return False
    
    return True

def validate_ingestion_stats(stats: Dict[str, Any]) -> bool:
    """Validate ingestion stats format."""
    required_fields = [
        "total_chunks",
        "embedding_dimension",
        "total_tokens",
        "ingestion_time_ms"
    ]
    
    if not all(field in stats for field in required_fields):
        return False
    
    if stats["total_chunks"] <= 0:
        return False
    
    if stats["embedding_dimension"] <= 0:
        return False
    
    if stats["ingestion_time_ms"] < 0:
        return False
    
    return True
