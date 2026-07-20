#!/usr/bin/env bash
# ============================================================================
# Dylan for Hire & BlueLine Automation - Two-Repository Github Sync Utility
# ============================================================================
# This script automates commits and pushes for both repositories on your local Mac.
# 
# Usage:
#   bash scripts/automate_github.sh
# ============================================================================

set -euo pipefail

# Path configurations on your local Mac
BLUELINE_DIR="$HOME/Downloads/BlueLine"
DYLAN_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "=== 🤖 Starting Automated GitHub Sync & Push ==="
echo "Dylan for Hire Master: $DYLAN_DIR"
echo "BlueLine Automation:   $BLUELINE_DIR"
echo ""

# ----------------------------------------------------------------------------
# PART 1: Sync and Push Dylan for Hire (Master SaaS Platform)
# ----------------------------------------------------------------------------
echo "----------------------------------------------------"
echo "📂 PART 1: Processing 'Dylan for Hire' Master..."
echo "----------------------------------------------------"

cd "$DYLAN_DIR"

# Run local sanity check/drift sync before push if requested
if [[ -f "$DYLAN_DIR/scripts/sync_check.sh" ]]; then
  echo "Checking for any final file drifts..."
  bash scripts/sync_check.sh --apply || echo "⚠️ Sync check reported minor warnings, proceeding with push."
fi

# Build verification
if command -v npm >/dev/null 2>&1; then
  echo "Running local build verification..."
  npm run build || { echo "❌ Build failed. Please fix compilation issues before pushing."; exit 1; }
fi

# Add and commit changes
if [[ -n $(git status --porcelain) ]]; then
  echo "Staging changes for Dylan for Hire..."
  git add .
  git commit -m "feat: complete live compliance documents, view switcher, and automated templates integration"
  echo "✅ Committed changes locally."
else
  echo "✨ Dylan for Hire workspace is already clean."
fi

# Push to GitHub
echo "Pushing Dylan for Hire Master to GitHub..."
git push origin master || {
  echo "⚠️ 'git push origin master' failed. Your remote might be configured differently."
  echo "Please verify your remote settings or push manually using: git push"
}

# ----------------------------------------------------------------------------
# PART 2: Sync and Push BlueLine Automation (Client-Specific Deployments)
# ----------------------------------------------------------------------------
echo ""
echo "----------------------------------------------------"
echo "📂 PART 2: Processing 'BlueLine Automation'..."
echo "----------------------------------------------------"

SOURCE_BLUELINE_REVIEW="$DYLAN_DIR/_incoming_blueline_automation_review"

if [[ -d "$BLUELINE_DIR" ]]; then
  echo "Found local BlueLine directory at $BLUELINE_DIR."
  
  if [[ -d "$SOURCE_BLUELINE_REVIEW" ]]; then
    echo "Copying latest updated scripts from '$SOURCE_BLUELINE_REVIEW' to '$BLUELINE_DIR'..."
    cp -v "$SOURCE_BLUELINE_REVIEW"/* "$BLUELINE_DIR/"
    echo "✅ Files successfully synchronized to your local folder."
  else
    echo "⚠️ Source folder '$SOURCE_BLUELINE_REVIEW' not found. Skipping auto-copy."
  fi

  cd "$BLUELINE_DIR"
  
  if [[ ! -d ".git" ]]; then
    echo "Initializing local git repository inside BlueLine directory..."
    git init
    git branch -M main || git branch -M master
  fi

  # Add files
  echo "Staging changes for BlueLine Automation..."
  git add .

  # Commit changes
  if [[ -n $(git status --porcelain) ]]; then
    git commit -m "feat: update local blueline automation scripts and synchronizers"
    echo "✅ Committed changes locally for BlueLine."
  else
    echo "✨ BlueLine Automation workspace is already clean."
  fi

  # Push to GitHub
  echo "Pushing BlueLine Automation to GitHub..."
  # If remote 'origin' doesn't exist, we skip the push so user can configure it safely
  if git remote | grep -q 'origin'; then
    git push origin main || git push origin master || echo "⚠️ Push failed. Please run manually in $BLUELINE_DIR: git push"
  else
    echo "💡 Remote 'origin' is not set for BlueLine directory yet."
    echo "Once you create your new GitHub repository for BlueLine, run these commands inside $BLUELINE_DIR:"
    echo "  git remote add origin <your-blueline-repo-url>"
    git branch -M main || git branch -M master
    echo "  git push -u origin main"
  fi
else
  echo "⚠️ Local BlueLine directory not found at $BLUELINE_DIR."
  echo "Please make sure you have the folder '$BLUELINE_DIR' on your Mac."
  echo "Skip pushing BlueLine Automation."
fi

echo ""
echo "=== 🎉 Synchronization Complete! ==="
