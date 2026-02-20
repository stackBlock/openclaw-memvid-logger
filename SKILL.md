# Unified Conversation Logger v1.2.0

**Version:** 1.2.0 (Full Context Edition)  
**Author:** AnToni  
**License:** MIT  
**OpenClaw:** >= 2026.2.12

A dual-output conversation logger for OpenClaw that captures **everything** - user messages, assistant responses, sub-agent conversations, tool calls, and system events - to both JSONL (backup) and Memvid (semantic search) formats.

## What's New in v1.2.0

- **Role Tagging:** Distinguishes user, assistant, agent:*, system, and tool messages
- **Full Context:** Captures sub-agent chatter, tool results, background processes
- **Three Storage Modes:** API mode (single file), Free mode (50MB), Sharding mode (monthly rotation)
- **Semantic Search:** Ask "What did the researcher agent find?" or "What did I say about X?"

## Quick Install (Choose Your Mode)

### Option 1: API Mode (Recommended) - Near Limitless Memory
Best for: Heavy users, long-term archives, unified search across everything

```bash
# 1. Get API key from memvid.com ($20/month for 1GB, $59 for 25GB)
export MEMVID_API_KEY="your_api_key_here"
export MEMVID_MODE="single"

# 2. Install
npm install -g @memvid/cli
cp -r unified-logger ~/.openclaw/workspace/skills/

# 3. Create unified memory file
memvid create anthony_memory.mv2

# 4. Start OpenClaw - everything logs to one searchable file
```

**Search everything at once:**
```bash
memvid ask anthony_memory.mv2 "What did we discuss about BadjAI?"
memvid ask anthony_memory.mv2 "What did the researcher agent find about Tesla?"
memvid ask anthony_memory.mv2 "Show me all the Python scripts I asked for"
```

---

### Option 2: Free Mode (50MB Limit) - Complete Memory in One Place
Best for: Testing, light usage, single searchable file

```bash
# 1. Install (no API key needed)
npm install -g @memvid/cli
cp -r unified-logger ~/.openclaw/workspace/skills/
export MEMVID_MODE="single"

# 2. Create memory file
memvid create anthony_memory.mv2

# 3. Start OpenClaw
```

**Limitations:**
- 50MB max (~5,000 conversation turns)
- When you hit limit, you'll need to archive or upgrade
- All searches from one file

**Check usage:**
```bash
memvid stats anthony_memory.mv2
```

---

### Option 3: Sharding Mode - More Than 50MB, Free Forever
Best for: Long-term use, staying under free tier, don't mind multi-file search

```bash
# 1. Install (no API key needed)
npm install -g @memvid/cli
cp -r unified-logger ~/.openclaw/workspace/skills/
export MEMVID_MODE="monthly"  # This is the default

# 2. Start OpenClaw - creates anthony_memory_2026-02.mv2, then 2026-03.mv2, etc.
```

**How it works:**
- New file created each month: `anthony_memory_2026-02.mv2`, `anthony_memory_2026-03.mv2`
- Each file stays under 50MB limit
- Old files remain searchable
- Free forever

**Search across files:**
```bash
# Search current month
memvid ask anthony_memory_2026-02.mv2 "recent discussions"

# Search specific month
memvid ask anthony_memory_2026-01.mv2 "what I said in January"

# Search all months (bash wrapper)
for f in anthony_memory_*.mv2; do
    echo "=== $f ==="
    memvid ask "$f" "your query" 2>/dev/null | head -10
done
```

**Drawbacks:**
- Can't search across months in one query
- Need to know which month to search
- No unified "search everything" view

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

### Natural Language Search

```bash
# What did you say about...?
memvid ask anthony_memory_2026-02.mv2 "What was your recommendation about the Mercedes vs Tesla?"

# What did I ask for...?
memvid ask anthony_memory_2026-02.mv2 "What Python scripts did I request last week?"

# What did agents do...?
memvid ask anthony_memory_2026-02.mv2 "What did the researcher agent find about options trading?"

# System events...?
memvid ask anthony_memory_2026-02.mv2 "When did the PowerSchool grades cron job run?"
```

### Keyword Search

```bash
# Find specific terms
memvid find anthony_memory_2026-02.mv2 --query "Mercedes"

# With filters
memvid find anthony_memory_2026-02.mv2 --query "script" --tag agent:coder
```

### Temporal Queries

```bash
memvid when anthony_memory_2026-02.mv2 "yesterday"
memvid when anthony_memory_2026-02.mv2 "last Tuesday"
memvid when anthony_memory_2026-02.mv2 "3 days ago"
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
| `MEMVID_MODE` | `monthly` | All | `single` or `monthly` |
| `JSONL_LOG_PATH` | `~/conversation_log.jsonl` | All | Backup JSONL file |
| `MEMVID_PATH` | `~/anthony_memory.mv2` | All | Base path for memory files |
| `MEMVID_BIN` | `~/.npm-global/bin/memvid` | All | Path to memvid CLI |

### OpenClaw Hooks (Advanced)

Add to `openclaw.json`:

```json
{
  "hooks": {
    "internal": {
      "enabled": true,
      "entries": {
        "conversation-logger": {
          "enabled": true,
          "command": "python3 ~/.openclaw/workspace/skills/unified-logger/tools/log.py"
        }
      }
    }
  }
}
```

---

## Memory File Formats

### Mode 1: Single File (API or Free Mode)
```
anthony_memory.mv2
├── [user] messages
├── [assistant] responses  
├── [agent:researcher] findings
├── [agent:coder] code
├── [tool:exec] commands
└── [system] events
```

### Mode 2: Sharding (Monthly Rotation)
```
anthony_memory_2026-01.mv2  (January conversations)
anthony_memory_2026-02.mv2  (February conversations) ← Current
anthony_memory_2026-03.mv2  (March, auto-created on March 1)
```

---

## Troubleshooting

### "Free tier limit exceeded" (Free Mode)
You've hit 50MB. Options:
1. **Archive:** Rename file and start fresh: `mv anthony_memory.mv2 anthony_memory_archive.mv2`
2. **Upgrade:** Get API key from memvid.com
3. **Switch modes:** Use monthly sharding instead

### "Cannot find memory file" (Sharding Mode)
Current month's file auto-creates. If missing:
```bash
memvid create anthony_memory_$(date +%Y-%m).mv2
```

### Missing agent conversations
Agents log to their own sessions. Ensure skill is installed in main agent workspace and sub-agents inherit it.

### Search returns wrong speaker
Memvid uses semantic search. Be specific:
- ❌ "Mercedes" → Returns all mentions
- ✅ "What did I say about Mercedes" → Targets [user] frames
- ✅ "Your recommendation about Mercedes" → Targets [assistant] frames

---

## Comparing the Three Modes

| Feature | API Mode | Free Mode | Sharding Mode |
|---------|----------|-----------|---------------|
| **Cost** | $20-59/month | $0 | $0 |
| **Capacity** | 1-25GB | 50MB | Unlimited (files) |
| **Files** | 1 | 1 | Multiple (monthly) |
| **Unified Search** | ✅ Yes | ✅ Yes | ❌ Per-file only |
| **Cross-Month Context** | ✅ Yes | ✅ Yes | ❌ No |
| **Setup Complexity** | Medium | Low | Low |
| **Best For** | Power users | Testing | Long-term free use |

---

## Future Enhancements

- [ ] Auto-archive old months to cold storage
- [ ] Web UI for browsing conversations
- [ ] Cross-file search wrapper script
- [ ] Export to other formats (Markdown, PDF)
- [ ] Conversation threading visualization

---

## Support

- **GitHub Issues:** [github.com/stackBlock/openclaw-memvid-logger](https://github.com/stackBlock/openclaw-memvid-logger)
- **OpenClaw Discord:** [discord.com/invite/clawd](https://discord.com/invite/clawd)
- **Memvid Support:** [memvid.com/docs](https://memvid.com/docs)

## License

MIT - See [LICENSE](LICENSE) file for details.
