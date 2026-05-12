#!/bin/bash
# MEMPALACE DIARY HOOK — Force diary save at every session end
#
# Claude Code "Stop" hook. Always blocks once per stop cycle and instructs
# the AI to call mempalace_diary_write before the session ends.
#
# Uses stop_hook_active to prevent an infinite loop:
#   1st stop → block → AI writes diary → 2nd stop → stop_hook_active=true → allow
#
# === INSTALL ===
# Add to ~/.claude/settings.json under "hooks":
#
#   "Stop": [{
#     "hooks": [{
#       "type": "command",
#       "command": "/path/to/mempal_diary_hook.sh",
#       "timeout": 30
#     }]
#   }]

INPUT=$(cat)

STOP_HOOK_ACTIVE=$(python3 -c "
import json, sys
d = json.load(sys.stdin)
sha = d.get('stop_hook_active', False)
print('true' if sha is True or str(sha).lower() in ('true','1','yes') else 'false')
" <<< "$INPUT" 2>/dev/null)

if [ "$STOP_HOOK_ACTIVE" = "true" ]; then
    echo "{}"
    exit 0
fi

cat << 'JSON'
{
  "decision": "block",
  "reason": "Before stopping: call mempalace_diary_write (agent_name=\"claude\") to record this session in AAAK format. Cover: what you worked on, key decisions, outcomes, and anything worth remembering. This is required at the end of every session."
}
JSON
