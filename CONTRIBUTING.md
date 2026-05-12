# Contributing to Context-Aware Retrieval Engine

Thank you for your interest in contributing to the Context-Aware Retrieval Engine! This document provides guidelines for setting up your development environment, writing tests, and submitting contributions.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Project Structure](#project-structure)
- [Testing Guidelines](#testing-guidelines)
- [Code Style](#code-style)
- [Contribution Process](#contribution-process)
- [Reporting Issues](#reporting-issues)
- [Feature Requests](#feature-requests)

## Code of Conduct

We are committed to providing a welcoming and inclusive environment for all contributors. Please be respectful and constructive in all interactions.

## Getting Started

Before contributing, please:

1. **Read the documentation**: Familiarize yourself with the [README.md](README.md) and [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)
2. **Check existing issues**: Look for open issues or create a new one to discuss your proposed changes
3. **Fork the repository**: Create your own fork to work on changes
4. **Create a branch**: Use descriptive branch names (e.g., `feature/add-new-metric`, `bugfix/fix-embedding-error`)

## Development Setup

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Git

### Initial Setup

1. **Clone your fork**:
```bash
git clone https://github.com/your-username/context-aware-retrieval-engine.git
cd context-aware-retrieval-engine
```

2. **Create a virtual environment** (strongly recommended):
```bash
python -m venv .venv

# On Linux/macOS:
source .venv/bin/activate

# On Windows:
.venv\Scripts\activate
```

3. **Install dependencies**:
```bash
# Install core dependencies
pip install -r requirements.txt

# Or install with development dependencies
pip install -e ".[dev]"
```

4. **Verify installation**:
```bash
# Run tests to ensure everything is working
pytest

# Check that imports work
python -c "from src.embedding import EmbeddingGenerator; print('Setup successful!')"
```

### Development Dependencies

The project uses the following development tools:

- **pytest**: Test framework
- **pytest-cov**: Coverage reporting
- **hypothesis**: Property-based testing
- **black** (optional): Code formatting
- **flake8** (optional): Linting

Install optional tools:
```bash
pip install black flake8
```

## Project Structure

Understanding the codebase organization:

```
context-aware-retrieval-engine/
├── src/                      # Source code
│   ├── embedding.py          # Embedding generation (sentence-transformers)
│   ├── storage.py            # Vector store implementations (FAISS, ChromaDB, NumPy)
│   ├── retrieval.py          # Retrieval strategies (Raw, AI-Enhanced)
│   ├── mocks.py              # Query expander mock (Vertex AI simulation)
│   ├── orchestrator.py       # Pipeline orchestration
│   ├── benchmark.py          # Benchmarking engine
│   ├── config.py             # Configuration management
│   └── models.py             # Data models and schemas
├── tests/                    # Test suite
│   ├── fixtures/             # Test data and fixtures
│   │   ├── sample_documents.py
│   │   ├── benchmark_queries.py
│   │   └── expected_outputs.py
│   ├── test_embedding.py     # Embedding tests
│   ├── test_storage.py       # Storage tests
│   ├── test_retrieval.py     # Retrieval tests
│   ├── test_mocks.py         # Mock tests
│   ├── test_orchestrator.py  # Orchestrator tests
│   └── test_benchmark.py     # Benchmark tests
├── examples/                 # Usage examples
├── docs/                     # Documentation
└── .kiro/specs/             # Specification documents
```

### Key Modules

- **embedding.py**: Wraps sentence-transformers for text-to-vector conversion
- **storage.py**: Abstract vector store interface with FAISS, ChromaDB, and NumPy implementations
- **retrieval.py**: Strategy pattern for different retrieval approaches
- **orchestrator.py**: High-level API coordinating ingestion and retrieval
- **benchmark.py**: Comparative analysis of retrieval strategies

## Testing Guidelines

The project uses a **dual testing strategy** combining property-based tests and example-based unit tests.

### Testing Philosophy

1. **Property-Based Tests (PBT)**: Verify universal correctness properties across all valid inputs
2. **Unit Tests**: Verify specific behaviors and edge cases
3. **Integration Tests**: Verify end-to-end pipeline functionality
4. **Performance Tests**: Verify latency and resource requirements

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=src --cov-report=html --cov-report=term-missing

# Run specific test file
pytest tests/test_embedding.py

# Run specific test class or function
pytest tests/test_embedding.py::TestEmbeddingGenerator::test_encode_single_string

# Run tests matching a pattern
pytest -k "embedding"

# Run with verbose output
pytest -v

# Run property-based tests only (if marked)
pytest -m property
```

### Writing Property-Based Tests

Property-based tests use the `hypothesis` library to generate random test inputs and verify universal properties.

**When to use PBT**:
- Testing pure functions with clear input/output behavior
- Verifying mathematical properties (idempotence, commutativity, etc.)
- Testing data transformations and algorithms
- Ensuring consistency across varying inputs

**Example property test**:

```python
from hypothesis import given, strategies as st
import numpy as np

@given(st.text(min_size=1, max_size=1000))
def test_embedding_dimension_consistency(text):
    """
    Feature: context-aware-retrieval-engine, Property 2: Embedding Dimension Consistency
    For any valid text input, all generated embeddings shall have identical dimensionality.
    """
    generator = EmbeddingGenerator()
    embedding1 = generator.encode(text)
    embedding2 = generator.encode(text + " additional text")
    assert embedding1.shape[1] == embedding2.shape[1]
```

**Property test configuration**:
- Minimum 100 iterations per property test
- Tag format: `# Feature: context-aware-retrieval-engine, Property {number}: {property_text}`
- Use appropriate `hypothesis.strategies` for input generation

**Common strategies**:
```python
import hypothesis.strategies as st

# Text strings
st.text(min_size=1, max_size=1000)

# Lists of text
st.lists(st.text(min_size=1), min_size=1, max_size=100)

# Integers in range
st.integers(min_value=1, max_value=100)

# Floating point numbers
st.floats(min_value=0.0, max_value=1.0, allow_nan=False)

# NumPy arrays
st.lists(st.floats(allow_nan=False), min_size=384, max_size=384).map(np.array)
```

### Writing Unit Tests

Unit tests verify specific behaviors and edge cases using concrete examples.

**Test structure**:

```python
import pytest
from src.embedding import EmbeddingGenerator

class TestEmbeddingGenerator:
    """Test suite for EmbeddingGenerator class."""
    
    def test_initialization_default_model(self):
        """Test that EmbeddingGenerator initializes with default model."""
        generator = EmbeddingGenerator()
        assert generator.model_name == "all-MiniLM-L6-v2"
        assert generator.model is not None
    
    def test_encode_empty_string_raises_error(self):
        """Test that empty string raises ValueError."""
        generator = EmbeddingGenerator()
        
        with pytest.raises(ValueError, match="empty strings"):
            generator.encode("")
```

**Best practices**:
- One assertion per test (when possible)
- Use descriptive test names that explain what is being tested
- Include docstrings explaining the test purpose
- Test both success and failure cases
- Use `pytest.raises()` for exception testing
- Use `pytest.mark.parametrize()` for testing multiple inputs

**Example parametrized test**:

```python
@pytest.mark.parametrize("batch_size", [1, 5, 10, 50])
def test_batch_processing_correspondence(batch_size):
    """Test that number of embeddings equals number of input texts."""
    generator = EmbeddingGenerator()
    texts = [f"Text number {i}" for i in range(batch_size)]
    embeddings = generator.encode(texts)
    assert embeddings.shape[0] == batch_size
```

### Writing Integration Tests

Integration tests verify that components work together correctly.

```python
def test_end_to_end_pipeline():
    """Test complete ingestion and retrieval pipeline."""
    # Setup
    embedding_generator = EmbeddingGenerator()
    vector_store = NumpyVectorStore(similarity_metric="cosine")
    raw_strategy = RawVectorSearch(embedding_generator, vector_store)
    
    orchestrator = RAGOrchestrator(
        embedding_generator,
        vector_store,
        strategies={"raw": raw_strategy}
    )
    
    # Ingest documents
    documents = ["Document 1 content", "Document 2 content"]
    stats = orchestrator.ingest_documents(documents, chunk_size=300)
    
    assert stats.total_chunks >= 2
    
    # Retrieve
    result = orchestrator.retrieve("test query", strategy_name="raw", k=3)
    
    assert len(result.chunks) > 0
    assert len(result.scores) == len(result.chunks)
    assert result.latency_ms > 0
```

### Test Coverage Requirements

- **Overall code coverage**: ≥ 80%
- **New features**: Must include tests achieving ≥ 80% coverage
- **Bug fixes**: Must include regression tests
- **Property tests**: All 26 correctness properties should be covered

Check coverage:
```bash
pytest --cov=src --cov-report=html
# Open htmlcov/index.html in browser to view detailed coverage
```

### Test Fixtures

Use fixtures in `tests/fixtures/` for reusable test data:

```python
# tests/fixtures/sample_documents.py
SAMPLE_DOCUMENTS = [
    "Microservices architecture is a design pattern...",
    "Load balancing distributes incoming network traffic...",
    "Caching is a technique used to store frequently accessed data..."
]

# In your test file
from tests.fixtures.sample_documents import SAMPLE_DOCUMENTS

def test_with_fixtures():
    orchestrator.ingest_documents(SAMPLE_DOCUMENTS)
    # ... rest of test
```

## Code Style

### Python Style Guidelines

Follow [PEP 8](https://pep8.org/) style guidelines:

- **Indentation**: 4 spaces (no tabs)
- **Line length**: Maximum 100 characters (120 for comments/docstrings)
- **Imports**: Group into standard library, third-party, and local imports
- **Naming conventions**:
  - Classes: `PascalCase` (e.g., `EmbeddingGenerator`)
  - Functions/methods: `snake_case` (e.g., `encode_text`)
  - Constants: `UPPER_SNAKE_CASE` (e.g., `DEFAULT_MODEL_NAME`)
  - Private methods: `_leading_underscore` (e.g., `_internal_method`)

### Docstrings

Use Google-style docstrings:

```python
def encode(self, texts: Union[str, List[str]]) -> np.ndarray:
    """
    Generate embeddings for input text(s).
    
    Args:
        texts: Single string or list of strings to encode
        
    Returns:
        numpy array of shape (n, embedding_dim) where n is number of texts
        
    Raises:
        ValueError: If texts is empty or contains empty strings
        TypeError: If texts is not a string or list of strings
        
    Example:
        >>> generator = EmbeddingGenerator()
        >>> embedding = generator.encode("Hello world")
        >>> embedding.shape
        (1, 384)
    """
```

### Type Hints

Use type hints for all function signatures:

```python
from typing import List, Dict, Optional, Union
import numpy as np

def search(self, query_embedding: np.ndarray, k: int = 3) -> List[SearchResult]:
    """Search for similar embeddings."""
    pass
```

### Code Formatting (Optional)

Use `black` for automatic code formatting:

```bash
# Format all Python files
black src/ tests/

# Check formatting without making changes
black --check src/ tests/
```

Use `flake8` for linting:

```bash
# Lint all Python files
flake8 src/ tests/

# With custom configuration
flake8 --max-line-length=100 src/ tests/
```

## Contribution Process

### 1. Create an Issue

Before starting work, create or comment on an issue to:
- Describe the problem or feature
- Discuss the proposed approach
- Get feedback from maintainers

### 2. Fork and Branch

```bash
# Fork the repository on GitHub, then clone your fork
git clone https://github.com/your-username/context-aware-retrieval-engine.git
cd context-aware-retrieval-engine

# Add upstream remote
git remote add upstream https://github.com/original-owner/context-aware-retrieval-engine.git

# Create a feature branch
git checkout -b feature/your-feature-name
```

### 3. Make Changes

- Write code following the style guidelines
- Add tests for new functionality
- Update documentation as needed
- Ensure all tests pass locally

```bash
# Run tests
pytest

# Check coverage
pytest --cov=src --cov-report=term-missing

# Format code (optional)
black src/ tests/
```

### 4. Commit Changes

Write clear, descriptive commit messages:

```bash
git add .
git commit -m "Add feature: implement new similarity metric

- Add Euclidean distance support to vector stores
- Update configuration to allow metric selection
- Add tests for new metric
- Update documentation with usage examples"
```

**Commit message guidelines**:
- First line: Brief summary (50 characters or less)
- Blank line
- Detailed description (wrap at 72 characters)
- Reference issue numbers (e.g., "Fixes #123")

### 5. Push and Create Pull Request

```bash
# Push to your fork
git push origin feature/your-feature-name
```

Create a pull request on GitHub with:
- **Title**: Clear, concise description of changes
- **Description**: 
  - What changes were made and why
  - How to test the changes
  - Any breaking changes or migration notes
  - Related issue numbers (e.g., "Closes #123")

**Pull request template**:

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix (non-breaking change fixing an issue)
- [ ] New feature (non-breaking change adding functionality)
- [ ] Breaking change (fix or feature causing existing functionality to change)
- [ ] Documentation update

## Testing
- [ ] All existing tests pass
- [ ] New tests added for new functionality
- [ ] Coverage remains ≥ 80%

## Checklist
- [ ] Code follows project style guidelines
- [ ] Self-review completed
- [ ] Comments added for complex logic
- [ ] Documentation updated
- [ ] No new warnings generated
```

### 6. Code Review

- Respond to review comments promptly
- Make requested changes in new commits
- Push updates to the same branch
- Request re-review when ready

### 7. Merge

Once approved, maintainers will merge your pull request.

## Reporting Issues

### Bug Reports

When reporting bugs, include:

1. **Description**: Clear description of the bug
2. **Steps to reproduce**: Minimal code example demonstrating the issue
3. **Expected behavior**: What you expected to happen
4. **Actual behavior**: What actually happened
5. **Environment**:
   - Python version
   - Operating system
   - Package versions (`pip list`)
6. **Error messages**: Full stack traces if applicable

**Example bug report**:

```markdown
## Bug Description
EmbeddingGenerator crashes when encoding very long texts (>10,000 characters)

## Steps to Reproduce
```python
from src.embedding import EmbeddingGenerator

generator = EmbeddingGenerator()
long_text = "a" * 15000
embedding = generator.encode(long_text)  # Crashes here
```

## Expected Behavior
Should either truncate text or raise a clear error message

## Actual Behavior
Crashes with cryptic CUDA error

## Environment
- Python 3.9.7
- sentence-transformers 2.2.2
- Ubuntu 20.04
```

### Security Issues

For security vulnerabilities, please **do not** create a public issue. Instead, email the maintainers directly at [security@example.com].

## Feature Requests

When requesting features, include:

1. **Use case**: Describe the problem you're trying to solve
2. **Proposed solution**: Your idea for how to solve it
3. **Alternatives**: Other approaches you've considered
4. **Additional context**: Any relevant examples or references

## Development Tips

### Debugging

Use Python's built-in debugger:

```python
import pdb; pdb.set_trace()  # Set breakpoint
```

Or use pytest with debugging:

```bash
pytest --pdb  # Drop into debugger on failure
pytest -x --pdb  # Stop on first failure and debug
```

### Performance Profiling

Profile code to identify bottlenecks:

```python
import cProfile
import pstats

profiler = cProfile.Profile()
profiler.enable()

# Your code here

profiler.disable()
stats = pstats.Stats(profiler)
stats.sort_stats('cumulative')
stats.print_stats(10)  # Top 10 slowest functions
```

### Working with Vector Stores

When testing vector store implementations:
- Use small datasets for unit tests
- Use realistic datasets for integration tests
- Clean up temporary files in teardown

```python
import tempfile
import os

def test_vector_store_persistence():
    with tempfile.TemporaryDirectory() as tmpdir:
        store_path = os.path.join(tmpdir, "test_store")
        # Test code here
        # Cleanup happens automatically
```

## Questions?

If you have questions not covered in this guide:

1. Check the [documentation](docs/)
2. Search [existing issues](https://github.com/owner/repo/issues)
3. Create a new issue with the "question" label
4. Join our community discussions (if applicable)

## License

By contributing, you agree that your contributions will be licensed under the same license as the project (see LICENSE file).

## Acknowledgments

Thank you for contributing to the Context-Aware Retrieval Engine! Your efforts help make this project better for everyone.
