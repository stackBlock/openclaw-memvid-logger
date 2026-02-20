# Memvid Unified Logger for OpenClaw

[![OpenClaw](https://img.shields.io/badge/OpenClaw->=2026.2.12-blue)](https://openclaw.ai)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Memvid](https://img.shields.io/badge/Memvid-2.0+-green)](https://memvid.com)

> **Never lose a conversation. Search everything you've ever discussed.**

A dual-output conversation logger for [OpenClaw](https://openclaw.ai) that captures **everything** - user messages, assistant responses, sub-agent conversations, tool executions, and system events - to both JSONL (backup) and Memvid (semantic search) formats.

## ✨ What Makes This Different

- **📝 Dual Storage** - Every message saved to JSONL + Memvid simultaneously
- **🔍 Semantic Search** - Ask "What did the researcher agent find about Tesla?" not just keyword search
- **🤖 Full Context** - Captures user input, assistant output, agent chatter, tool results
- **💾 Three Modes** - API (unlimited), Free (50MB), or Sharding (multi-file)
- **🚀 Always On** - Hooks into OpenClaw automatically

## 🚀 Quick Start (Pick Your Mode)

### Option 1: API Mode - Near Limitless Memory ⭐ Recommended
**Best for:** Heavy users, unified search across everything  
**Cost:** $20-59/month via [memvid.com](https://memvid.com)

```bash
# Install
npm install -g @memvid/cli
git clone https://github.com/StackBlock/unified-logger.git
cp -r unified-logger ~/.openclaw/workspace/skills/

# Configure
export MEMVID_API_KEY="your_key_here"
export MEMVID_MODE="single"

# Create memory
memvid create ~/anthony_memory.mv2

# Start OpenClaw - everything logs to one searchable file
```

**Search everything:**
```bash
memvid ask anthony_memory.mv2 "What did we discuss about BadjAI?"
memvid ask anthony_memory.mv2 "What did the researcher agent find?"
memvid ask anthony_memory.mv2 "Show me all Python scripts I requested"
```

---

### Option 2: Free Mode - 50MB Limit
**Best for:** Testing, light usage, single file  
**Cost:** FREE

```bash
# Install
npm install -g @memvid/cli
git clone https://github.com/StackBlock/unified-logger.git
cp -r unified-logger ~/.openclaw/workspace/skills/
export MEMVID_MODE="single"

# Create memory
memvid create ~/anthony_memory.mv2

# Start OpenClaw
```

**⚠️ Limit:** 50MB (~5,000 conversation turns). When you hit it:
- Archive and start fresh, OR
- Upgrade to API mode, OR  
- Switch to Sharding mode

---

### Option 3: Sharding Mode - Free Forever
**Best for:** Long-term use, staying under free tier  
**Cost:** FREE  
**Trade-off:** Multi-file search

```bash
# Install
npm install -g @memvid/cli
git clone https://github.com/StackBlock/unified-logger.git
cp -r unified-logger ~/.openclaw/workspace/skills/
export MEMVID_MODE="monthly"  # Default

# Start OpenClaw - auto-creates monthly files
```

**How it works:**
- `anthony_memory_2026-02.mv2` (February)
- `anthony_memory_2026-03.mv2` (March - auto-created)
- Each file stays under 50MB

**Search per month:**
```bash
memvid ask anthony_memory_2026-02.mv2 "recent discussions"
memvid ask anthony_memory_2026-01.mv2 "January conversations"
```

---

## 🔍 Search Examples

### Natural Language (Semantic)
```bash
# What you said
memvid ask anthony_memory.mv2 "What did I say about the Mercedes?"

# What I recommended  
memvid ask anthony_memory.mv2 "What was your recommendation about Tesla?"

# What agents did
memvid ask anthony_memory.mv2 "What did the researcher agent find about options?"

# System events
memvid ask anthony_memory.mv2 "When did the PowerSchool cron job run?"
```

### Keywords
```bash
memvid find anthony_memory.mv2 --query "Python script"
memvid find anthony_memory.mv2 --query "Mercedes" --tag agent:researcher
```

### Temporal
```bash
memvid when anthony_memory.mv2 "yesterday"
memvid when anthony_memory.mv2 "last Tuesday"
```

### JSONL Backup
```bash
grep "Mercedes" conversation_log.jsonl
jq 'select(.role_tag == "user")' conversation_log.jsonl
```

---

## 📊 Three Modes Compared

| Feature | API Mode | Free Mode | Sharding Mode |
|---------|----------|-----------|---------------|
| **Cost** | $20-59/mo | FREE | FREE |
| **Capacity** | 1-25GB | 50MB | Unlimited |
| **Files** | 1 | 1 | Monthly files |
| **Unified Search** | ✅ | ✅ | ❌ Per-file |
| **Cross-Context** | ✅ | ✅ | ❌ |
| **Best For** | Power users | Testing | Long-term free |

---

## 📁 What Gets Logged

| Source | Tag | Captured |
|--------|-----|----------|
| **Your messages** | `[user]` | ✅ Everything you type |
| **My responses** | `[assistant]` | ✅ Everything I say |
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

---

## ⚙️ Configuration

```bash
# Choose your mode
export MEMVID_MODE="single"    # API or Free mode
export MEMVID_MODE="monthly"   # Sharding mode (default)

# Paths
export JSONL_LOG_PATH="~/conversation_log.jsonl"
export MEMVID_PATH="~/anthony_memory.mv2"
export MEMVID_BIN="~/.npm-global/bin/memvid"

# For API mode only
export MEMVID_API_KEY="your_key_here"
```

---

## 🆘 Troubleshooting

**"Free tier limit exceeded"**
```bash
# Option 1: Archive and start fresh
mv anthony_memory.mv2 anthony_memory_archive.mv2
memvid create anthony_memory.mv2

# Option 2: Switch to monthly sharding
export MEMVID_MODE="monthly"

# Option 3: Get API key
export MEMVID_API_KEY="your_key"
```

**"memvid: command not found"**
```bash
npm install -g @memvid/cli
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

- GitHub: [github.com/StackBlock/unified-logger](https://github.com/StackBlock/unified-logger)
- Discord: [discord.com/invite/clawd](https://discord.com/invite/clawd)
