"""Demonstration of QueryExpander functionality."""

from src.mocks import QueryExpander


def demo_synonym_addition():
    """Demonstrate synonym addition strategy."""
    print("=" * 60)
    print("SYNONYM ADDITION STRATEGY")
    print("=" * 60)
    
    expander = QueryExpander(expansion_strategy="synonym_addition")
    
    queries = [
        "How to fix database error",
        "System performance issues",
        "User authentication problems"
    ]
    
    for query in queries:
        expanded = expander.expand_query(query)
        print(f"\nOriginal:  {query}")
        print(f"Expanded:  {expanded}")


def demo_clarification():
    """Demonstrate clarification strategy."""
    print("\n" + "=" * 60)
    print("CLARIFICATION STRATEGY")
    print("=" * 60)
    
    expander = QueryExpander(expansion_strategy="clarification")
    
    queries = [
        "How does the system handle peak load",
        "What is the cache mechanism",
        "Why does the API fail"
    ]
    
    for query in queries:
        expanded = expander.expand_query(query)
        print(f"\nOriginal:  {query}")
        print(f"Expanded:  {expanded}")


def demo_decomposition():
    """Demonstrate decomposition strategy."""
    print("\n" + "=" * 60)
    print("DECOMPOSITION STRATEGY")
    print("=" * 60)
    
    expander = QueryExpander(expansion_strategy="decomposition")
    
    queries = [
        "authentication and authorization",
        "cache or database",
        "microservices architecture"
    ]
    
    for query in queries:
        expanded = expander.expand_query(query)
        print(f"\nOriginal:  {query}")
        print(f"Expanded:  {expanded}")


def demo_interaction_logging():
    """Demonstrate interaction logging."""
    print("\n" + "=" * 60)
    print("INTERACTION LOGGING")
    print("=" * 60)
    
    expander = QueryExpander()
    
    # Perform some expansions
    expander.expand_query("How to fix errors")
    expander.expand_query("Database performance")
    expander.expand_query("API security")
    
    # Retrieve and display logs
    logs = expander.get_interaction_log()
    
    print(f"\nTotal interactions logged: {len(logs)}")
    print("\nLog entries:")
    for i, log in enumerate(logs, 1):
        print(f"\n{i}. Timestamp: {log['timestamp']}")
        print(f"   Strategy: {log['strategy']}")
        print(f"   Original: {log['original_query']}")
        print(f"   Expanded: {log['expanded_query']}")
        print(f"   Changed: {log['expansion_occurred']}")


if __name__ == "__main__":
    demo_synonym_addition()
    demo_clarification()
    demo_decomposition()
    demo_interaction_logging()
    
    print("\n" + "=" * 60)
    print("DEMO COMPLETE")
    print("=" * 60)
