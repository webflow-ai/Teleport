"""Tests for the Benchmark Engine module."""

import pytest
import os
import tempfile
from unittest.mock import Mock, MagicMock

from src.benchmark import BenchmarkEngine, BenchmarkMetrics
from src.orchestrator import RAGOrchestrator
from src.retrieval import RetrievalResult


class TestBenchmarkEngine:
    """Test suite for BenchmarkEngine class."""
    
    def test_init_with_valid_orchestrator(self):
        """Test BenchmarkEngine initialization with valid orchestrator."""
        # Create mock orchestrator with strategies
        orchestrator = Mock(spec=RAGOrchestrator)
        orchestrator.strategies = {"raw": Mock(), "enhanced": Mock()}
        
        engine = BenchmarkEngine(orchestrator)
        
        assert engine.orchestrator == orchestrator
    
    def test_init_with_no_strategies_raises_error(self):
        """Test BenchmarkEngine initialization fails with no strategies."""
        # Create mock orchestrator with no strategies
        orchestrator = Mock(spec=RAGOrchestrator)
        orchestrator.strategies = {}
        
        with pytest.raises(ValueError, match="at least one configured strategy"):
            BenchmarkEngine(orchestrator)
    
    def test_calculate_metrics_with_valid_results(self):
        """Test metrics calculation with valid results."""
        # Create mock orchestrator
        orchestrator = Mock(spec=RAGOrchestrator)
        orchestrator.strategies = {"raw": Mock()}
        
        engine = BenchmarkEngine(orchestrator)
        
        # Create sample results
        results = [
            RetrievalResult(
                query="test query 1",
                expanded_query=None,
                chunks=["chunk1", "chunk2"],
                scores=[0.9, 0.8],
                latency_ms=100.0,
                strategy_name="raw"
            ),
            RetrievalResult(
                query="test query 2",
                expanded_query=None,
                chunks=["chunk2", "chunk3"],
                scores=[0.85, 0.75],
                latency_ms=120.0,
                strategy_name="raw"
            )
        ]
        
        metrics = engine.calculate_metrics("raw", results)
        
        assert metrics.strategy_name == "raw"
        assert metrics.avg_similarity_score == pytest.approx((0.9 + 0.8 + 0.85 + 0.75) / 4)
        assert metrics.unique_chunks_retrieved == 3  # chunk1, chunk2, chunk3
        assert metrics.avg_latency_ms == pytest.approx((100.0 + 120.0) / 2)
        assert len(metrics.query_results) == 2
    
    def test_calculate_metrics_with_empty_results_raises_error(self):
        """Test metrics calculation fails with empty results."""
        orchestrator = Mock(spec=RAGOrchestrator)
        orchestrator.strategies = {"raw": Mock()}
        
        engine = BenchmarkEngine(orchestrator)
        
        with pytest.raises(ValueError, match="Results list cannot be empty"):
            engine.calculate_metrics("raw", [])
    
    def test_calculate_metrics_with_no_retrieved_chunks(self):
        """Test metrics calculation handles no retrieved chunks."""
        orchestrator = Mock(spec=RAGOrchestrator)
        orchestrator.strategies = {"raw": Mock()}
        
        engine = BenchmarkEngine(orchestrator)
        
        # Create results with no chunks
        results = [
            RetrievalResult(
                query="test query",
                expanded_query=None,
                chunks=[],
                scores=[],
                latency_ms=50.0,
                strategy_name="raw"
            )
        ]
        
        metrics = engine.calculate_metrics("raw", results)
        
        assert metrics.avg_similarity_score == 0.0
        assert metrics.unique_chunks_retrieved == 0
        assert metrics.avg_latency_ms == 50.0
    
    def test_run_benchmark_with_valid_queries(self):
        """Test benchmark execution with valid queries."""
        # Create mock orchestrator
        orchestrator = Mock(spec=RAGOrchestrator)
        orchestrator.strategies = {"raw": Mock(), "enhanced": Mock()}
        
        # Mock retrieve method
        def mock_retrieve(query, strategy_name, k):
            return RetrievalResult(
                query=query,
                expanded_query=f"expanded {query}" if strategy_name == "enhanced" else None,
                chunks=[f"chunk1 for {query}", f"chunk2 for {query}"],
                scores=[0.9, 0.8],
                latency_ms=100.0,
                strategy_name=strategy_name
            )
        
        orchestrator.retrieve = Mock(side_effect=mock_retrieve)
        
        engine = BenchmarkEngine(orchestrator)
        
        # Run benchmark with temporary output file
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, "test_benchmark.md")
            
            metrics = engine.run_benchmark(
                queries=["query1", "query2"],
                output_path=output_path
            )
            
            # Verify metrics were calculated for both strategies
            assert "raw" in metrics
            assert "enhanced" in metrics
            
            # Verify report was created
            assert os.path.exists(output_path)
            
            # Verify report content
            with open(output_path, 'r', encoding='utf-8') as f:
                content = f.read()
                assert "Retrieval Benchmark Report" in content
                assert "query1" in content
                assert "query2" in content
                assert "raw" in content
                assert "enhanced" in content
    
    def test_run_benchmark_with_empty_queries_raises_error(self):
        """Test benchmark execution fails with empty queries."""
        orchestrator = Mock(spec=RAGOrchestrator)
        orchestrator.strategies = {"raw": Mock()}
        
        engine = BenchmarkEngine(orchestrator)
        
        with pytest.raises(ValueError, match="Queries list cannot be empty"):
            engine.run_benchmark(queries=[])
    
    def test_run_benchmark_handles_strategy_failures(self):
        """Test benchmark gracefully handles strategy execution failures."""
        orchestrator = Mock(spec=RAGOrchestrator)
        orchestrator.strategies = {"raw": Mock(), "enhanced": Mock()}
        
        # Mock retrieve to fail for enhanced strategy
        def mock_retrieve(query, strategy_name, k):
            if strategy_name == "enhanced":
                raise Exception("Strategy failed")
            return RetrievalResult(
                query=query,
                expanded_query=None,
                chunks=["chunk1"],
                scores=[0.9],
                latency_ms=100.0,
                strategy_name=strategy_name
            )
        
        orchestrator.retrieve = Mock(side_effect=mock_retrieve)
        
        engine = BenchmarkEngine(orchestrator)
        
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, "test_benchmark.md")
            
            # Should not raise exception
            with pytest.warns(UserWarning, match="Strategy 'enhanced' failed"):
                metrics = engine.run_benchmark(
                    queries=["query1"],
                    output_path=output_path
                )
            
            # Verify both strategies have metrics (enhanced with empty results)
            assert "raw" in metrics
            assert "enhanced" in metrics
            assert len(metrics["enhanced"].query_results[0].chunks) == 0
    
    def test_generate_report_includes_overlap_analysis(self):
        """Test report generation includes overlap analysis for multiple strategies."""
        orchestrator = Mock(spec=RAGOrchestrator)
        orchestrator.strategies = {"raw": Mock(), "enhanced": Mock()}
        
        # Mock retrieve with overlapping chunks
        def mock_retrieve(query, strategy_name, k):
            if strategy_name == "raw":
                chunks = ["common_chunk", "raw_only_chunk"]
            else:
                chunks = ["common_chunk", "enhanced_only_chunk"]
            
            return RetrievalResult(
                query=query,
                expanded_query=None,
                chunks=chunks,
                scores=[0.9, 0.8],
                latency_ms=100.0,
                strategy_name=strategy_name
            )
        
        orchestrator.retrieve = Mock(side_effect=mock_retrieve)
        
        engine = BenchmarkEngine(orchestrator)
        
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, "test_benchmark.md")
            
            engine.run_benchmark(
                queries=["query1"],
                output_path=output_path
            )
            
            # Verify overlap analysis in report
            with open(output_path, 'r', encoding='utf-8') as f:
                content = f.read()
                assert "Result Overlap Analysis" in content
                assert "common chunks" in content
    
    def test_generate_report_includes_expanded_queries(self):
        """Test report includes expanded queries for AI-enhanced retrieval."""
        orchestrator = Mock(spec=RAGOrchestrator)
        orchestrator.strategies = {"enhanced": Mock()}
        
        # Mock retrieve with expanded query
        orchestrator.retrieve = Mock(return_value=RetrievalResult(
            query="original query",
            expanded_query="expanded original query with synonyms",
            chunks=["chunk1"],
            scores=[0.9],
            latency_ms=100.0,
            strategy_name="enhanced"
        ))
        
        engine = BenchmarkEngine(orchestrator)
        
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, "test_benchmark.md")
            
            engine.run_benchmark(
                queries=["original query"],
                output_path=output_path
            )
            
            # Verify expanded query in report
            with open(output_path, 'r', encoding='utf-8') as f:
                content = f.read()
                assert "Expanded Query" in content
                assert "expanded original query with synonyms" in content
