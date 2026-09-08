#!/bin/sh
# session-log.sh — append session events to an audit log
#
# Reads the hook envelope from stdin and appends a one-line JSON entry
# to ~/.grok/session-audit.log with event name, session ID, cwd, and
# timestamp.

#!/bin/sh
# session-log.sh — append session events to an audit log
#
# Reads the hook envelope from stdin and appends a one-line JSON entry
# to ~/.grok/session-audit.log with event name, session ID, cwd, and
# timestamp.

if [ "${1:-}" = "-h" ] || [ "${1:-}" = "--help" ]; then
  echo "Usage: session-log.sh [--help]"
  echo "Reads a grok hook envelope from stdin. options: --help"
  echo "Appends one JSON line to ~/.grok/session-audit.log"
  exit 0
fi

INPUT=$(cat)

EVENT=$(echo "$INPUT" | grep -o '"hookEventName":"[^"]*"' | sed 's/"hookEventName":"//;s/"$//')
SESSION=$(echo "$INPUT" | grep -o '"sessionId":"[^"]*"' | sed 's/"sessionId":"//;s/"$//')
CWD=$(echo "$INPUT" | grep -o '"cwd":"[^"]*"' | sed 's/"cwd":"//;s/"$//')
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

LOG_FILE="${HOME}/.grok/session-audit.log"
mkdir -p "$(dirname "$LOG_FILE")"

echo "{\"timestamp\":\"${TIMESTAMP}\",\"event\":\"${EVENT}\",\"session\":\"${SESSION}\",\"cwd\":\"${CWD}\"}" >> "$LOG_FILE"