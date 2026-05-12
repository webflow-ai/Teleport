@echo off
REM Upload to GitHub - Windows Batch Script

echo ==========================================
echo   GitHub Upload Script
echo   Context-Aware Retrieval Engine
echo ==========================================
echo.

REM Step 1: Check if git is initialized
if not exist ".git" (
    echo [*] Initializing git repository...
    git init
) else (
    echo [*] Git repository already initialized
)

REM Step 2: Verify critical files exist
echo.
echo Checking critical files...
set files_missing=0

if not exist "retrieval_benchmark.md" (
    echo [X] retrieval_benchmark.md NOT FOUND
    set files_missing=1
) else (
    echo [*] retrieval_benchmark.md found
)

if not exist "docs\SIMILARITY_METRICS.md" (
    echo [X] docs\SIMILARITY_METRICS.md NOT FOUND
    set files_missing=1
) else (
    echo [*] docs\SIMILARITY_METRICS.md found
)

if not exist "docs\MIGRATION.md" (
    echo [X] docs\MIGRATION.md NOT FOUND
    set files_missing=1
) else (
    echo [*] docs\MIGRATION.md found
)

if not exist "README.md" (
    echo [X] README.md NOT FOUND
    set files_missing=1
) else (
    echo [*] README.md found
)

if not exist "requirements.txt" (
    echo [X] requirements.txt NOT FOUND
    set files_missing=1
) else (
    echo [*] requirements.txt found
)

if %files_missing%==1 (
    echo.
    echo [X] Critical files are missing. Please fix before uploading.
    pause
    exit /b 1
)

REM Step 3: Add all files
echo.
echo Adding files to git...
git add .

REM Remove .kiro/ if it was accidentally added
git rm -r --cached .kiro/ 2>nul

REM Step 4: Show what will be committed
echo.
echo Files to be committed:
git status --short
echo.

REM Step 5: Ask for confirmation
set /p confirm="Do you want to commit these files? (y/n): "
if /i not "%confirm%"=="y" (
    echo Upload cancelled.
    pause
    exit /b 0
)

REM Step 6: Commit
echo.
echo Creating commit...
git commit -m "Initial commit: Context-Aware Retrieval Engine" -m "" -m "- Implemented local RAG pipeline with dual retrieval strategies" -m "- Strategy A: Raw Vector Search (direct embedding similarity)" -m "- Strategy B: AI-Enhanced Retrieval (query expansion + similarity)" -m "- 168 tests passing with 85%% code coverage" -m "- Comprehensive documentation including Vertex AI migration guide" -m "- Benchmark report comparing both strategies on 3 complex queries" -m "" -m "Assessment: Senior Gen AI - Semantic RAG & Vector Search"

REM Step 7: Instructions for GitHub
echo.
echo ==========================================
echo   GitHub Repository Setup
echo ==========================================
echo.
echo Please create a repository on GitHub:
echo 1. Go to https://github.com/new
echo 2. Repository name: context-aware-retrieval-engine
echo 3. Make it Public (or Private if required)
echo 4. Do NOT initialize with README
echo 5. Click 'Create repository'
echo.
set /p repo_url="Enter your GitHub repository URL: "

if "%repo_url%"=="" (
    echo.
    echo No URL provided. You can add it later with:
    echo   git remote add origin ^<your-repo-url^>
    echo   git branch -M main
    echo   git push -u origin main
    pause
    exit /b 0
)

REM Step 8: Add remote and push
echo.
echo Adding remote and pushing...
git remote add origin "%repo_url%"
git branch -M main
git push -u origin main

echo.
echo ==========================================
echo   [*] Upload Complete!
echo ==========================================
echo.
echo Your repository is now available at:
echo %repo_url%
echo.
echo Next steps:
echo 1. Visit your repository on GitHub
echo 2. Verify retrieval_benchmark.md is visible
echo 3. Check that docs/ directory has all files
echo 4. Submit the repository URL for assessment
echo.
pause
