#!/usr/bin/env python3
"""
Unified Conversation Logger for OpenClaw
=====================================

Logs every conversation turn to both JSONL (backup) and Memvid (searchable memory).
Part of the OpenClaw skills ecosystem.

Author: AnToni
Version: 1.0.0
License: MIT
"""

import json
import sys
import os
import subprocess
import tempfile
from datetime import datetime, timezone

# Configuration paths - override with environment variables
LOG_PATH = os.environ.get("JSONL_LOG_PATH", 
                          "/home/anthony/.openclaw/workspace/conversation_log.jsonl")
MEMVID_PATH = os.environ.get("MEMVID_PATH", 
                             "/home/anthony/.openclaw/workspace/anthony_memory.mv2")
MEMVID_BIN = os.environ.get("MEMVID_BIN", 
                            "/home/anthony/.npm-global/bin/memvid")


def log_to_jsonl(log_entry: dict) -> bool:
    """
    Append conversation turn to JSONL file.
    
    Args:
        log_entry: Dictionary containing timestamp, role, content, etc.
        
    Returns:
        True if successful, False otherwise
    """
    try:
        os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
        with open(LOG_PATH, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
            f.flush()
        return True
    except Exception as e:
        print(f"[jsonl-logger error] {e}", file=sys.stderr)
        return False


def log_to_memvid(log_entry: dict) -> bool:
    """
    Append conversation turn to Memvid .mv2 file for semantic search.
    
    Args:
        log_entry: Dictionary containing timestamp, role, content, etc.
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Create temp file with the entry content
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', 
                                         delete=False) as f:
            json.dump(log_entry, f, ensure_ascii=False, indent=2)
            temp_path = f.name
        
        # Build title from role and content preview
        role = log_entry.get("role", "unknown")
        content = log_entry.get("content", "")
        content_preview = content[:60].replace('\n', ' ').strip()
        title = f"[{role}] {content_preview}..."
        
        # Format timestamp for memvid (YYYY-MM-DD)
        ts = log_entry.get("timestamp", 
                          datetime.now(timezone.utc).isoformat())
        date_only = ts.split('T')[0] if 'T' in ts else ts[:10]
        
        # Call memvid put to append frame
        result = subprocess.run(
            [
                MEMVID_BIN, "put", MEMVID_PATH,
                "--title", title,
                "--timestamp", date_only,
                "--input", temp_path
            ],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        # Clean up temp file
        os.unlink(temp_path)
        
        if result.returncode == 0:
            return True
        else:
            # Memvid errors are common (size limits, etc) - don't spam stderr
            return False
            
    except Exception as e:
        # Silent fail - don't break the conversation
        return False


def main():
    """
    Main entry point. Reads message JSON from stdin, logs to both destinations.
    
    Expected input format from OpenClaw:
    {
        "timestamp": "2026-02-19T13:20:00Z",
        "session_id": "abc123",
        "role": "user" | "assistant",
        "content": "message text",
        "tool_calls": [...] | null
    }
    """
    try:
        data = sys.stdin.read()
        if not data:
            return
            
        message = json.loads(data)
        
        # Build standardized log entry
        log_entry = {
            "timestamp": message.get("timestamp", 
                                    datetime.now(timezone.utc).isoformat()),
            "session_id": message.get("session_id", "unknown"),
            "role": message.get("role", "unknown"),
            "content": message.get("content", ""),
            "tool_calls": message.get("tool_calls", None),
            "source": "openclaw_conversation",
            "logged_at": datetime.now(timezone.utc).isoformat()
        }
        
        # Log to both destinations (JSONL always, Memvid best-effort)
        log_to_jsonl(log_entry)
        log_to_memvid(log_entry)
        
    except Exception as e:
        # Never fail the conversation due to logging errors
        print(f"[logger error] {e}", file=sys.stderr)
        sys.exit(0)


if __name__ == "__main__":
    main()
