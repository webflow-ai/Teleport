#!/usr/bin/env python
"""
Demonstration of test fixtures usage.

This script shows how to use the test fixtures for integration testing
and benchmarking the Context-Aware Retrieval Engine.
"""

import sys
sys.path.insert(0, '.')

# Load fixtures by executing them directly (workaround for Python 3.13 import issue)
fixtures = {}
exec(open('tests/fixtures/sample_documents.py').read(), fixtures)
exec(open('tests/fixtures/benchmark_queries.py').read(), fixtures)
exec(open('tests/fixtures/expected_outputs.py').read(), fixtures)

# Extract fixture data
SAMPLE_DOCUMENTS = fixtures['SAMPLE_DOCUMENTS']
SIMPLE_DOCUMENTS = fixtures['SIMPLE_DOCUMENTS']
BENCHMARK_QUERIES = fixtures['BENCHMARK_QUERIES']
SIMPLE_QUERIES = fixtures['SIMPLE_QUERIES']
COMPLEX_QUERIES = fixtures['COMPLEX_QUERIES']
validate_search_result = fixtures['validate_search_result']
validate_retrieval_result = fixtures['validate_retrieval_result']
VALID_SEARCH_RESULT_EXAMPLE = fixtures['VALID_SEARCH_RESULT_EXAMPLE']
VALID_RETRIEVAL_RESULT_EXAMPLE = fixtures['VALID_RETRIEVAL_RESULT_EXAMPLE']


def main():
    """Demonstrate fixture usage."""
    print("=" * 70)
    print("Test Fixtures Demonstration")
    print("=" * 70)
    
    # Sample Documents
    print(f"\n1. Sample Documents: {len(SAMPLE_DOCUMENTS)} technical paragraphs")
    print(f"   - First document preview: {SAMPLE_DOCUMENTS[0][:100]}...")
    print(f"   - Simple documents: {len(SIMPLE_DOCUMENTS)} documents")
    
    # Benchmark Queries
    print(f"\n2. Benchmark Queries: {len(BENCHMARK_QUERIES)} complex queries")
    print(f"   - Example query: {BENCHMARK_QUERIES[0]}")
    print(f"   - Simple queries: {len(SIMPLE_QUERIES)} queries")
    print(f"   - Complex queries: {len(COMPLEX_QUERIES)} queries")
    
    # Validators
    print(f"\n3. Output Validators:")
    print(f"   - Search result validation: {validate_search_result(VALID_SEARCH_RESULT_EXAMPLE)}")
    print(f"   - Retrieval result validation: {validate_retrieval_result(VALID_RETRIEVAL_RESULT_EXAMPLE)}")
    
    # Example usage
    print(f"\n4. Example Usage:")
    print(f"   - Documents can be used for ingestion testing")
    print(f"   - Queries can be used for retrieval benchmarking")
    print(f"   - Validators ensure output format correctness")
    
    print("\n" + "=" * 70)
    print("All fixtures loaded and validated successfully!")
    print("=" * 70)


if __name__ == "__main__":
    main()
