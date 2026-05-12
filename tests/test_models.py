"""Unit tests for the data models module.

Tests all data model dataclasses including SearchResult, RetrievalResult,
BenchmarkMetrics, and IngestionStats.
"""

import pytest
from src.models import SearchResult, RetrievalResult, BenchmarkMetrics, IngestionStats


class TestSearchResult:
    """Test SearchResult dataclass."""
    
    def test_search_result_creation(self):
        """Test creating a SearchResult with all fields."""
        result = SearchResult(
            text="Sample text",
            score=0.85,
            metadata={"source": "doc1", "chunk_index": 0}
        )
        
        assert result.text == "Sample text"
        assert result.score == 0.85
        assert result.metadata == {"source": "doc1", "chunk_index": 0}
    
    def test_search_result_without_metadata(self):
        """Test creating a SearchResult without metadata."""
        result = SearchResult(
            text="Sample text",
            score=0.85
        )
        
        assert result.text == "Sample text"
        assert result.score == 0.85
        assert result.metadata is None
    
    def test_search_result_with_none_metadata(self):
        """Test creating a SearchResult with explicit None metadata."""
        result = SearchResult(
            text="Sample text",
            score=0.85,
            metadata=None
        )
        
        assert result.metadata is None
    
    def test_search_result_score_types(self):
        """Test SearchResult with different score types."""
        # Float score
        result1 = SearchResult(text="text", score=0.85)
        assert isinstance(result1.score, float)
        
        # Integer score (should work)
        result2 = SearchResult(text="text", score=1)
        assert result2.score == 1
    
    def test_search_result_empty_metadata(self):
        """Test SearchResult with empty metadata dictionary."""
        result = SearchResult(
            text="Sample text",
            score=0.85,
            metadata={}
        )
        
        assert result.metadata == {}


class TestRetrievalResult:
    """Test RetrievalResult dataclass."""
    
    def test_retrieval_result_creation(self):
        """Test creating a RetrievalResult with all fields."""
        result = RetrievalResult(
            query="How does the system work?",
            expanded_query="How does the system work? operate function",
            chunks=["Chunk 1", "Chunk 2", "Chunk 3"],
            scores=[0.9, 0.85, 0.8],
            latency_ms=45.3,
            strategy_name="AIEnhancedRetrieval"
        )
        
        assert result.query == "How does the system work?"
        assert result.expanded_query == "How does the system work? operate function"
        assert result.chunks == ["Chunk 1", "Chunk 2", "Chunk 3"]
        assert result.scores == [0.9, 0.85, 0.8]
        assert result.latency_ms == 45.3
        assert result.strategy_name == "AIEnhancedRetrieval"
    
    def test_retrieval_result_without_expansion(self):
        """Test creating a RetrievalResult without query expansion (raw search)."""
        result = RetrievalResult(
            query="How does the system work?",
            expanded_query=None,
            chunks=["Chunk 1", "Chunk 2"],
            scores=[0.9, 0.85],
            latency_ms=30.5,
            strategy_name="RawVectorSearch"
        )
        
        assert result.query == "How does the system work?"
        assert result.expanded_query is None
        assert result.strategy_name == "RawVectorSearch"
    
    def test_retrieval_result_empty_results(self):
        """Test creating a RetrievalResult with no results."""
        result = RetrievalResult(
            query="Query with no results",
            expanded_query=None,
            chunks=[],
            scores=[],
            latency_ms=25.0,
            strategy_name="RawVectorSearch"
        )
        
        assert result.chunks == []
        assert result.scores == []
        assert len(result.chunks) == 0
        assert len(result.scores) == 0
    
    def test_retrieval_result_chunks_scores_correspondence(self):
        """Test that chunks and scores have matching lengths."""
        result = RetrievalResult(
            query="Test query",
            expanded_query=None,
            chunks=["A", "B", "C"],
            scores=[0.9, 0.8, 0.7],
            latency_ms=20.0,
            strategy_name="RawVectorSearch"
        )
        
        assert len(result.chunks) == len(result.scores)
        assert len(result.chunks) == 3


class TestBenchmarkMetrics:
    """Test BenchmarkMetrics dataclass."""
    
    def test_benchmark_metrics_creation(self):
        """Test creating BenchmarkMetrics with all fields."""
        query_results = [
            RetrievalResult(
                query="Query 1",
                expanded_query=None,
                chunks=["A", "B"],
                scores=[0.9, 0.8],
                latency_ms=30.0,
                strategy_name="RawVectorSearch"
            ),
            RetrievalResult(
                query="Query 2",
                expanded_query=None,
                chunks=["C", "D"],
                scores=[0.85, 0.75],
                latency_ms=35.0,
                strategy_name="RawVectorSearch"
            )
        ]
        
        metrics = BenchmarkMetrics(
            strategy_name="RawVectorSearch",
            avg_similarity_score=0.825,
            unique_chunks_retrieved=4,
            avg_latency_ms=32.5,
            query_results=query_results
        )
        
        assert metrics.strategy_name == "RawVectorSearch"
        assert metrics.avg_similarity_score == 0.825
        assert metrics.unique_chunks_retrieved == 4
        assert metrics.avg_latency_ms == 32.5
        assert len(metrics.query_results) == 2
    
    def test_benchmark_metrics_empty_results(self):
        """Test creating BenchmarkMetrics with empty query results."""
        metrics = BenchmarkMetrics(
            strategy_name="TestStrategy",
            avg_similarity_score=0.0,
            unique_chunks_retrieved=0,
            avg_latency_ms=0.0,
            query_results=[]
        )
        
        assert metrics.query_results == []
        assert len(metrics.query_results) == 0
    
    def test_benchmark_metrics_single_query(self):
        """Test BenchmarkMetrics with a single query result."""
        query_result = RetrievalResult(
            query="Single query",
            expanded_query=None,
            chunks=["A"],
            scores=[0.9],
            latency_ms=25.0,
            strategy_name="RawVectorSearch"
        )
        
        metrics = BenchmarkMetrics(
            strategy_name="RawVectorSearch",
            avg_similarity_score=0.9,
            unique_chunks_retrieved=1,
            avg_latency_ms=25.0,
            query_results=[query_result]
        )
        
        assert len(metrics.query_results) == 1
        assert metrics.avg_similarity_score == 0.9


class TestIngestionStats:
    """Test IngestionStats dataclass."""
    
    def test_ingestion_stats_creation(self):
        """Test creating IngestionStats with all fields."""
        stats = IngestionStats(
            total_chunks=47,
            embedding_dimension=384,
            total_tokens=5823,
            ingestion_time_ms=1234.5
        )
        
        assert stats.total_chunks == 47
        assert stats.embedding_dimension == 384
        assert stats.total_tokens == 5823
        assert stats.ingestion_time_ms == 1234.5
    
    def test_ingestion_stats_zero_values(self):
        """Test creating IngestionStats with zero values."""
        stats = IngestionStats(
            total_chunks=0,
            embedding_dimension=0,
            total_tokens=0,
            ingestion_time_ms=0.0
        )
        
        assert stats.total_chunks == 0
        assert stats.embedding_dimension == 0
        assert stats.total_tokens == 0
        assert stats.ingestion_time_ms == 0.0
    
    def test_ingestion_stats_large_values(self):
        """Test IngestionStats with large values."""
        stats = IngestionStats(
            total_chunks=10000,
            embedding_dimension=1536,
            total_tokens=1000000,
            ingestion_time_ms=60000.0
        )
        
        assert stats.total_chunks == 10000
        assert stats.embedding_dimension == 1536
        assert stats.total_tokens == 1000000
        assert stats.ingestion_time_ms == 60000.0
    
    def test_ingestion_stats_typical_values(self):
        """Test IngestionStats with typical values for all-MiniLM-L6-v2."""
        stats = IngestionStats(
            total_chunks=25,
            embedding_dimension=384,  # all-MiniLM-L6-v2 dimension
            total_tokens=3000,
            ingestion_time_ms=500.0
        )
        
        assert stats.embedding_dimension == 384


class TestDataModelInteroperability:
    """Test that data models work together correctly."""
    
    def test_search_result_in_retrieval_result(self):
        """Test that SearchResult data can be used to create RetrievalResult."""
        # Simulate converting SearchResults to RetrievalResult
        search_results = [
            SearchResult(text="Chunk 1", score=0.9, metadata={"idx": 0}),
            SearchResult(text="Chunk 2", score=0.85, metadata={"idx": 1}),
            SearchResult(text="Chunk 3", score=0.8, metadata={"idx": 2})
        ]
        
        retrieval_result = RetrievalResult(
            query="Test query",
            expanded_query=None,
            chunks=[r.text for r in search_results],
            scores=[r.score for r in search_results],
            latency_ms=30.0,
            strategy_name="RawVectorSearch"
        )
        
        assert len(retrieval_result.chunks) == 3
        assert retrieval_result.chunks[0] == "Chunk 1"
        assert retrieval_result.scores[0] == 0.9
    
    def test_retrieval_results_in_benchmark_metrics(self):
        """Test that RetrievalResults can be aggregated into BenchmarkMetrics."""
        results = [
            RetrievalResult(
                query=f"Query {i}",
                expanded_query=None,
                chunks=[f"Chunk {i}"],
                scores=[0.9 - i * 0.1],
                latency_ms=30.0 + i * 5,
                strategy_name="RawVectorSearch"
            )
            for i in range(3)
        ]
        
        # Calculate metrics
        all_scores = [score for result in results for score in result.scores]
        avg_score = sum(all_scores) / len(all_scores)
        
        unique_chunks = set()
        for result in results:
            unique_chunks.update(result.chunks)
        
        avg_latency = sum(r.latency_ms for r in results) / len(results)
        
        metrics = BenchmarkMetrics(
            strategy_name="RawVectorSearch",
            avg_similarity_score=avg_score,
            unique_chunks_retrieved=len(unique_chunks),
            avg_latency_ms=avg_latency,
            query_results=results
        )
        
        assert len(metrics.query_results) == 3
        assert metrics.unique_chunks_retrieved == 3
        assert metrics.avg_latency_ms == 35.0  # (30 + 35 + 40) / 3


class TestDataModelImports:
    """Test that models can be imported from src.models."""
    
    def test_import_search_result(self):
        """Test importing SearchResult from src.models."""
        from src.models import SearchResult as SR
        result = SR(text="test", score=0.5)
        assert result.text == "test"
    
    def test_import_retrieval_result(self):
        """Test importing RetrievalResult from src.models."""
        from src.models import RetrievalResult as RR
        result = RR(
            query="test",
            expanded_query=None,
            chunks=[],
            scores=[],
            latency_ms=0.0,
            strategy_name="test"
        )
        assert result.query == "test"
    
    def test_import_benchmark_metrics(self):
        """Test importing BenchmarkMetrics from src.models."""
        from src.models import BenchmarkMetrics as BM
        metrics = BM(
            strategy_name="test",
            avg_similarity_score=0.0,
            unique_chunks_retrieved=0,
            avg_latency_ms=0.0,
            query_results=[]
        )
        assert metrics.strategy_name == "test"
    
    def test_import_ingestion_stats(self):
        """Test importing IngestionStats from src.models."""
        from src.models import IngestionStats as IS
        stats = IS(
            total_chunks=0,
            embedding_dimension=0,
            total_tokens=0,
            ingestion_time_ms=0.0
        )
        assert stats.total_chunks == 0
