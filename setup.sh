#!/usr/bin/env bash
# setup.sh — one-time project setup
# Creates a symlink from .claude/commands → playbook/ so Claude Code
# slash commands are available without tracking .claude/ in git.

set -e

echo "Setting up Sentinel MAS..."

# 1. Environment file
if [ ! -f .env ]; then
  cp .env.example .env
  echo "  created .env from .env.example — fill in your API keys"
else
  echo "  .env already exists, skipping"
fi

# 2. Symlink playbook → .claude/commands
mkdir -p .claude
if [ -L .claude/commands ]; then
  echo "  .claude/commands symlink already exists, skipping"
elif [ -d .claude/commands ]; then
  echo "  .claude/commands exists as a real directory — please remove it first"
else
  ln -s "$(pwd)/playbook" .claude/commands
  echo "  linked .claude/commands → playbook/"
fi

echo ""
echo "Done. Next steps:"
echo "  1. Fill in .env with your API keys"
echo "  2. Run: docker compose up -d postgres localstack"
echo "  3. Run: make install"
echo "  4. Open Claude Code and run: /init-specs"
