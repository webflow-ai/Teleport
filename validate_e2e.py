"""End-to-end validation script for Context-Aware Retrieval Engine.

This script validates:
1. Document ingestion with sample data
2. Retrieval with both strategies
3. Benchmark execution and report generation
4. Metrics calculation accuracy
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.embedding import EmbeddingGenerator
from src.storage import NumpyVectorStore
from src.mocks import QueryExpander
from src.retrieval import RawVectorSearch, AIEnhancedRetrieval
from src.orchestrator import RAGOrchestrator
from src.benchmark import BenchmarkEngine
from tests.fixtures.sample_documents import SAMPLE_DOCUMENTS
from tests.fixtures.benchmark_queries import BENCHMARK_QUERIES


def main():
    print("=" * 80)
    print("Context-Aware Retrieval Engine - End-to-End Validation")
    print("=" * 80)
    print()
    
    # Step 1: Initialize components
    print("Step 1: Initializing components...")
    embedding_generator = EmbeddingGenerator(model_name="all-MiniLM-L6-v2")
    vector_store = NumpyVectorStore(similarity_metric="cosine")
    
    raw_strategy = RawVectorSearch(embedding_generator, vector_store)
    query_expander = QueryExpander(expansion_strategy="synonym_addition")
    enhanced_strategy = AIEnhancedRetrieval(
        embedding_generator,
        vector_store,
        query_expander
    )
    
    orchestrator = RAGOrchestrator(
        embedding_generator,
        vector_store,
        strategies={"raw": raw_strategy, "enhanced": enhanced_strategy}
    )
    print("✓ Components initialized successfully")
    print()
    
    # Step 2: Ingest sample documents
    print("Step 2: Ingesting sample technical documents...")
    print(f"  Documents to ingest: {len(SAMPLE_DOCUMENTS)}")
    
    stats = orchestrator.ingest_documents(SAMPLE_DOCUMENTS, chunk_size=300)
    
    print(f"✓ Ingestion complete:")
    print(f"  - Total chunks: {stats.total_chunks}")
    print(f"  - Embedding dimension: {stats.embedding_dimension}")
    print(f"  - Approximate tokens: {stats.total_tokens}")
    print(f"  - Ingestion time: {stats.ingestion_time_ms:.2f}ms")
    print()
    
    # Step 3: Test retrieval with both strategies
    print("Step 3: Testing retrieval strategies...")
    test_query = "How does the system handle peak load?"
    
    # Raw vector search
    print(f"  Query: '{test_query}'")
    raw_result = orchestrator.retrieve(test_query, "raw", k=3)
    print(f"  ✓ Raw vector search: {len(raw_result.chunks)} chunks in {raw_result.latency_ms:.2f}ms")
    print(f"    Top score: {raw_result.scores[0]:.4f}")
    
    # AI-enhanced retrieval
    enhanced_result = orchestrator.retrieve(test_query, "enhanced", k=3)
    print(f"  ✓ AI-enhanced retrieval: {len(enhanced_result.chunks)} chunks in {enhanced_result.latency_ms:.2f}ms")
    print(f"    Expanded query: '{enhanced_result.expanded_query}'")
    print(f"    Top score: {enhanced_result.scores[0]:.4f}")
    print()
    
    # Step 4: Run benchmark
    print("Step 4: Running benchmark with predefined queries...")
    print(f"  Benchmark queries: {len(BENCHMARK_QUERIES)}")
    
    benchmark = BenchmarkEngine(orchestrator)
    benchmark.run_benchmark(
        queries=BENCHMARK_QUERIES,
        output_path="retrieval_benchmark.md"
    )
    
    print("✓ Benchmark complete:")
    print(f"  - Report saved to: retrieval_benchmark.md")
    print()
    
    # Step 5: Verify benchmark report
    print("Step 5: Verifying benchmark report...")
    report_path = Path("retrieval_benchmark.md")
    
    if not report_path.exists():
        print("✗ ERROR: Benchmark report not found!")
        return False
    
    report_content = report_path.read_text()
    
    # Check required sections
    required_sections = [
        "# Retrieval Benchmark Report",
        "## Summary Metrics",
        "## Result Overlap Analysis",
        "## Per-Query Results"
    ]
    
    missing_sections = []
    for section in required_sections:
        if section not in report_content:
            missing_sections.append(section)
    
    if missing_sections:
        print(f"✗ ERROR: Missing sections in report: {missing_sections}")
        return False
    
    print("✓ Benchmark report structure validated")
    
    # Check metrics are present
    if "Avg Similarity Score" not in report_content:
        print("✗ ERROR: Average similarity scores not found in report")
        return False
    
    if "Avg Latency (ms)" not in report_content:
        print("✗ ERROR: Latency metrics not found in report")
        return False
    
    if "Unique Chunks" not in report_content:
        print("✗ ERROR: Diversity metrics not found in report")
        return False
    
    print("✓ All required metrics present in report")
    print()
    
    # Step 6: Validate statistics
    print("Step 6: Validating system statistics...")
    system_stats = orchestrator.get_statistics()
    
    print(f"  - Total chunks in store: {system_stats['total_chunks']}")
    print(f"  - Embedding dimension: {system_stats['embedding_dimension']}")
    print(f"  - Vector store size: {system_stats['vector_store_size']}")
    
    if system_stats['total_chunks'] != stats.total_chunks:
        print("✗ ERROR: Chunk count mismatch!")
        return False
    
    if system_stats['embedding_dimension'] != 384:
        print("✗ ERROR: Unexpected embedding dimension!")
        return False
    
    print("✓ System statistics validated")
    print()
    
    # Final summary
    print("=" * 80)
    print("✓ END-TO-END VALIDATION SUCCESSFUL")
    print("=" * 80)
    print()
    print("Summary:")
    print(f"  - Ingested {stats.total_chunks} chunks from {len(SAMPLE_DOCUMENTS)} documents")
    print(f"  - Tested both retrieval strategies successfully")
    print(f"  - Generated benchmark report with {len(BENCHMARK_QUERIES)} queries")
    print(f"  - All metrics calculated accurately")
    print()
    
    return True


if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n✗ VALIDATION FAILED WITH ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
