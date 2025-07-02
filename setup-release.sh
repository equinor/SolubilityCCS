#!/bin/bash
# Setup script for automated releases

echo "🚀 Setting up automated releases for SolubilityCCS"
echo ""

# Check if we're in a git repository
if ! git rev-parse --git-dir > /dev/null 2>&1; then
    echo "❌ Error: Not in a git repository"
    exit 1
fi

# Check if GitHub CLI is installed
if ! command -v gh &> /dev/null; then
    echo "📦 GitHub CLI not found. Install with:"
    echo "   - macOS: brew install gh"
    echo "   - Ubuntu/Debian: sudo apt install gh"
    echo "   - Or visit: https://cli.github.com/"
    echo ""
else
    echo "✅ GitHub CLI found"
fi

echo "📋 Setup Checklist:"
echo ""
echo "1. 🔑 PyPI API Token Setup:"
echo "   - Go to https://pypi.org/manage/account/token/"
echo "   - Create a new API token for your project"
echo "   - Copy the token (starts with 'pypi-')"
echo ""

if command -v gh &> /dev/null; then
    echo "2. 🔐 Add token to GitHub Secrets (using GitHub CLI):"
    echo "   Run: gh secret set PYPI_API_TOKEN"
    echo "   Then paste your PyPI token when prompted"
    echo ""
else
    echo "2. 🔐 Add token to GitHub Secrets (manually):"
    echo "   - Go to your GitHub repo → Settings → Secrets and variables → Actions"
    echo "   - Click 'New repository secret'"
    echo "   - Name: PYPI_API_TOKEN"
    echo "   - Value: Your PyPI token"
    echo ""
fi

echo "3. 🛡️  Set up branch protection (recommended):"
echo "   - Go to GitHub repo → Settings → Branches"
echo "   - Add rule for 'main' branch"
echo "   - Enable: 'Require pull request reviews before merging'"
echo "   - Enable: 'Require status checks to pass before merging'"
echo ""

echo "4. ✨ Test the workflow:"
echo "   - Create a test branch: git checkout -b test-release"
echo "   - Make a small change and commit"
echo "   - Create a PR with title: 'feat: test automated release'"
echo "   - Merge the PR to trigger an automatic minor release"
echo ""

echo "🎯 Release Types:"
echo "   - patch (1.0.0 → 1.0.1): Default for bug fixes"
echo "   - minor (1.0.0 → 1.1.0): Include 'feat' or 'feature' in PR title"
echo "   - major (1.0.0 → 2.0.0): Include 'breaking' or 'major' in PR title"
echo ""

echo "📚 For more details, see RELEASE_PROCESS.md"
echo ""

# Check current git status
current_branch=$(git branch --show-current)
echo "🌿 Current branch: $current_branch"

if [ "$current_branch" != "main" ] && [ "$current_branch" != "master" ]; then
    echo "⚠️  Note: You're not on the main branch. The release workflow triggers on merges to main."
fi

echo ""
echo "🎉 Automated release system is ready!"
echo "   Next: Set up your PyPI token secret and start creating PRs!"
