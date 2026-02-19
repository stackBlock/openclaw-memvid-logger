# Unified Logger for OpenClaw

[![OpenClaw](https://img.shields.io/badge/OpenClaw->=2026.2.12-blue)](https://openclaw.ai)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Memvid](https://img.shields.io/badge/Memvid-2.0+-green)](https://memvid.com)

> Never lose a conversation. Search everything you've ever discussed.

A dual-output conversation logger for [OpenClaw](https://openclaw.ai) that captures every message to both **JSONL** (backup) and **Memvid** (semantic search) formats.

## ✨ Features

- **📝 Dual Storage** - Every message saved to JSONL + Memvid simultaneously
- **🔍 Instant Search** - Natural language queries across all conversations
- **💾 Zero Data Loss** - Raw text only, no summarization
- **🚀 Always On** - Hooks into OpenClaw automatically, survives restarts
- **🔒 Privacy First** - Self-hosted, your data stays local

## 🚀 Quick Start

```bash
# 1. Install dependencies
npm install -g @memvid/cli

# 2. Create your memory file
memvid create ~/anthony_memory.mv2

# 3. Install this skill
cp -r unified-logger ~/.openclaw/workspace/skills/

# 4. Start chatting - every message is now logged!
```

## 🔍 Search Your Memories

```bash
# Ask natural language questions
memvid ask anthony_memory.mv2 "What car did I decide to buy?"

# Keyword search
memvid find anthony_memory.mv2 --query "options trading strategy"

# Temporal queries
memvid when anthony_memory.mv2 "last Tuesday"

# Grep the JSONL backup
grep "Mercedes" conversation_log.jsonl
jq 'select(.timestamp >= "2026-02-01")' conversation_log.jsonl
```

## 📁 Architecture

```
┌─────────────────┐
│  OpenClaw Chat  │
└────────┬────────┘
         │
    ┌────▼────┐
    │ log.py  │  ← Hooks into message flow
    └────┬────┘
         │
    ┌────┴────┐
    ↓         ↓
┌───────┐  ┌─────────┐
│ JSONL │  │ Memvid  │
│ File  │  │ .mv2    │
└───────┘  └─────────┘
```

| Feature | JSONL | Memvid |
|---------|-------|--------|
| **Speed** | Instant append | ~100ms per frame |
| **Search** | grep/jq | Semantic + lexical |
| **Size** | ~1KB per turn | ~500B compressed |
| **Portability** | Universal | Memvid CLI required |
| **Limits** | Disk only | 50MB free tier |

## ⚙️ Configuration

Set environment variables (optional):

```bash
export JSONL_LOG_PATH="~/conversation_log.jsonl"
export MEMVID_PATH="~/anthony_memory.mv2"
export MEMVID_BIN="~/.npm-global/bin/memvid"
```

## 💡 Use Cases

- **Project Continuity** - "What did we decide about the database schema?"
- **Code Archaeology** - "Show me that Python script from last week"
- **Decision Tracking** - "Why did we choose PostgreSQL over MySQL?"
- **Knowledge Base** - Build a searchable archive of everything learned

## 📋 Log Format

### JSONL Entry
```jsonl
{
  "timestamp": "2026-02-19T18:30:00Z",
  "session_id": "abc123",
  "role": "user",
  "content": "What about the Mercedes?",
  "tool_calls": null,
  "source": "openclaw_conversation",
  "logged_at": "2026-02-19T18:30:01Z"
}
```

### Memvid Frame
- **Title:** `[user] What about the Mercedes?...`
- **Timestamp:** Date extracted from message
- **Content:** Full JSON of the log entry
- **Tags:** Auto-extracted from content

## 🔧 Maintenance

```bash
# Check memory status
memvid stats anthony_memory.mv2

# Expand capacity (self-hosted)
memvid tickets issue anthony_memory.mv2 \
    --issuer self-hosted \
    --seq 2 \
    --capacity 1073741824  # 1GB

# Rebuild indexes
memvid doctor anthony_memory.mv2 --vacuum --rebuild-lex-index
```

## 🐛 Troubleshooting

**"Free tier limit exceeded"**
Your memory is >50MB. Options:
- Archive to new file: `memvid create memory_2026_02.mv2`
- Upgrade at [memvid.com/pricing](https://memvid.com/pricing)

**"memvid: command not found"**
```bash
npm install -g @memvid/cli
```

## 📦 Requirements

- OpenClaw >= 2026.2.12
- Python 3.8+
- Memvid CLI >= 2.0
- Memvid account (free tier: 50MB ≈ 5,000 turns)

## 🤝 Contributing

1. Fork this template repository
2. Create a feature branch
3. Submit a PR

## 📄 License

MIT - See [LICENSE](LICENSE)

## 🔗 Related

- [OpenClaw](https://openclaw.ai) - The AI assistant framework
- [Memvid](https://memvid.com) - Portable memory system
- [OpenClaw Skills](https://clawhub.com) - More skills

---

**Made with 🤝 for the OpenClaw community**
