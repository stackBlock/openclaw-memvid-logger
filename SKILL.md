# Unified Conversation Logger

**Version:** 1.0.0  
**Author:** AnToni  
**License:** MIT  
**OpenClaw:** >= 2026.2.12

A dual-output conversation logger for OpenClaw that captures every message to both JSONL (backup) and Memvid (semantic search) formats.

## Overview

This skill hooks into OpenClaw's message flow and preserves every conversation turn with:
- **Zero data loss** - Raw text only, no summarization
- **Dual storage** - JSONL for grep/jq, Memvid for semantic search
- **Instant searchability** - Every message indexed as it's spoken
- **Crash resilience** - Append-only writes, survives `/new` and restarts

## Installation

### 1. Install Memvid CLI

```bash
npm install -g @memvid/cli
```

### 2. Install Skill

```bash
# Clone or copy to OpenClaw skills directory
cp -r unified-logger ~/.openclaw/workspace/skills/

# Or use clawhub (when published)
clawhub install unified-logger
```

### 3. Configure (Optional)

Set environment variables or accept defaults:

```bash
export JSONL_LOG_PATH="/home/anthony/.openclaw/workspace/conversation_log.jsonl"
export MEMVID_PATH="/home/anthony/.openclaw/workspace/anthony_memory.mv2"
export MEMVID_BIN="/home/anthony/.npm-global/bin/memvid"
```

### 4. Initialize Memory File

```bash
memvid create $MEMVID_PATH
```

## Architecture

```
┌─────────────────┐
│  OpenClaw Chat  │
└────────┬────────┘
         │
    ┌────▼────┐
    │ log.py  │
    └────┬────┘
         │
    ┌────┴────┐
    ↓         ↓
┌───────┐  ┌─────────┐
│ JSONL │  │ Memvid  │
│ Backup│  │ Search  │
└───────┘  └─────────┘
    │          │
    ↓          ↓
 grep/jq   memvid ask
```

## Usage

### Search Your Conversations

**Semantic search (natural language):**
```bash
memvid ask anthony_memory.mv2 "What did we discuss about BadjAI?"
```

**Keyword search:**
```bash
memvid find anthony_memory.mv2 --query "Mercedes car decision"
```

**Temporal queries:**
```bash
memvid when anthony_memory.mv2 "yesterday"
memvid when anthony_memory.mv2 "last Tuesday"
```

**JSONL grep (backup):**
```bash
grep "Mercedes" conversation_log.jsonl
jq 'select(.role == "user")' conversation_log.jsonl
```

### Memory Maintenance

**Check status:**
```bash
memvid stats anthony_memory.mv2
```

**Expand capacity (self-hosted):**
```bash
memvid tickets issue anthony_memory.mv2 \
    --issuer self-hosted \
    --seq 2 \
    --capacity 1073741824  # 1GB
```

**Vacuum and rebuild indexes:**
```bash
memvid doctor anthony_memory.mv2 --vacuum
```

## Log Format

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

Each turn becomes a searchable frame with:
- **Title:** `[user] What about the Mercedes?...`
- **Timestamp:** Date extracted from message
- **Content:** Full JSON of the log entry
- **Tags:** Auto-extracted from content

## Configuration

### OpenClaw Hooks (Advanced)

To enable via `openclaw.json`:

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

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `JSONL_LOG_PATH` | `~/workspace/conversation_log.jsonl` | Backup log file |
| `MEMVID_PATH` | `~/workspace/anthony_memory.mv2` | Searchable memory file |
| `MEMVID_BIN` | `~/.npm-global/bin/memvid` | Path to memvid CLI |

## Memvid Integration

This skill requires a Memvid account for memories over 50MB:

### Free Tier (50MB)
- Perfect for testing
- ~5,000 conversation turns
- No API key required

### Paid Plans
- **1GB:** $20/month - ~100,000 turns
- **10GB:** $50/month - ~1M turns
- **Unlimited:** Custom pricing

Sign up at [memvid.com](https://memvid.com)

## Troubleshooting

### "Free tier limit exceeded"
Your memory file is over 50MB. Options:
1. Archive old conversations to new file
2. Upgrade to paid Memvid plan
3. Use JSONL-only mode (modify log.py)

### "memvid: command not found"
Install the CLI:
```bash
npm install -g @memvid/cli
```

### Missing conversations in search
Memvid indexes are eventually consistent. Run:
```bash
memvid doctor anthony_memory.mv2 --rebuild-lex-index
```

## Future Enhancements

- [ ] Automatic rotation when memory reaches capacity
- [ ] Configurable filtering (exclude certain sessions)
- [ ] Compression for older frames
- [ ] Multi-user support
- [ ] Web UI for browsing conversations

## Related Skills

- **jsonl-logger** - Simpler version, JSONL only
- **memvid-query** - Advanced search tools (planned)
- **conversation-export** - Export to other formats (planned)

## Support

- GitHub Issues: [github.com/openclaw/unified-logger](https://github.com/openclaw/unified-logger)
- OpenClaw Discord: [discord.com/invite/clawd](https://discord.com/invite/clawd)
- Memvid Docs: [memvid.com/docs](https://memvid.com/docs)

## License

MIT - See LICENSE file for details.
