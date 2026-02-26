# Unified Logger for OpenClaw - v1.4.0

[![OpenClaw](https://img.shields.io/badge/OpenClaw->=2026.2.12-blue)](https://openclaw.ai)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Memvid](https://img.shields.io/badge/Memvid-2.0+-green)](https://memvid.com)

> **Give your AI Agent Photographic Memory**
>
> Memvid: A single-file memory layer for AI agents with instant retrieval and long-term memory. Persistent, versioned, and portable memory, without databases.

A dual-output conversation logger for [OpenClaw](https://openclaw.ai) that captures **everything** - user messages, assistant responses, sub-agent conversations, tool executions, and system events - to both JSONL (backup) and Memvid (semantic search) formats.

## ✨ What Makes This Different

- **📝 Dual Storage** - Every message saved to JSONL + Memvid simultaneously
- **🔍 Semantic Search** - Ask "What did the researcher agent find about Tesla?" not just keyword search
- **🤖 Full Context** - Captures user input, assistant output, agent chatter, tool results
- **💾 Three Modes** - API (unlimited), Free (50MB), or Sharding (multi-file)
- **🚀 Always On** - Hooks into OpenClaw automatically
- **📅 Weekly Rotation** - Safer free tier usage with automatic weekly file rotation
- **🧠 Neural Embeddings** - Full semantic embeddings for AI-powered search

## 🚀 Quick Start (Pick Your Mode)

### Option 1: API Mode - Near Limitless Memory ⭐ Recommended
**Best for:** Heavy users, unified search across everything  
**Cost:** $59-299/month via [memvid.com](https://memvid.com)

```bash
# Install
npm install -g memvid
git clone https://github.com/stackBlock/openclaw-memvid-logger.git
cp -r openclaw-memvid-logger ~/.openclaw/workspace/skills/unified-logger

# Configure
export MEMVID_API_KEY="your_key_here"
export MEMVID_MODE="single"

# Create memory
memvid create ~/memory.mv2

# Start OpenClaw - everything logs to one searchable file
```

**Search everything:**
```bash
memvid ask memory.mv2 "What did we discuss about BadjAI?" --mode sem
memvid ask memory.mv2 "What did the researcher agent find?" --mode sem
memvid ask memory.mv2 "Show me all Python scripts I requested" --mode sem
```

---

### Option 2: Free Mode - 50MB Limit
**Best for:** Testing, light usage, single file  
**Cost:** FREE

```bash
# Install
npm install -g memvid
git clone https://github.com/stackBlock/openclaw-memvid-logger.git
cp -r openclaw-memvid-logger ~/.openclaw/workspace/skills/unified-logger
export MEMVID_MODE="single"

# Create memory
memvid create ~/memory.mv2

# Start OpenClaw
```

**⚠️ Limit:** 50MB (~5,000 conversation turns). When you hit it:
- Archive and start fresh, OR
- Upgrade to API mode, OR  
- Switch to Sharding mode

---

### Option 3: Weekly Sharding - Free Forever (Our Recommended Setup)
**Best for:** Long-term use, staying under free tier, with neural embeddings  
**Cost:** FREE  
**Trade-off:** Multi-file search

```bash
# Install
npm install -g memvid
git clone https://github.com/stackBlock/openclaw-memvid-logger.git
cp -r openclaw-memvid-logger ~/.openclaw/workspace/skills/unified-logger
export MEMVID_MODE="weekly"  # Weekly rotation (safer than monthly)

# Start OpenClaw - auto-creates weekly files with embeddings
```

**How it works:**
- `memory_2026-W09.mv2` (Week 9: Feb 24-Mar 2)
- `memory_2026-W10.mv2` (Week 10: Mar 3-9, auto-created)
- Each file stays well under 50MB
- **Full embeddings enabled** - Neural search works on all conversations

**Why weekly over monthly:**
- Monthly files can approach 50MB too quickly
- Weekly files typically use only 10-20MB
- Safer margin for free tier
- Still manageable (52 files per year)

**Search:**
```bash
# Current week (with semantic/neural search)
memvid ask memory_2026-W09.mv2 "recent discussions" --mode sem

# Specific week
memvid ask memory_2026-W08.mv2 "last week's conversations" --mode sem

# Search all weeks
for file in memory_2026-W*.mv2; do
    echo "=== $file ==="
    memvid ask "$file" "your query" --mode sem 2>/dev/null | head -5
done
```

---

## 🔍 Search Examples

### Neural Search (Semantic Understanding)
```bash
# What you said
memvid ask memory_2026-W09.mv2 "What did I say about the Mercedes?" --mode sem

# What assistant recommended  
memvid ask memory_2026-W09.mv2 "What was your recommendation about Tesla?" --mode sem

# What agents did
memvid ask memory_2026-W09.mv2 "What did the researcher agent find?" --mode sem

# System events
memvid ask memory_2026-W09.mv2 "When did the PowerSchool cron job run?" --mode sem
```

### Keyword Search
```bash
memvid find memory_2026-W09.mv2 --query "Python script" --mode sem
memvid find memory_2026-W09.mv2 --query "Mercedes" --tag agent:researcher --mode sem
```

### Temporal
```bash
memvid when memory_2026-W09.mv2 "yesterday"
memvid when memory_2026-W09.mv2 "last Tuesday"
```

### JSONL Backup
```bash
grep "Mercedes" conversation_log.jsonl
jq 'select(.role_tag == "user")' conversation_log.jsonl
```

---

## 📊 Three Modes Compared

| Feature | API Mode | Free Mode | Weekly Sharding |
|---------|----------|-----------|-----------------|
| **Cost** | $59-299/mo | FREE | FREE |
| **Capacity** | 1GB-25GB+ | 50MB | Unlimited |
| **Files** | 1 | 1 | Weekly files |
| **Unified Search** | ✅ | ✅ | ❌ Per-file |
| **Cross-Context** | ✅ | ✅ | ❌ |
| **Neural Embeddings** | ✅ | ⚠️ Risk | ✅ |
| **Safety Margin** | N/A | Low | High |
| **Best For** | Power users | Testing | Long-term free |

---

## 📁 What Gets Logged

| Source | Tag | Captured |
|--------|-----|----------|
| **Your messages** | `[user]` | ✅ Everything you type |
| **Assistant responses** | `[assistant]` | ✅ Everything assistant says |
| **Sub-agents** | `[agent:researcher]`, `[agent:coder]` | ✅ Agent conversations |
| **Tool calls** | `[tool:exec]`, `[tool:browser]` | ✅ Commands & results |
| **System** | `[system]` | ✅ Cron, heartbeats, events |

---

## 🏗️ Architecture

```
User → OpenClaw → log.py → JSONL (backup)
                         → Memvid .mv2 (search)
```

**Zero data loss:** Every character preserved  
**Instant indexing:** Searchable immediately  
**Crash proof:** Append-only writes  
**Neural embeddings:** Semantic search enabled

---

## ⚙️ Configuration

```bash
# Choose your mode
export MEMVID_MODE="single"    # API or Free mode
export MEMVID_MODE="weekly"    # Sharding mode (recommended)

# Paths
export JSONL_LOG_PATH="~/conversation_log.jsonl"
export MEMVID_PATH="~/memory.mv2"
export MEMVID_BIN="~/.npm-global/bin/memvid"

# For API mode only
export MEMVID_API_KEY="your_key_here"
```

---

## 🆘 Troubleshooting

**"Free tier limit exceeded"**
```bash
# Option 1: Archive and start fresh
mv memory.mv2 memory_archive.mv2
memvid create memory.mv2

# Option 2: Switch to weekly sharding
export MEMVID_MODE="weekly"

# Option 3: Get API key
export MEMVID_API_KEY="your_key"  # $59-299/month at memvid.com
```

**"memvid: command not found"**
```bash
npm install -g memvid
```

**Embeddings not working**
```bash
# Check vector index
memvid stats memory_2026-W09.mv2 | grep "Vector index"
# Should be > 8 bytes (e.g., "80.3 KB")
```

---

## 📚 Documentation

- [SKILL.md](SKILL.md) - Detailed OpenClaw skill documentation
- [Memvid Docs](https://memvid.com/docs) - Memvid CLI reference
- [OpenClaw Docs](https://docs.openclaw.ai) - OpenClaw framework

---

## 🤝 Contributing

1. Fork the repo
2. Create a feature branch
3. Submit a PR

See [CONTRIBUTING.md](CONTRIBUTING.md)

---

## 📄 License

MIT - See [LICENSE](LICENSE)

---

**Made with 🤝 for the OpenClaw community**

- GitHub: [github.com/stackBlock/openclaw-memvid-logger](https://github.com/stackBlock/openclaw-memvid-logger)
- Discord: [discord.com/invite/clawd](https://discord.com/invite/clawd)

**About Memvid:**
> Memvid is a single-file memory layer for AI agents with instant retrieval and long-term memory. 
> Persistent, versioned, and portable memory, without databases.
> 
> Replace complex RAG pipelines with a single portable file you own, and give your agent 
> instant retrieval and long-term memory.
