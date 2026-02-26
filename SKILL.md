# Unified Conversation Logger v1.4.0

**Version:** 1.4.0 (Weekly Rotation + Embeddings Edition)  
**Author:** AnToni (based on work by stackBlock)  
**License:** MIT  
**OpenClaw:** >= 2026.2.12

A dual-output conversation logger for OpenClaw that captures **everything** - user messages, assistant responses, sub-agent conversations, tool calls, and system events - to both JSONL (backup) and Memvid (semantic search) formats.

> **Memvid**: A single-file memory layer for AI agents with instant retrieval and long-term memory. Persistent, versioned, and portable memory, without databases.
>
> *"Replace complex RAG pipelines with a single portable file you own, and give your agent instant retrieval and long-term memory."*

---

## ⚠️ Security & Privacy Notice

**Before installing, please understand:**

This skill captures **everything** - by design. It logs all user messages, assistant responses, sub-agent conversations, tool outputs, and system events to local files. This enables powerful long-term memory but requires trust.

**What you should know:**
- **Broad capture scope:** This is intentional - the skill's purpose is complete conversation logging
- **Sensitive data risk:** Tool outputs (commands, API responses, file contents) are logged. Review what tools expose.
- **Continuous logging:** Once installed, it runs automatically on every assistant response until removed
- **Optional cloud mode:** API mode with `MEMVID_API_KEY` sends data to memvid.com (third-party service). Free/local modes keep data on your machine only.
- **Your responsibility:** Secure the JSONL/.mv2 files, rotate logs regularly, and audit what gets captured.

**Mitigations available:**
- Use **Free/Sharding mode** to keep data local (no API key needed)
- Change default paths to encrypted locations
- Review `tools/log.py` before installing to understand exactly what gets logged
- File permissions: restrict access to log files (`chmod 600`)

**This skill is for users who want complete conversation memory and accept the privacy trade-offs.**

---

## ✨ What Makes This Different

- **📝 Dual Storage** - Every message saved to JSONL + Memvid simultaneously
- **🔍 Semantic Search** - Ask "What did the researcher agent find about Tesla?" not just keyword search
- **🤖 Full Context** - Captures user input, assistant output, agent chatter, tool results
- **💾 Three Modes** - API (unlimited), Free (50MB), or Sharding (multi-file)
- **🚀 Always On** - Hooks into OpenClaw automatically
- **📅 Weekly Rotation** - Safer free tier usage with automatic weekly file rotation
- **🧠 Embeddings** - Full semantic embeddings for neural search

## What's New in v1.4.0

### Major Changes
- **Weekly Rotation Mode:** Changed from monthly to weekly file rotation
  - **Why:** Monthly files can approach 50MB limit too quickly
  - **Format:** `memory_YYYY-WW.mv2` (e.g., `memory_2026-W09.mv2`)
  - **Benefit:** Each week starts fresh, stays well under free tier limit
  - **Embeddings:** Full semantic embeddings enabled for neural search

### Previous: v1.3.1
- **Memvid Duplicate URI Fix:** Added `--allow-duplicate` flag
- **Failure Alerts:** Telegram notifications when logging fails
- **Tag Format:** KEY=VALUE format for Memvid 2.0+

### Compatibility
- Verified with OpenClaw 2026.2.12
- Verified with Memvid CLI 2.0+

---

## Quick Install (Choose Your Mode)

### Option 1: API Mode (Recommended) - Near Limitless Memory
**Best for:** Heavy users, unified search across everything  
**Cost:** $59-299/month via [memvid.com](https://memvid.com)

```bash
# 1. Get API key from memvid.com ($59/month for 1GB, $299 for 25GB)
export MEMVID_API_KEY="your_api_key_here"
export MEMVID_MODE="single"

# 2. Install
npm install -g memvid
git clone https://github.com/stackBlock/openclaw-memvid-logger.git
cp -r openclaw-memvid-logger ~/.openclaw/workspace/skills/unified-logger

# 3. Create unified memory file
memvid create ~/memory.mv2

# 4. Start OpenClaw - everything logs to one searchable file
```

**Search everything at once:**
```bash
memvid ask memory.mv2 "What did we discuss about BadjAI?"
memvid ask memory.mv2 "What did the researcher agent find about Tesla?"
memvid ask memory.mv2 "Show me all the Python scripts I asked for"
```

---

### Option 2: Free Mode (50MB Limit) - Complete Memory in One Place
**Best for:** Testing, light usage, single searchable file  
**Cost:** FREE

```bash
# 1. Install (no API key needed)
npm install -g memvid
git clone https://github.com/stackBlock/openclaw-memvid-logger.git
cp -r openclaw-memvid-logger ~/.openclaw/workspace/skills/unified-logger
export MEMVID_MODE="single"

# 2. Create memory file
memvid create ~/memory.mv2

# 3. Start OpenClaw
```

**⚠️ Limit:** 50MB (~5,000 conversation turns). When you hit it:
- Archive and start fresh, OR
- Upgrade to API mode ($59-299/month), OR  
- Switch to Sharding mode

---

### Option 3: Sharding Mode - Free Forever (Our Recommended Free Setup)
**Best for:** Long-term use, staying under free tier, weekly rotation  
**Cost:** FREE  
**Trade-off:** Multi-file search (but we use weekly rotation for safety)

```bash
# 1. Install (no API key needed)
npm install -g memvid
git clone https://github.com/stackBlock/openclaw-memvid-logger.git
cp -r openclaw-memvid-logger ~/.openclaw/workspace/skills/unified-logger
export MEMVID_MODE="weekly"  # Weekly rotation (recommended over monthly)

# 2. Start OpenClaw - auto-creates weekly files with embeddings
```

**How it works:**
- `memory_2026-W09.mv2` (Week 9 - Feb 24-Mar 2)
- `memory_2026-W10.mv2` (Week 10 - Mar 3-9, auto-created)
- Each file stays well under 50MB
- **Embeddings enabled** - Full neural search on all conversations

**Why weekly over monthly:**
- Monthly files can hit 50MB limit
- Weekly files typically use only 10-20MB
- Safer margin for free tier
- Still easy to search (just 52 files per year vs 12)

**Search:**
```bash
# Current week
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

## What Gets Logged

### Role Tags (Automatic)

| Role | Tag | Example Search |
|------|-----|----------------|
| **User** | `[user]` | "What did **I** say about Mercedes?" |
| **Assistant** | `[assistant]` | "What did **you** recommend?" |
| **Sub-agents** | `[agent:researcher]`, `[agent:coder]` | "What did the **researcher** find?" |
| **System** | `[system]` | "When did the **cron job** run?" |
| **Tools** | `[tool:exec]`, `[tool:browser]` | "What **commands** were run?" |

### Everything Captured

- ✅ User messages (what you type)
- ✅ Assistant responses (what I say back)
- ✅ Sub-agent conversations (researcher, coder, vision, math, etc.)
- ✅ Tool executions (bash commands, browser actions, file edits)
- ✅ Background processes (cron jobs, heartbeats, scheduled tasks)
- ✅ System events (config changes, restarts, errors)

---

## Architecture

```
┌─────────────────────────────────────────┐
│           OpenClaw Ecosystem            │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐ │
│  │  User   │  │Assistant│  │  Agents │ │
│  │ Messages│  │Responses│  │Research │ │
│  └────┬────┘  └────┬────┘  └────┬────┘ │
│       └─────────────┴─────────────┘     │
│                     │                   │
│              ┌──────▼──────┐            │
│              │  log.py     │            │
│              │  (this skill)│           │
│              └──────┬──────┘            │
└─────────────────────┼───────────────────┘
                      │
    ┌─────────────────┼─────────────────┐
    ↓                 ↓                 ↓
┌───────┐      ┌─────────────┐    ┌──────────┐
│ JSONL │      │   Memvid    │    │  Search  │
│ File  │      │   Files     │    │  Query   │
└───────┘      └─────────────┘    └──────────┘
    │                 │
    ↓                 ↓
 grep/jq       memvid ask/find
```

---

## Usage Examples

### Natural Language Search (Neural Mode)

```bash
# What did you say about...?
memvid ask memory_2026-W09.mv2 "What was your recommendation about the Mercedes?" --mode sem

# What did I ask for...?
memvid ask memory_2026-W09.mv2 "What Python scripts did I request?" --mode sem

# What did agents do...?
memvid ask memory_2026-W09.mv2 "What did the researcher agent find?" --mode sem

# System events...?
memvid ask memory_2026-W09.mv2 "When did the PowerSchool cron job run?" --mode sem
```

### Keyword Search

```bash
# Find specific terms
memvid find memory_2026-W09.mv2 --query "Mercedes" --mode sem

# With filters
memvid find memory_2026-W09.mv2 --query "script" --tag agent:coder --mode sem
```

### Temporal Queries

```bash
memvid when memory_2026-W09.mv2 "yesterday"
memvid when memory_2026-W09.mv2 "last Tuesday"
memvid when memory_2026-W09.mv2 "3 days ago"
```

### JSONL Backup

```bash
# Quick grep
grep "Mercedes" conversation_log.jsonl

# Complex queries with jq
jq 'select(.role_tag == "user" and .content | contains("Python"))' conversation_log.jsonl

# Time range
jq 'select(.timestamp >= "2026-02-01" and .timestamp < "2026-03-01")' conversation_log.jsonl
```

---

## Configuration

### Environment Variables

| Variable | Default | Mode | Description |
|----------|---------|------|-------------|
| `MEMVID_API_KEY` | (none) | API | Your memvid.com API key |
| `MEMVID_MODE` | `weekly` | All | `single`, `monthly`, or `weekly` |
| `JSONL_LOG_PATH` | `~/workspace/conversation_log.jsonl` | All | Backup log file |
| `MEMVID_PATH` | `~/workspace/memory.mv2` | All | Base path for memory files |
| `MEMVID_BIN` | `~/.npm-global/bin/memvid` | All | Path to memvid CLI |

### Setting Environment Variables

Add to `/etc/environment` (required for background services):

```bash
# Weekly rotation (recommended for free tier)
export MEMVID_MODE="weekly"
export JSONL_LOG_PATH="/home/anthony/.openclaw/workspace/conversation_log.jsonl"
export MEMVID_PATH="/home/anthony/.openclaw/workspace/memory.mv2"
export MEMVID_BIN="/home/anthony/.npm-global/bin/memvid"
```

Then reload:
```bash
source /etc/environment
# Or restart your session
```

---

## Memory File Formats

### Mode 1: Single File (API or Free Mode)
```
memory.mv2
├── [user] messages
├── [assistant] responses  
├── [agent:researcher] findings
├── [agent:coder] code
├── [tool:exec] commands
└── [system] events
```

### Mode 2: Sharding (Weekly Rotation - Recommended)
```
memory_2026-W09.mv2  (Week 9: Feb 24-Mar 2) ← Current
memory_2026-W10.mv2  (Week 10: Mar 3-9)
memory_2026-W11.mv2  (Week 11: Mar 10-16)
```

---

## Troubleshooting

### "Free tier limit exceeded" (Free Mode)
```bash
# Option 1: Archive and start fresh
mv memory.mv2 memory_archive.mv2
memvid create memory.mv2

# Option 2: Switch to weekly sharding
export MEMVID_MODE="weekly"

# Option 3: Get API key
export MEMVID_API_KEY="your_key"  # $59-299/month at memvid.com
```

### "Cannot find memory file" (Sharding Mode)
Current week's file auto-creates. If missing:
```bash
memvid create memory_$(date +%Y-W%V).mv2
```

### Missing agent conversations
Agents log to their own sessions. Ensure skill is installed in main agent workspace and sub-agents inherit it.

### Search returns wrong speaker
Memvid uses semantic search. Be specific:
- ❌ "Mercedes" → Returns all mentions
- ✅ "What did I say about Mercedes" → Targets [user] frames
- ✅ "Your recommendation about Mercedes" → Targets [assistant] frames

### Embeddings not working
Check vector index size:
```bash
memvid stats memory_2026-W09.mv2 | grep "Vector index"
```
Should show > 8 bytes. If 8 bytes, the `--embedding` flag may not be set.

---

## Comparing the Three Modes

| Feature | API Mode | Free Mode | Weekly Sharding |
|---------|----------|-----------|-----------------|
| **Cost** | $59-299/mo | FREE | FREE |
| **Capacity** | 1GB-25GB+ | 50MB | Unlimited (files) |
| **Files** | 1 | 1 | Weekly files |
| **Unified Search** | ✅ Yes | ✅ Yes | ❌ Per-file |
| **Cross-Context** | ✅ Yes | ✅ Yes | ❌ Week isolated |
| **Embeddings** | ✅ Yes | ⚠️ Risk of filling | ✅ Yes |
| **Safety Margin** | N/A | Low (50MB max) | High (new file weekly) |
| **Best For** | Power users | Testing | Long-term free use |

---

## Real-World Usage (Our Setup)

We use **Weekly Sharding Mode** with **embeddings enabled**:

```bash
# Environment
export MEMVID_MODE="weekly"
export MEMVID_PATH="/home/anthony/.openclaw/workspace/memory.mv2"

# Results
# - Week 9 file: memory_2026-W09.mv2
# - Size: ~5-10 MB per week (well under 50MB)
# - Embeddings: 80+ KB vector index
# - Search: Neural semantic search works perfectly
```

This gives us:
- ✅ Free tier safe (never hits 50MB)
- ✅ Full semantic embeddings
- ✅ Neural search capability
- ✅ 52 files per year (manageable)
- ✅ No data loss

---

## Future Enhancements

- [ ] Auto-archive old weeks to cold storage
- [ ] Web UI for browsing conversations
- [ ] Cross-file search wrapper script
- [ ] Export to other formats (Markdown, PDF)
- [ ] Conversation threading visualization
- [ ] Compression options for older files

---

## Support

- **GitHub Issues:** [github.com/stackBlock/openclaw-memvid-logger](https://github.com/stackBlock/openclaw-memvid-logger)
- **OpenClaw Discord:** [discord.com/invite/clawd](https://discord.com/invite/clawd)
- **Memvid Support:** [memvid.com/docs](https://memvid.com/docs)

## License

MIT - See [LICENSE](LICENSE)

---

**About Memvid:**
> Memvid is a single-file memory layer for AI agents with instant retrieval and long-term memory. 
> Persistent, versioned, and portable memory, without databases.
> 
> Replace complex RAG pipelines with a single portable file you own, and give your agent 
> instant retrieval and long-term memory.
