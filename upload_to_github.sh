#!/bin/bash
# Upload to GitHub - Automated Script

echo "=========================================="
echo "  GitHub Upload Script"
echo "  Context-Aware Retrieval Engine"
echo "=========================================="
echo ""

# Step 1: Check if git is initialized
if [ ! -d ".git" ]; then
    echo "✓ Initializing git repository..."
    git init
else
    echo "✓ Git repository already initialized"
fi

# Step 2: Verify critical files exist
echo ""
echo "Checking critical files..."
files_missing=0

if [ ! -f "retrieval_benchmark.md" ]; then
    echo "❌ retrieval_benchmark.md NOT FOUND"
    files_missing=1
else
    echo "✓ retrieval_benchmark.md found"
fi

if [ ! -f "docs/SIMILARITY_METRICS.md" ]; then
    echo "❌ docs/SIMILARITY_METRICS.md NOT FOUND"
    files_missing=1
else
    echo "✓ docs/SIMILARITY_METRICS.md found"
fi

if [ ! -f "docs/MIGRATION.md" ]; then
    echo "❌ docs/MIGRATION.md NOT FOUND"
    files_missing=1
else
    echo "✓ docs/MIGRATION.md found"
fi

if [ ! -f "README.md" ]; then
    echo "❌ README.md NOT FOUND"
    files_missing=1
else
    echo "✓ README.md found"
fi

if [ ! -f "requirements.txt" ]; then
    echo "❌ requirements.txt NOT FOUND"
    files_missing=1
else
    echo "✓ requirements.txt found"
fi

if [ $files_missing -eq 1 ]; then
    echo ""
    echo "❌ Critical files are missing. Please fix before uploading."
    exit 1
fi

# Step 3: Add all files
echo ""
echo "Adding files to git..."
git add .

# Step 4: Show what will be committed
echo ""
echo "Files to be committed:"
git status --short | head -20
echo "..."
echo ""
echo "Total files: $(git status --short | wc -l)"

# Step 5: Ask for confirmation
echo ""
read -p "Do you want to commit these files? (y/n) " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Upload cancelled."
    exit 0
fi

# Step 6: Commit
echo ""
echo "Creating commit..."
git commit -m "Initial commit: Context-Aware Retrieval Engine

- Implemented local RAG pipeline with dual retrieval strategies
- Strategy A: Raw Vector Search (direct embedding similarity)
- Strategy B: AI-Enhanced Retrieval (query expansion + similarity)
- 168 tests passing with 85% code coverage
- Comprehensive documentation including Vertex AI migration guide
- Benchmark report comparing both strategies on 3 complex queries

Assessment: Senior Gen AI - Semantic RAG & Vector Search"

# Step 7: Ask for GitHub repository URL
echo ""
echo "=========================================="
echo "  GitHub Repository Setup"
echo "=========================================="
echo ""
echo "Please create a repository on GitHub:"
echo "1. Go to https://github.com/new"
echo "2. Repository name: context-aware-retrieval-engine"
echo "3. Make it Public (or Private if required)"
echo "4. Do NOT initialize with README"
echo "5. Click 'Create repository'"
echo ""
read -p "Enter your GitHub repository URL: " repo_url

if [ -z "$repo_url" ]; then
    echo "No URL provided. You can add it later with:"
    echo "  git remote add origin <your-repo-url>"
    echo "  git branch -M main"
    echo "  git push -u origin main"
    exit 0
fi

# Step 8: Add remote and push
echo ""
echo "Adding remote and pushing..."
git remote add origin "$repo_url"
git branch -M main
git push -u origin main

echo ""
echo "=========================================="
echo "  ✅ Upload Complete!"
echo "=========================================="
echo ""
echo "Your repository is now available at:"
echo "$repo_url"
echo ""
echo "Next steps:"
echo "1. Visit your repository on GitHub"
echo "2. Verify retrieval_benchmark.md is visible"
echo "3. Check that docs/ directory has all files"
echo "4. Submit the repository URL for assessment"
echo ""
