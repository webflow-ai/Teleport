"""
Benchmark queries for testing retrieval strategies.
"""

BENCHMARK_QUERIES = [
    "How does the system handle distributed transactions across multiple services?",
    "What are the benefits of separating read and write operations in application architecture?",
    "Explain the role of API Gateway in managing client requests and cross-cutting concerns.",
    "How do microservices communicate asynchronously using events?",
    "What patterns help prevent cascading failures in distributed systems?",
    "How does serverless architecture differ from traditional server-based deployment?",
    "What is the purpose of the Repository pattern in data access?",
]

SIMPLE_QUERIES = [
    "What is microservices architecture?",
    "Explain event-driven architecture",
    "What is CQRS?",
    "Define API Gateway",
    "What is serverless?"
]

COMPLEX_QUERIES = [
    "How does the system handle peak load while maintaining data consistency across distributed services?",
    "What are the tradeoffs between using choreography versus orchestration in saga patterns?",
    "How can hexagonal architecture improve testability and enable technology-agnostic business logic?",
    "What strategies combine event sourcing with CQRS to optimize read and write workloads independently?",
]

def get_queries(category="benchmark"):
    """Get queries by category."""
    if category == "simple":
        return SIMPLE_QUERIES
    elif category == "complex":
        return COMPLEX_QUERIES
    return BENCHMARK_QUERIES

def validate_query(query):
    """Validate query meets minimum requirements."""
    if not query or not isinstance(query, str):
        return False
    query = query.strip()
    word_count = len(query.split())
    return len(query) >= 10 and len(query) <= 500 and word_count >= 3
