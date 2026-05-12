"""Mock Components for Context-Aware Retrieval Engine.

This module provides mock implementations that simulate Vertex AI services
for local development and testing without cloud dependencies.
"""

from typing import List, Dict
from datetime import datetime


class QueryExpander:
    """Mocks Vertex AI GenerativeModel for query expansion.
    
    This class provides rule-based query expansion strategies that simulate
    the behavior of Vertex AI's GenerativeModel for query enhancement in
    retrieval-augmented generation pipelines.
    
    Attributes:
        expansion_strategy: The strategy to use for query expansion.
            Options: "synonym_addition", "clarification", "decomposition"
        interaction_log: List of all query expansion interactions for debugging.
    """
    
    # Synonym mappings for synonym_addition strategy
    SYNONYM_MAP = {
        "error": ["exception", "failure", "bug"],
        "fix": ["resolve", "repair", "correct"],
        "handle": ["manage", "process", "deal with"],
        "load": ["peak traffic", "high volume", "stress"],
        "system": ["application", "service", "platform"],
        "data": ["information", "records", "dataset"],
        "user": ["client", "customer", "end-user"],
        "performance": ["speed", "efficiency", "throughput"],
        "security": ["authentication", "authorization", "access control"],
        "database": ["data store", "repository", "storage"],
        "api": ["interface", "endpoint", "service"],
        "server": ["backend", "host", "node"],
        "network": ["connectivity", "communication", "connection"],
        "cache": ["buffer", "temporary storage", "memory"],
        "query": ["search", "request", "lookup"],
    }
    
    # Clarification templates for clarification strategy
    CLARIFICATION_TEMPLATES = {
        "how": "What are the specific steps and mechanisms for",
        "what": "Please explain in detail what",
        "why": "What are the reasons and rationale for why",
        "when": "Under what conditions and timing does",
        "where": "In which components or locations does",
    }
    
    def __init__(self, expansion_strategy: str = "synonym_addition"):
        """Initialize the QueryExpander with a specific expansion strategy.
        
        Args:
            expansion_strategy: The strategy to use for query expansion.
                Valid options:
                - "synonym_addition": Add synonyms to key terms
                - "clarification": Add clarifying phrases
                - "decomposition": Break complex queries into sub-queries
        
        Raises:
            ValueError: If expansion_strategy is not one of the valid options.
        """
        valid_strategies = ["synonym_addition", "clarification", "decomposition"]
        if expansion_strategy not in valid_strategies:
            raise ValueError(
                f"Invalid expansion strategy '{expansion_strategy}'. "
                f"Must be one of: {', '.join(valid_strategies)}"
            )
        
        self.expansion_strategy = expansion_strategy
        self.interaction_log: List[Dict] = []
    
    def expand_query(self, query: str) -> str:
        """Expand query using rule-based logic.
        
        This method applies the configured expansion strategy to enhance
        the input query for better retrieval results. All interactions
        are logged for debugging purposes.
        
        Args:
            query: The original user query string.
        
        Returns:
            The expanded query string.
        
        Raises:
            ValueError: If query is empty or None.
        """
        # Validate input
        if not query or not isinstance(query, str):
            raise ValueError("Query must be a non-empty string.")
        
        if query.strip() == "":
            raise ValueError("Query cannot be empty or whitespace only.")
        
        # Handle very long queries
        if len(query) > 500:
            import warnings
            warnings.warn(
                f"Query length ({len(query)}) exceeds 500 characters. "
                "Truncating to 500 characters.",
                UserWarning
            )
            query = query[:500]
        
        # Apply expansion strategy
        if self.expansion_strategy == "synonym_addition":
            expanded = self._expand_with_synonyms(query)
        elif self.expansion_strategy == "clarification":
            expanded = self._expand_with_clarification(query)
        elif self.expansion_strategy == "decomposition":
            expanded = self._expand_with_decomposition(query)
        else:
            # Fallback (should not reach here due to __init__ validation)
            expanded = query
        
        # Log the interaction
        self._log_interaction(query, expanded)
        
        return expanded
    
    def _expand_with_synonyms(self, query: str) -> str:
        """Expand query by adding synonyms to key terms.
        
        Args:
            query: The original query.
        
        Returns:
            Query with synonyms added in parentheses.
        """
        words = query.lower().split()
        expanded_parts = []
        
        for word in words:
            # Remove punctuation for matching
            clean_word = word.strip(".,!?;:")
            
            if clean_word in self.SYNONYM_MAP:
                synonyms = self.SYNONYM_MAP[clean_word]
                # Add first synonym in parentheses
                expanded_parts.append(f"{word} ({synonyms[0]})")
            else:
                expanded_parts.append(word)
        
        expanded = " ".join(expanded_parts)
        
        # Ensure expansion actually changed the query
        if expanded == query:
            # If no synonyms were found, add a generic clarification
            expanded = f"{query} (detailed explanation)"
        
        return expanded
    
    def _expand_with_clarification(self, query: str) -> str:
        """Expand query by adding clarifying phrases.
        
        Args:
            query: The original query.
        
        Returns:
            Query with clarifying phrases prepended.
        """
        query_lower = query.lower().strip()
        
        # Check for question words at the start
        for question_word, clarification in self.CLARIFICATION_TEMPLATES.items():
            if query_lower.startswith(question_word):
                # Replace the question word with clarification
                rest_of_query = query[len(question_word):].strip()
                return f"{clarification} {rest_of_query}"
        
        # If no question word found, add generic clarification
        return f"Please provide detailed information about: {query}"
    
    def _expand_with_decomposition(self, query: str) -> str:
        """Expand query by decomposing it into sub-queries.
        
        Args:
            query: The original query.
        
        Returns:
            Query decomposed into multiple sub-queries.
        """
        # Look for compound queries with "and" or "or"
        if " and " in query.lower():
            parts = query.split(" and ")
            sub_queries = [f"({part.strip()})" for part in parts]
            return " AND ".join(sub_queries)
        
        elif " or " in query.lower():
            parts = query.split(" or ")
            sub_queries = [f"({part.strip()})" for part in parts]
            return " OR ".join(sub_queries)
        
        # If no obvious decomposition, break into aspects
        else:
            return f"{query} (including implementation, benefits, and challenges)"
    
    def _log_interaction(self, original_query: str, expanded_query: str) -> None:
        """Log a query expansion interaction.
        
        Args:
            original_query: The original user query.
            expanded_query: The expanded query result.
        """
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "strategy": self.expansion_strategy,
            "original_query": original_query,
            "expanded_query": expanded_query,
            "expansion_occurred": original_query != expanded_query,
        }
        self.interaction_log.append(log_entry)
    
    def get_interaction_log(self) -> List[Dict]:
        """Return all logged interactions for debugging.
        
        Returns:
            List of dictionaries containing interaction details.
            Each dictionary includes:
            - timestamp: ISO format timestamp of the interaction
            - strategy: The expansion strategy used
            - original_query: The original query string
            - expanded_query: The expanded query string
            - expansion_occurred: Boolean indicating if expansion changed the query
        """
        return self.interaction_log.copy()
