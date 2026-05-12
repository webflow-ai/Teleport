"""Benchmark Engine Module for Context-Aware Retrieval Engine.

This module provides benchmarking capabilities to compare retrieval strategies
across query sets, measuring quality metrics like similarity scores, diversity,
overlap, and latency.
"""

from dataclasses import dataclass
from typing import List, Dict, Optional
import time

from src.orchestrator import RAGOrchestrator
from src.retrieval import RetrievalResult


@dataclass
class BenchmarkMetrics:
    """Aggregated benchmark results for a retrieval strategy.
    
    Attributes:
        strategy_name: Name of the retrieval strategy
        avg_similarity_score: Average similarity score across all queries
        unique_chunks_retrieved: Number of unique chunks retrieved across all queries
        avg_latency_ms: Average retrieval latency in milliseconds
        query_results: List of individual RetrievalResult objects for each query
    """
    strategy_name: str
    avg_similarity_score: float
    unique_chunks_retrieved: int
    avg_latency_ms: float
    query_results: List[RetrievalResult]


class BenchmarkEngine:
    """Compares retrieval strategies across query sets.
    
    The BenchmarkEngine executes predefined query sets against multiple
    retrieval strategies, collects performance metrics, and generates
    structured comparison reports.
    """
    
    def __init__(self, orchestrator: RAGOrchestrator):
        """Initialize BenchmarkEngine with required dependencies.
        
        Args:
            orchestrator: RAGOrchestrator instance with configured strategies
        
        Raises:
            ValueError: If orchestrator has no configured strategies
        """
        if not orchestrator.strategies:
            raise ValueError("Orchestrator must have at least one configured strategy.")
        
        self.orchestrator = orchestrator
    
    def run_benchmark(self, queries: List[str], output_path: str = "retrieval_benchmark.md") -> Dict:
        """Execute benchmark suite across all configured strategies.
        
        This method:
        1. Executes each query against all available strategies
        2. Collects retrieval results, similarity scores, and latency
        3. Calculates quality metrics for each strategy
        4. Generates and saves a structured comparison report
        
        Args:
            queries: List of query strings to benchmark
            output_path: Path where benchmark report should be saved (default: "retrieval_benchmark.md")
        
        Returns:
            Dictionary mapping strategy names to BenchmarkMetrics objects
        
        Raises:
            ValueError: If queries list is empty
            IOError: If unable to write report to output_path
        """
        # Validate inputs
        if not queries or len(queries) == 0:
            raise ValueError("Queries list cannot be empty.")
        
        # Dictionary to store results for each strategy
        # Format: {strategy_name: [RetrievalResult1, RetrievalResult2, ...]}
        strategy_results: Dict[str, List[RetrievalResult]] = {
            strategy_name: [] for strategy_name in self.orchestrator.strategies.keys()
        }
        
        # Execute each query against all strategies
        for query in queries:
            for strategy_name in self.orchestrator.strategies.keys():
                try:
                    # Execute retrieval
                    result = self.orchestrator.retrieve(query, strategy_name, k=3)
                    strategy_results[strategy_name].append(result)
                except Exception as e:
                    # Handle strategy execution failures gracefully
                    import warnings
                    warnings.warn(
                        f"Strategy '{strategy_name}' failed for query '{query}': {e}",
                        UserWarning
                    )
                    # Create empty result to maintain consistency
                    from src.retrieval import RetrievalResult
                    empty_result = RetrievalResult(
                        query=query,
                        expanded_query=None,
                        chunks=[],
                        scores=[],
                        latency_ms=0.0,
                        strategy_name=strategy_name
                    )
                    strategy_results[strategy_name].append(empty_result)
        
        # Calculate metrics for each strategy
        metrics_by_strategy: Dict[str, BenchmarkMetrics] = {}
        for strategy_name, results in strategy_results.items():
            metrics = self.calculate_metrics(strategy_name, results)
            metrics_by_strategy[strategy_name] = metrics
        
        # Generate and save report
        self._generate_report(metrics_by_strategy, queries, output_path)
        
        return metrics_by_strategy
    
    def calculate_metrics(self, strategy_name: str, results: List[RetrievalResult]) -> BenchmarkMetrics:
        """Calculate aggregated metrics for a strategy's results.
        
        This method calculates:
        - Average similarity score across all retrieved chunks
        - Number of unique chunks retrieved
        - Average retrieval latency
        
        Args:
            strategy_name: Name of the strategy being evaluated
            results: List of RetrievalResult objects from benchmark execution
        
        Returns:
            BenchmarkMetrics object with calculated metrics
        
        Raises:
            ValueError: If results list is empty
        """
        if not results or len(results) == 0:
            raise ValueError("Results list cannot be empty.")
        
        # Calculate average similarity score
        all_scores = []
        for result in results:
            all_scores.extend(result.scores)
        
        if len(all_scores) > 0:
            avg_similarity_score = sum(all_scores) / len(all_scores)
        else:
            # Handle case where no results were retrieved
            avg_similarity_score = 0.0
        
        # Calculate unique chunks retrieved
        unique_chunks = set()
        for result in results:
            unique_chunks.update(result.chunks)
        unique_chunks_retrieved = len(unique_chunks)
        
        # Calculate average latency
        total_latency = sum(result.latency_ms for result in results)
        avg_latency_ms = total_latency / len(results)
        
        return BenchmarkMetrics(
            strategy_name=strategy_name,
            avg_similarity_score=avg_similarity_score,
            unique_chunks_retrieved=unique_chunks_retrieved,
            avg_latency_ms=avg_latency_ms,
            query_results=results
        )
    
    def _generate_report(self, metrics_by_strategy: Dict[str, BenchmarkMetrics], 
                        queries: List[str], output_path: str) -> None:
        """Generate structured Markdown benchmark report.
        
        The report includes:
        - Summary table comparing all strategies
        - Per-query results with retrieved chunks and scores
        - Aggregated metrics analysis
        
        Args:
            metrics_by_strategy: Dictionary mapping strategy names to BenchmarkMetrics
            queries: List of queries that were benchmarked
            output_path: Path where report should be saved
        
        Raises:
            IOError: If unable to write to output_path
        """
        lines = []
        
        # Header
        lines.append("# Retrieval Benchmark Report")
        lines.append("")
        lines.append(f"**Total Queries**: {len(queries)}")
        lines.append(f"**Strategies Compared**: {', '.join(metrics_by_strategy.keys())}")
        lines.append("")
        
        # Summary table
        lines.append("## Summary Metrics")
        lines.append("")
        lines.append("| Strategy | Avg Similarity Score | Unique Chunks | Avg Latency (ms) |")
        lines.append("|----------|---------------------|---------------|------------------|")
        
        for strategy_name, metrics in metrics_by_strategy.items():
            lines.append(
                f"| {strategy_name} | {metrics.avg_similarity_score:.4f} | "
                f"{metrics.unique_chunks_retrieved} | {metrics.avg_latency_ms:.2f} |"
            )
        
        lines.append("")
        
        # Calculate result overlap (chunks common to all strategies)
        if len(metrics_by_strategy) >= 2:
            lines.append("## Result Overlap Analysis")
            lines.append("")
            
            # Get all chunks from each strategy
            strategy_chunks = {}
            for strategy_name, metrics in metrics_by_strategy.items():
                all_chunks = set()
                for result in metrics.query_results:
                    all_chunks.update(result.chunks)
                strategy_chunks[strategy_name] = all_chunks
            
            # Calculate pairwise overlaps
            strategy_names = list(strategy_chunks.keys())
            for i in range(len(strategy_names)):
                for j in range(i + 1, len(strategy_names)):
                    strategy1 = strategy_names[i]
                    strategy2 = strategy_names[j]
                    
                    chunks1 = strategy_chunks[strategy1]
                    chunks2 = strategy_chunks[strategy2]
                    
                    overlap = chunks1.intersection(chunks2)
                    overlap_count = len(overlap)
                    
                    lines.append(
                        f"**{strategy1} ∩ {strategy2}**: {overlap_count} common chunks"
                    )
            
            lines.append("")
        
        # Per-query results
        lines.append("## Per-Query Results")
        lines.append("")
        
        for query_idx, query in enumerate(queries, 1):
            lines.append(f"### Query {query_idx}: \"{query}\"")
            lines.append("")
            
            for strategy_name, metrics in metrics_by_strategy.items():
                result = metrics.query_results[query_idx - 1]
                
                lines.append(f"#### {strategy_name}")
                lines.append("")
                
                if result.expanded_query and result.expanded_query != result.query:
                    lines.append(f"**Expanded Query**: \"{result.expanded_query}\"")
                    lines.append("")
                
                lines.append(f"**Latency**: {result.latency_ms:.2f} ms")
                lines.append("")
                
                if len(result.chunks) > 0:
                    lines.append("**Retrieved Chunks**:")
                    lines.append("")
                    
                    for chunk_idx, (chunk, score) in enumerate(zip(result.chunks, result.scores), 1):
                        lines.append(f"{chunk_idx}. **Score: {score:.4f}**")
                        lines.append(f"   ```")
                        lines.append(f"   {chunk}")
                        lines.append(f"   ```")
                        lines.append("")
                else:
                    lines.append("*No results retrieved*")
                    lines.append("")
        
        # Write report to file
        report_content = "\n".join(lines)
        
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(report_content)
        except IOError as e:
            raise IOError(f"Failed to write benchmark report to {output_path}: {e}")
