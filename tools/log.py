#!/usr/bin/env python3
"""
Unified Conversation Logger for OpenClaw - Weekly Rotation Edition v1.4.0
====================================================================

Logs every conversation turn to both JSONL (backup) and Memvid (searchable memory).
Uses weekly rotation files to stay under free tier limits (safer than monthly).

Features:
- Dual-output logging (JSONL + Memvid)
- Weekly rotation: memory_YYYY-WW.mv2 (ISO week number)
- Role tagging: user, assistant, agent:*, system, tool
- Captures everything: messages, tool calls, agent spawns, background tasks
- Embeddings enabled for neural search

Author: AnToni
Version: 1.4.0 (Weekly Rotation + Embeddings Edition)
License: MIT
"""

import json
import sys
import os
import subprocess
import tempfile
import datetime
import traceback
from datetime import datetime as dt, timezone
from typing import Dict, Optional

# Configuration paths - override with environment variables
# Default paths use user's home directory for portability
HOME_DIR = os.path.expanduser("~")
DEFAULT_WORKSPACE = os.path.join(HOME_DIR, ".openclaw", "workspace")

LOG_PATH = os.environ.get("JSONL_LOG_PATH", 
                          os.path.join(DEFAULT_WORKSPACE, "conversation_log.jsonl"))

# Weekly rotation for Memvid files (stays under 50MB free tier per file)
# Format: memory_YYYY-WW.mv2 where WW is ISO week number (generic, not user-specific)
MEMVID_BASE = os.environ.get("MEMVID_PATH", 
                             os.path.join(DEFAULT_WORKSPACE, "memory.mv2"))
MEMORY_DIR = os.path.dirname(MEMVID_BASE) or DEFAULT_WORKSPACE

# Check for mode: 'single' (one file), 'monthly', or 'weekly' (rotating)
MEMVID_MODE = os.environ.get("MEMVID_MODE", "weekly")  # 'weekly' for safer free tier usage

if MEMVID_MODE == "weekly":
    current_year = dt.now().strftime("%Y")
    current_week = dt.now().isocalendar()[1]
    MEMVID_PATH = os.path.join(MEMORY_DIR, f"memory_{current_year}-W{current_week:02d}.mv2")
elif MEMVID_MODE == "monthly":
    current_month = dt.now().strftime("%Y-%m")
    MEMVID_PATH = os.path.join(MEMORY_DIR, f"memory_{current_month}.mv2")
else:
    MEMVID_PATH = MEMVID_BASE

# Try to find memvid in PATH, fallback to common npm global locations
_MEMVID_PATHS = [
    "/usr/local/bin/memvid",
    "/usr/bin/memvid",
    os.path.expanduser("~/.npm-global/bin/memvid"),
    os.path.expanduser("~/.local/bin/memvid"),
]
_DEFAULT_MEMVID = next((p for p in _MEMVID_PATHS if os.path.exists(p)), "memvid")
MEMVID_BIN = os.environ.get("MEMVID_BIN", _DEFAULT_MEMVID)


VERBOSE_DEBUG = os.environ.get("LOGGER_DEBUG", "0") == "1"

# Telegram notification settings
ALERT_TELEGRAM_TARGET = "telegram:328254434"
ALERT_COOLDOWN_SECONDS = 60  # Don't spam alerts - max 1 per minute
_last_alert_time = None

def send_failure_alert(function_name: str, error_details: str, log_entry: Dict):
    """
    Send Telegram notification when logging fails.
    Uses a cooldown to prevent spam.
    """
    global _last_alert_time
    
    # Cooldown check to prevent spam
    now = dt.now(timezone.utc)
    if _last_alert_time:
        elapsed = (now - _last_alert_time).total_seconds()
        if elapsed < ALERT_COOLDOWN_SECONDS:
            log_debug(f"Alert cooldown active ({elapsed:.0f}s < {ALERT_COOLDOWN_SECONDS}s), skipping notification")
            return
    
    _last_alert_time = now
    
    # Build alert message
    timestamp = now.strftime("%Y-%m-%d %H:%M:%S UTC")
    content_preview = log_entry.get("content", "")[:60].replace('\n', ' ').strip()
    role = log_entry.get("role_tag", "unknown")
    session = log_entry.get("session_id", "unknown")[:8]
    
    # Truncate error details if too long
    if len(error_details) > 200:
        error_details = error_details[:200] + "..."
    
    alert_message = f"""🚨 **Unified Logger FAILURE**

**Time:** {timestamp}
**Function:** `{function_name}`
**Role:** {role}
**Session:** {session}

**Error:**
```
{error_details}
```

**Content Preview:**
"{content_preview}..."

**Status:** ⚠️ Needs investigation
**File:** `{MEMVID_PATH}`"""
    
    try:
        # Parse the target to extract channel type and destination
        # Format: "telegram:328254434"
        if ":" in ALERT_TELEGRAM_TARGET:
            channel_type, destination = ALERT_TELEGRAM_TARGET.split(":", 1)
        else:
            channel_type = "telegram"
            destination = ALERT_TELEGRAM_TARGET
        
        # Use openclaw message tool if available
        result = subprocess.run(
            [
                "openclaw", "message", "send",
                "--channel", channel_type,
                "--target", destination,
                "--message", alert_message
            ],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            log_debug(f"Sent failure alert to Telegram")
        else:
            # Fallback: write to alert log file
            log_debug(f"Failed to send Telegram alert via CLI: {result.stderr}")
            _write_alert_to_file(alert_message)
            
    except Exception as e:
        log_debug(f"Exception sending alert: {e}")
        # Fallback: write to alert log file
        _write_alert_to_file(alert_message)

def _write_alert_to_file(alert_message: str):
    """Write alert to a file as fallback when Telegram fails."""
    try:
        alert_file = os.path.join(MEMORY_DIR, "logger_alerts.log")
        with open(alert_file, "a") as f:
            f.write(f"\n{'='*50}\n")
            f.write(f"Alert at {dt.now(timezone.utc).isoformat()}\n")
            f.write(alert_message)
            f.write("\n")
        log_debug(f"Wrote alert to {alert_file}")
    except Exception as e:
        log_debug(f"Failed to write alert to file: {e}")

def log_debug(msg: str):
    """Log debug message to stderr if VERBOSE_DEBUG is enabled."""
    if VERBOSE_DEBUG:
        print(f"[unified-logger DEBUG] {msg}", file=sys.stderr)
        sys.stderr.flush()

def log_error(msg: str, exc: Exception = None):
    """Log error to stderr with full traceback if available."""
    print(f"[unified-logger ERROR] {msg}", file=sys.stderr)
    if exc:
        print(f"[unified-logger ERROR] Exception: {type(exc).__name__}: {exc}", file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
    sys.stderr.flush()


def ensure_memory_file():
    """Create memory file for current month if it doesn't exist."""
    if not os.path.exists(MEMVID_PATH):
        log_debug(f"Memory file does not exist: {MEMVID_PATH}. Creating...")
        try:
            result = subprocess.run(
                [MEMVID_BIN, "create", MEMVID_PATH],
                capture_output=True,
                text=True,
                timeout=30
            )
            if result.returncode != 0:
                log_error(f"Failed to create memory file: {result.stderr}")
                return False
            log_debug(f"Created memory file: {MEMVID_PATH}")
            return True
        except Exception as e:
            log_error(f"Exception creating memory file", e)
            return False
    return True


def get_role_tag(message: Dict) -> str:
    """
    Generate role tag for frame title.
    
    Roles:
    - user: Human input
    - assistant: Main agent response
    - agent:{name}: Sub-agent (researcher, coder, etc.)
    - system: System events, heartbeats, cron
    - tool: Tool execution results
    """
    raw_role = message.get("role", "unknown")
    
    # Check if this is a sub-agent message
    agent_id = message.get("agent_id") or message.get("subagent_id")
    if agent_id:
        return f"agent:{agent_id}"
    
    # Check source field
    source = message.get("source", "")
    if source.startswith("agent:"):
        return source
    
    # Check for system/cron messages
    msg_type = message.get("type", "")
    if msg_type in ["system", "heartbeat", "cron"]:
        return "system"
    
    # Check for tool results
    if "tool_calls" in message and message.get("tool_result"):
        return "tool"
    
    return raw_role


def get_frame_title(log_entry: Dict) -> str:
    """Build descriptive title for memvid frame."""
    role = log_entry.get("role_tag", "unknown")
    content = log_entry.get("content", "")
    agent_name = log_entry.get("agent_name", "")
    
    # Get preview
    content_preview = content[:80].replace('\n', ' ').strip()
    
    # Build title based on role
    if role == "user":
        return f"[user] {content_preview}..."
    elif role == "assistant":
        return f"[assistant] {content_preview}..."
    elif role.startswith("agent:"):
        agent = role.split(":")[1] if ":" in role else "unknown"
        return f"[agent:{agent}] {content_preview}..."
    elif role == "system":
        return f"[system] {content_preview}..."
    elif role == "tool":
        tool_name = log_entry.get("tool_name", "unknown")
        return f"[tool:{tool_name}] {content_preview}..."
    else:
        return f"[{role}] {content_preview}..."


def build_tags(log_entry: Dict) -> list:
    """Build KEY=VALUE tags for memvid."""
    tags = []
    
    # Role tag
    role = log_entry.get("role_tag", "unknown")
    tags.append(f"role={role}")
    
    # Source tag
    if log_entry.get("source"):
        tags.append(f"source={log_entry.get('source')}")
    
    # Agent tag
    if log_entry.get("agent_id"):
        tags.append(f"agent={log_entry.get('agent_id')}")
    
    # Tool tag
    if log_entry.get("tool_calls"):
        tags.append("has_tools=true")
    
    # Session tag
    session = log_entry.get("session_id", "")[:8]
    if session:
        tags.append(f"session={session}")
    
    # Event type
    if log_entry.get("event_type"):
        tags.append(f"event={log_entry.get('event_type')}")
    
    return tags if tags else ["source=openclaw"]


def log_to_jsonl(log_entry: Dict) -> bool:
    """Append conversation turn to JSONL file."""
    try:
        os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
        with open(LOG_PATH, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
            f.flush()
        return True
    except Exception as e:
        log_error(f"JSONL logging failed", e)
        return False


def log_to_memvid(log_entry: Dict) -> bool:
    """Append conversation turn to Memvid .mv2 file."""
    temp_path = None
    error_context = []  # Collect error details for alert
    
    try:
        # Step 1: Ensure memory file exists
        if not ensure_memory_file():
            error_msg = "Failed to ensure memory file exists"
            log_error(error_msg)
            error_context.append(error_msg)
            send_failure_alert("log_to_memvid (ensure_memory_file)", "\n".join(error_context), log_entry)
            return False
        
        # Step 2: Verify memvid binary exists and is executable
        if not os.path.exists(MEMVID_BIN):
            # Try to find it in PATH
            path_result = subprocess.run(
                ["which", "memvid"],
                capture_output=True,
                text=True
            )
            if path_result.returncode == 0:
                memvid_bin = path_result.stdout.strip()
                log_debug(f"Found memvid in PATH: {memvid_bin}")
            else:
                error_msg = f"Memvid binary not found at {MEMVID_BIN} and not in PATH"
                log_error(error_msg)
                send_failure_alert("log_to_memvid (find_binary)", error_msg, log_entry)
                return False
        else:
            memvid_bin = MEMVID_BIN
            log_debug(f"Using memvid binary: {memvid_bin}")
        
        # Step 3: Create temp file with log entry
        try:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', 
                                             delete=False) as f:
                json.dump(log_entry, f, ensure_ascii=False, indent=2)
                temp_path = f.name
            log_debug(f"Created temp file: {temp_path}")
        except Exception as e:
            error_msg = f"Failed to create temp file: {type(e).__name__}: {e}"
            log_error(f"Failed to create temp file", e)
            send_failure_alert("log_to_memvid (create_temp_file)", error_msg, log_entry)
            return False
        
        # Step 4: Build metadata
        title = get_frame_title(log_entry)
        ts = log_entry.get("timestamp", dt.now(timezone.utc).isoformat())
        date_only = ts.split('T')[0] if 'T' in ts else ts[:10]
        tags = build_tags(log_entry)
        
        log_debug(f"Title: {title}")
        log_debug(f"Date: {date_only}")
        log_debug(f"Tags: {tags}")
        
        # Step 5: Build command with multiple --tag arguments
        # --allow-duplicate required because temp file names can repeat
        # --embedding generates semantic embeddings for neural search
        cmd = [
            memvid_bin, "put", MEMVID_PATH,
            "--title", title,
            "--timestamp", date_only,
            "--input", temp_path,
            "--allow-duplicate",
            "--embedding"
        ]
        for tag in tags:
            cmd.extend(["--tag", tag])
        
        log_debug(f"Command: {' '.join(cmd)}")
        
        # Step 6: Call memvid put
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        log_debug(f"Return code: {result.returncode}")
        log_debug(f"Stdout: {result.stdout}")
        if result.stderr:
            log_debug(f"Stderr: {result.stderr}")
        
        # Clean up temp file
        try:
            os.unlink(temp_path)
        except:
            pass
        
        if result.returncode != 0:
            error_msg = f"Memvid put failed with return code {result.returncode}:\n{result.stderr}"
            log_error(f"Memvid put failed with return code {result.returncode}: {result.stderr}")
            send_failure_alert("log_to_memvid (memvid_put)", error_msg, log_entry)
            return False
        
        log_debug(f"Successfully wrote to memvid: {MEMVID_PATH}")
        return True
        
    except subprocess.TimeoutExpired:
        error_msg = "Memvid put timed out after 30 seconds"
        log_error(error_msg)
        send_failure_alert("log_to_memvid (timeout)", error_msg, log_entry)
        return False
    except Exception as e:
        error_msg = f"Exception in log_to_memvid: {type(e).__name__}: {e}"
        log_error(f"Exception in log_to_memvid", e)
        send_failure_alert("log_to_memvid (exception)", error_msg, log_entry)
        return False
    finally:
        # Ensure temp file is cleaned up
        if temp_path and os.path.exists(temp_path):
            try:
                os.unlink(temp_path)
            except:
                pass


def main():
    """
    Main entry point. Reads message JSON from stdin.
    
    Captures:
    - user: Human messages
    - assistant: Main agent responses  
    - agent:*: Sub-agent conversations (researcher, coder, vision, etc.)
    - system: Heartbeats, cron jobs, system events
    - tool: Tool execution results
    """
    try:
        data = sys.stdin.read()
        if not data:
            log_error("No data read from stdin")
            return
        
        try:
            message = json.loads(data)
        except json.JSONDecodeError as e:
            log_error(f"Failed to parse JSON from stdin: {e}")
            return
        
        # Determine role/tag
        role_tag = get_role_tag(message)
        
        # Build comprehensive log entry
        log_entry = {
            "timestamp": message.get("timestamp", 
                                    dt.now(timezone.utc).isoformat()),
            "session_id": message.get("session_id", "unknown"),
            "role": message.get("role", "unknown"),
            "role_tag": role_tag,
            "content": message.get("content", ""),
            "agent_id": message.get("agent_id") or message.get("subagent_id"),
            "agent_name": message.get("agent_name", ""),
            "tool_calls": message.get("tool_calls", None),
            "tool_name": message.get("tool_name", ""),
            "tool_result": message.get("tool_result", None),
            "source": message.get("source", "openclaw_conversation"),
            "type": message.get("type", "message"),
            "memvid_mode": MEMVID_MODE,
            "memvid_file": MEMVID_PATH,
            "logged_at": dt.now(timezone.utc).isoformat()
        }
        
        # Log to both destinations
        jsonl_ok = log_to_jsonl(log_entry)
        memvid_ok = log_to_memvid(log_entry)
        
        log_debug(f"JSONL: {jsonl_ok}, Memvid: {memvid_ok}, role={role_tag}")
        
    except Exception as e:
        log_error(f"Unhandled exception in main", e)
        sys.exit(0)


if __name__ == "__main__":
    main()
