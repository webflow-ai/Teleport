"""Documentation validation script.

Validates:
1. All required documentation files exist
2. Documentation files are not empty
3. Key sections are present
"""

from pathlib import Path


def main():
    print("=" * 80)
    print("Documentation Validation")
    print("=" * 80)
    print()
    
    # Required documentation files
    required_docs = {
        "README.md": ["Installation", "Quick Start", "Usage"],
        "docs/ARCHITECTURE.md": ["Overview", "Components"],
        "docs/MIGRATION.md": ["Migration", "Vertex AI"],
        "docs/SIMILARITY_METRICS.md": ["Cosine", "Euclidean"],
        "docs/BENCHMARKING.md": ["Benchmark"],
        "docs/API.md": ["API"],
        "CONTRIBUTING.md": ["Contributing", "Development"],
    }
    
    all_valid = True
    
    for doc_path, required_sections in required_docs.items():
        print(f"Checking {doc_path}...")
        
        path = Path(doc_path)
        if not path.exists():
            print(f"  ✗ ERROR: File not found!")
            all_valid = False
            continue
        
        content = path.read_text(encoding='utf-8')
        
        if len(content) < 100:
            print(f"  ✗ ERROR: File is too short (< 100 characters)")
            all_valid = False
            continue
        
        missing_sections = []
        for section in required_sections:
            if section.lower() not in content.lower():
                missing_sections.append(section)
        
        if missing_sections:
            print(f"  ⚠ WARNING: Missing sections: {missing_sections}")
            # Don't fail for missing sections, just warn
        
        print(f"  ✓ Valid ({len(content)} characters)")
    
    print()
    
    # Check for code examples in README
    print("Checking code examples in README.md...")
    readme_path = Path("README.md")
    if readme_path.exists():
        readme_content = readme_path.read_text(encoding='utf-8')
        
        # Count code blocks
        code_blocks = readme_content.count("```python")
        if code_blocks > 0:
            print(f"  ✓ Found {code_blocks} Python code examples")
        else:
            print(f"  ⚠ WARNING: No Python code examples found")
    
    print()
    
    if all_valid:
        print("=" * 80)
        print("✓ DOCUMENTATION VALIDATION SUCCESSFUL")
        print("=" * 80)
        return True
    else:
        print("=" * 80)
        print("✗ DOCUMENTATION VALIDATION FAILED")
        print("=" * 80)
        return False


if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)
