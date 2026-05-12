"""Tests for mock components in the Context-Aware Retrieval Engine."""

import pytest
from src.mocks import QueryExpander


class TestQueryExpander:
    """Test suite for QueryExpander mock component."""
    
    def test_init_with_valid_strategy(self):
        """Test initialization with valid expansion strategies."""
        for strategy in ["synonym_addition", "clarification", "decomposition"]:
            expander = QueryExpander(expansion_strategy=strategy)
            assert expander.expansion_strategy == strategy
            assert expander.interaction_log == []
    
    def test_init_with_default_strategy(self):
        """Test initialization with default strategy."""
        expander = QueryExpander()
        assert expander.expansion_strategy == "synonym_addition"
    
    def test_init_with_invalid_strategy(self):
        """Test initialization with invalid strategy raises ValueError."""
        with pytest.raises(ValueError) as exc_info:
            QueryExpander(expansion_strategy="invalid_strategy")
        assert "Invalid expansion strategy" in str(exc_info.value)
    
    def test_expand_query_with_empty_string(self):
        """Test that empty query raises ValueError."""
        expander = QueryExpander()
        with pytest.raises(ValueError) as exc_info:
            expander.expand_query("")
        assert "empty" in str(exc_info.value).lower()
    
    def test_expand_query_with_whitespace_only(self):
        """Test that whitespace-only query raises ValueError."""
        expander = QueryExpander()
        with pytest.raises(ValueError) as exc_info:
            expander.expand_query("   ")
        assert "empty" in str(exc_info.value).lower()
    
    def test_expand_query_with_none(self):
        """Test that None query raises ValueError."""
        expander = QueryExpander()
        with pytest.raises(ValueError) as exc_info:
            expander.expand_query(None)
        assert "non-empty string" in str(exc_info.value).lower()
    
    def test_expand_query_with_very_long_query(self):
        """Test that very long queries are truncated with warning."""
        expander = QueryExpander()
        long_query = "word " * 200  # Creates a query > 500 characters
        
        with pytest.warns(UserWarning, match="exceeds 500 characters"):
            expanded = expander.expand_query(long_query)
        
        # Verify truncation occurred
        assert len(expanded) <= 600  # Allow some room for expansion
    
    def test_synonym_addition_strategy(self):
        """Test synonym addition expansion strategy."""
        expander = QueryExpander(expansion_strategy="synonym_addition")
        
        # Test with query containing known synonyms
        query = "How to fix database error"
        expanded = expander.expand_query(query)
        
        # Verify expansion occurred
        assert expanded != query
        assert len(expanded) > len(query)
        
        # Verify synonyms were added
        assert "(" in expanded and ")" in expanded
    
    def test_synonym_addition_with_no_matches(self):
        """Test synonym addition when no synonyms match."""
        expander = QueryExpander(expansion_strategy="synonym_addition")
        
        query = "xyz abc def"  # No words in synonym map
        expanded = expander.expand_query(query)
        
        # Should still expand with generic clarification
        assert expanded != query
        assert "detailed explanation" in expanded
    
    def test_clarification_strategy_with_how(self):
        """Test clarification strategy with 'how' question."""
        expander = QueryExpander(expansion_strategy="clarification")
        
        query = "How does the system handle load"
        expanded = expander.expand_query(query)
        
        assert expanded != query
        assert "specific steps and mechanisms" in expanded.lower()
    
    def test_clarification_strategy_with_what(self):
        """Test clarification strategy with 'what' question."""
        expander = QueryExpander(expansion_strategy="clarification")
        
        query = "What is the performance metric"
        expanded = expander.expand_query(query)
        
        assert expanded != query
        assert "explain in detail" in expanded.lower()
    
    def test_clarification_strategy_with_why(self):
        """Test clarification strategy with 'why' question."""
        expander = QueryExpander(expansion_strategy="clarification")
        
        query = "Why does the cache fail"
        expanded = expander.expand_query(query)
        
        assert expanded != query
        assert "reasons and rationale" in expanded.lower()
    
    def test_clarification_strategy_without_question_word(self):
        """Test clarification strategy with non-question query."""
        expander = QueryExpander(expansion_strategy="clarification")
        
        query = "Database connection issues"
        expanded = expander.expand_query(query)
        
        assert expanded != query
        assert "detailed information" in expanded.lower()
    
    def test_decomposition_strategy_with_and(self):
        """Test decomposition strategy with 'and' conjunction."""
        expander = QueryExpander(expansion_strategy="decomposition")
        
        query = "authentication and authorization"
        expanded = expander.expand_query(query)
        
        assert expanded != query
        assert "AND" in expanded
        assert "(" in expanded and ")" in expanded
    
    def test_decomposition_strategy_with_or(self):
        """Test decomposition strategy with 'or' conjunction."""
        expander = QueryExpander(expansion_strategy="decomposition")
        
        query = "cache or database"
        expanded = expander.expand_query(query)
        
        assert expanded != query
        assert "OR" in expanded
        assert "(" in expanded and ")" in expanded
    
    def test_decomposition_strategy_without_conjunction(self):
        """Test decomposition strategy with simple query."""
        expander = QueryExpander(expansion_strategy="decomposition")
        
        query = "system architecture"
        expanded = expander.expand_query(query)
        
        assert expanded != query
        assert "implementation" in expanded.lower()
        assert "benefits" in expanded.lower()
        assert "challenges" in expanded.lower()
    
    def test_interaction_logging(self):
        """Test that all interactions are logged."""
        expander = QueryExpander()
        
        # Perform multiple expansions
        queries = [
            "How to fix errors",
            "What is the system",
            "Database performance"
        ]
        
        for query in queries:
            expander.expand_query(query)
        
        # Verify all interactions were logged
        log = expander.get_interaction_log()
        assert len(log) == len(queries)
        
        # Verify log structure
        for i, entry in enumerate(log):
            assert "timestamp" in entry
            assert "strategy" in entry
            assert "original_query" in entry
            assert "expanded_query" in entry
            assert "expansion_occurred" in entry
            
            assert entry["original_query"] == queries[i]
            assert entry["strategy"] == "synonym_addition"
            assert entry["expansion_occurred"] is True
    
    def test_get_interaction_log_returns_copy(self):
        """Test that get_interaction_log returns a copy, not reference."""
        expander = QueryExpander()
        expander.expand_query("test query")
        
        log1 = expander.get_interaction_log()
        log2 = expander.get_interaction_log()
        
        # Verify they are equal but not the same object
        assert log1 == log2
        assert log1 is not log2
        
        # Modifying one should not affect the other
        log1.append({"test": "data"})
        assert len(log1) != len(log2)
    
    def test_expansion_always_differs_from_original(self):
        """Test that expansion always produces different output."""
        strategies = ["synonym_addition", "clarification", "decomposition"]
        test_queries = [
            "simple query",
            "How does it work",
            "authentication and authorization",
            "database performance issues"
        ]
        
        for strategy in strategies:
            expander = QueryExpander(expansion_strategy=strategy)
            for query in test_queries:
                expanded = expander.expand_query(query)
                assert expanded != query, f"Strategy {strategy} failed to expand: {query}"
    
    def test_special_characters_in_query(self):
        """Test handling of special characters in queries."""
        expander = QueryExpander()
        
        queries_with_special_chars = [
            "What's the error?",
            "How to fix: database connection",
            "System (production) performance",
            "API endpoint /users/{id}"
        ]
        
        for query in queries_with_special_chars:
            expanded = expander.expand_query(query)
            assert expanded != query
            assert len(expanded) > 0
    
    def test_unicode_in_query(self):
        """Test handling of Unicode characters in queries."""
        expander = QueryExpander()
        
        unicode_queries = [
            "How to handle データベース errors",
            "System performance in 中文",
            "API with émojis 🚀"
        ]
        
        for query in unicode_queries:
            expanded = expander.expand_query(query)
            assert expanded != query
            assert len(expanded) > 0
    
    def test_case_sensitivity(self):
        """Test that expansion handles different cases correctly."""
        expander = QueryExpander(expansion_strategy="synonym_addition")
        
        # Test with different cases
        queries = [
            "How to fix error",
            "How to FIX error",
            "How to Fix Error"
        ]
        
        for query in queries:
            expanded = expander.expand_query(query)
            assert expanded != query
            # All should produce expansions (case-insensitive matching)
    
    def test_multiple_expansions_same_query(self):
        """Test that expanding the same query multiple times is consistent."""
        expander = QueryExpander()
        
        query = "How to fix database error"
        expanded1 = expander.expand_query(query)
        expanded2 = expander.expand_query(query)
        
        # Should produce identical expansions
        assert expanded1 == expanded2
        
        # But both should be logged
        log = expander.get_interaction_log()
        assert len(log) == 2
    
    def test_log_entry_structure(self):
        """Test the structure of log entries."""
        expander = QueryExpander()
        query = "test query"
        expanded = expander.expand_query(query)
        
        log = expander.get_interaction_log()
        assert len(log) == 1
        
        entry = log[0]
        
        # Verify all required fields
        assert isinstance(entry["timestamp"], str)
        assert entry["strategy"] == "synonym_addition"
        assert entry["original_query"] == query
        assert entry["expanded_query"] == expanded
        assert isinstance(entry["expansion_occurred"], bool)
        assert entry["expansion_occurred"] is True
    
    def test_complex_technical_query(self):
        """Test expansion of complex technical queries."""
        expander = QueryExpander(expansion_strategy="synonym_addition")
        
        query = "How does the system handle peak load during database queries"
        expanded = expander.expand_query(query)
        
        assert expanded != query
        assert len(expanded) > len(query)
        
        # Should contain synonyms for multiple terms
        assert "(" in expanded
    
    def test_query_with_only_stop_words(self):
        """Test handling of queries with only common stop words."""
        expander = QueryExpander()
        
        query = "the and or but"
        expanded = expander.expand_query(query)
        
        # Should still expand (with generic clarification)
        assert expanded != query
    
    def test_single_word_query(self):
        """Test expansion of single-word queries."""
        expander = QueryExpander(expansion_strategy="synonym_addition")
        
        query = "error"
        expanded = expander.expand_query(query)
        
        assert expanded != query
        assert "exception" in expanded or "failure" in expanded or "bug" in expanded
