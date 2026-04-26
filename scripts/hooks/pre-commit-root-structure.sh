#!/bin/bash
# Pre-commit hook to enforce root structure
# This prevents prohibited files from being committed to the root directory

set -e

echo "🔍 Checking root directory structure..."

# Define allowed files in root
ALLOWED_FILES=(
  "README.md"
  "CHANGELOG.md"
  "CONTRIBUTING.md"
  "CODE_OF_CONDUCT.md"
  "CODEOWNERS"
  "LICENSE"
  "DEVELOPER_QUICK_REFERENCE.md"
  "SECURITY.md"
  "Dockerfile"
  "docker-compose.yml"
  "docker-compose.override.yml"
  "Makefile"
  "build.gradle"
  "build.tarl"
  "settings.gradle"
  "gradle.properties"
  "gradlew"
  "gradlew.bat"
  "setup.py"
  "setup.cfg"
  "pyproject.toml"
  "package.json"
  "package-lock.json"
  "requirements.txt"
  "requirements-dev.txt"
  "requirements.in"
  "requirements.lock"
  "pytest.ini"
  "MANIFEST.in"
  ".gitignore"
  ".gitattributes"
  ".gitmodules"
  ".dockerignore"
  ".python-version"
  ".pre-commit-config.yaml"
  "mcp.json"
  "app-config.json"
  "bootstrap.py"
  "quickstart.py"
  "start_api.py"
  "project_ai_cli.py"
  "LAUNCH_MISSION_CONTROL.bat"
  "PR_Overseer.prompt.yml"
  "Project-AI.code-workspace"
)

# Convert to associative array
declare -A ALLOWED
for file in "${ALLOWED_FILES[@]}"; do
  ALLOWED["$file"]=1
done

VIOLATIONS=0

# Check staged files in root directory
while IFS= read -r file; do
  # Only check files in root (not subdirectories)
  if [[ "$file" == */* ]]; then
    continue
  fi
  
  filename=$(basename "$file")
  
  # Skip if allowed
  if [[ -n "${ALLOWED[$filename]}" ]]; then
    continue
  fi
  
  # Check for prohibited patterns
  if [[ "$filename" =~ _COMPLETE\.md$ ]] || \
     [[ "$filename" =~ _SUMMARY\.md$ ]] || \
     [[ "$filename" =~ _STATUS\.md$ ]] || \
     [[ "$filename" =~ _IMPLEMENTATION.*\.md$ ]]; then
    echo "❌ BLOCKED: Cannot commit $filename to root directory"
    echo "   → Move to: docs/internal/archive/"
    VIOLATIONS=$((VIOLATIONS + 1))
  elif [[ "$filename" =~ \.md$ ]] && \
       [[ "$filename" != "README.md" ]] && \
       [[ "$filename" != "CHANGELOG.md" ]] && \
       [[ "$filename" != "CODE_OF_CONDUCT.md" ]] && \
       [[ "$filename" != "CONTRIBUTING.md" ]] && \
       [[ "$filename" != "SECURITY.md" ]] && \
       [[ "$filename" != "DEVELOPER_QUICK_REFERENCE.md" ]]; then
    echo "⚠️  WARNING: Unexpected markdown in root: $filename"
    echo "   → Is this intentional? Should it be in docs/?"
    # Not blocking, just warning
  elif [[ "$filename" =~ \.(backup|bak|tmp)$ ]] || [[ "$filename" =~ ~$ ]]; then
    echo "❌ BLOCKED: Cannot commit backup/temp file: $filename"
    VIOLATIONS=$((VIOLATIONS + 1))
  fi
done < <(git diff --cached --name-only --diff-filter=A)

if [ $VIOLATIONS -gt 0 ]; then
  echo ""
  echo "═══════════════════════════════════════════════════════════"
  echo "❌ COMMIT BLOCKED: Root structure violation(s)"
  echo "═══════════════════════════════════════════════════════════"
  echo ""
  echo "To fix:"
  echo "  1. Move files to appropriate directories"
  echo "  2. Update ROOT_STRUCTURE.md if file should be allowed"
  echo "  3. Re-stage and commit"
  echo ""
  echo "See: docs/architecture/ROOT_STRUCTURE.md"
  echo "═══════════════════════════════════════════════════════════"
  exit 1
fi

echo "✅ Root structure check passed"
exit 0
