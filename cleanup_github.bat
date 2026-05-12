@echo off
REM Cleanup: Remove irrelevant files from GitHub

echo ==========================================
echo   GitHub Repository Cleanup
echo ==========================================
echo.

echo This will remove the following from GitHub:
echo - .kiro/ directory (internal spec files)
echo - Helper guide files (ASSESSMENT_VALIDATION.md, etc.)
echo - Internal validation scripts
echo.
echo These files will remain on your local machine.
echo.

set /p confirm="Continue? (y/n): "
if /i not "%confirm%"=="y" (
    echo Cancelled.
    pause
    exit /b 0
)

echo.
echo Removing files from git tracking...

REM Remove .kiro directory
git rm -r --cached .kiro/ 2>nul

REM Remove helper guide files
git rm --cached ASSESSMENT_VALIDATION.md 2>nul
git rm --cached FINAL_TEST_INSTRUCTIONS.md 2>nul
git rm --cached FINAL_VALIDATION_REPORT.md 2>nul
git rm --cached GITHUB_SUBMISSION_CHECKLIST.md 2>nul
git rm --cached QUICK_START_GITHUB.md 2>nul
git rm --cached REMOVE_KIRO_FROM_GITHUB.md 2>nul
git rm --cached UPLOAD_TO_GITHUB.md 2>nul

REM Remove helper scripts
git rm --cached final_validation.py 2>nul
git rm --cached fix_github_remove_kiro.bat 2>nul
git rm --cached upload_to_github.bat 2>nul
git rm --cached upload_to_github.sh 2>nul
git rm --cached validate_docs.py 2>nul
git rm --cached validate_e2e.py 2>nul

echo.
echo Committing changes...
git commit -m "Clean up: Remove internal helper files and .kiro/ directory

Keep only assessment deliverables:
- Source code (src/)
- Tests (tests/)
- Documentation (docs/)
- Examples (examples/)
- Benchmark report (retrieval_benchmark.md)
- Setup files (README.md, requirements.txt, etc.)"

echo.
echo Pushing to GitHub...
git push origin main

echo.
echo ==========================================
echo   Cleanup Complete!
echo ==========================================
echo.
echo Your repository now contains only:
echo   [*] src/ - Source code
echo   [*] tests/ - Test suite
echo   [*] docs/ - Documentation
echo   [*] examples/ - Usage examples
echo   [*] retrieval_benchmark.md - Benchmark report
echo   [*] README.md - Setup instructions
echo   [*] requirements.txt - Dependencies
echo   [*] pyproject.toml - Package config
echo   [*] .gitignore - Git ignore rules
echo   [*] CONTRIBUTING.md - Development guide
echo   [*] RELEASE_CHECKLIST.md - Release checklist
echo.
echo All helper files removed from GitHub.
echo They still exist on your local machine.
echo.
pause
