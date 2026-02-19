#!/bin/bash
# Unified Logger Installation Script
# Usage: ./install.sh

set -e

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OPENCLAW_SKILLS="${HOME}/.openclaw/workspace/skills"
TARGET_DIR="${OPENCLAW_SKILLS}/unified-logger"

echo "Installing Unified Conversation Logger..."
echo ""

# Check dependencies
echo "Checking dependencies..."

if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Please install Python 3.8+"
    exit 1
fi
echo "✓ Python 3 found"

if ! command -v memvid &> /dev/null; then
    echo "⚠️  Memvid CLI not found. Installing..."
    npm install -g @memvid/cli || {
        echo "❌ Failed to install Memvid CLI. Install manually: npm install -g @memvid/cli"
        exit 1
    }
fi
echo "✓ Memvid CLI found"

# Create OpenClaw skills directory if needed
mkdir -p "${OPENCLAW_SKILLS}"

# Copy skill files
echo ""
echo "Installing skill to ${TARGET_DIR}..."
if [ -d "${TARGET_DIR}" ]; then
    echo "⚠️  Skill already exists. Overwrite? (y/N)"
    read -r response
    if [[ ! "$response" =~ ^[Yy]$ ]]; then
        echo "Installation cancelled."
        exit 0
    fi
    rm -rf "${TARGET_DIR}"
fi

cp -r "${SKILL_DIR}" "${TARGET_DIR}"
echo "✓ Skill files copied"

# Make log.py executable
chmod +x "${TARGET_DIR}/tools/log.py"

# Initialize memory file if doesn't exist
MEMVID_PATH="${HOME}/.openclaw/workspace/anthony_memory.mv2"
if [ ! -f "${MEMVID_PATH}" ]; then
    echo ""
    echo "Creating initial memory file..."
    memvid create "${MEMVID_PATH}" || {
        echo "⚠️  Could not create memory file. Create manually with: memvid create ${MEMVID_PATH}"
    }
    echo "✓ Memory file created at ${MEMVID_PATH}"
else
    echo "✓ Memory file already exists at ${MEMVID_PATH}"
fi

# Set up environment variables
BASHRC="${HOME}/.bashrc"
if ! grep -q "JSONL_LOG_PATH" "${BASHRC}" 2>/dev/null; then
    echo ""
    echo "Adding environment variables to ${BASHRC}..."
    cat >> "${BASHRC}" << 'EOF'

# Unified Logger configuration
export JSONL_LOG_PATH="${HOME}/.openclaw/workspace/conversation_log.jsonl"
export MEMVID_PATH="${HOME}/.openclaw/workspace/anthony_memory.mv2"
export MEMVID_BIN="$(which memvid 2>/dev/null || echo ${HOME}/.npm-global/bin/memvid)"
EOF
    echo "✓ Environment variables added"
    echo "  Run 'source ${BASHRC}' to apply changes"
else
    echo "✓ Environment variables already configured"
fi

echo ""
echo "═══════════════════════════════════════════"
echo "  Installation Complete!"
echo "═══════════════════════════════════════════"
echo ""
echo "Next steps:"
echo "  1. Source your profile: source ${BASHRC}"
echo "  2. Start OpenClaw - logging begins automatically"
echo "  3. Search your conversations:"
echo ""
echo "     memvid ask ${MEMVID_PATH} 'What did we discuss?'"
echo ""
echo "Documentation: ${TARGET_DIR}/README.md"
echo ""
