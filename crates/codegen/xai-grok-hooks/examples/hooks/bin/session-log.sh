#!/usr/bin/env bash
# -----------------------------------------------------------------------------
# Goal     : Append one JSON line per hook event to a local session audit log.
# Purpose  : Example grok hook — read hook envelope from stdin and record
#             event name, session ID, cwd, timestamp under ~/.grok/.
# Consumers: grok hook runner; complete-e2e CLI contract (--help).
# Inputs   : --help | hook JSON on stdin.
# Outputs  : usage/help on --help; append-only log line.
# Exit codes: 0 success or --help
# Side effects: creates ~/.grok/session-audit.log if missing.
# [ai] Revised: --help before cat so fleet-all iterator stdin is not drained.
# -----------------------------------------------------------------------------
set -uo pipefail

for _arg in "$@"; do
	case "$_arg" in
		-h | --help)
			echo "usage: session-log.sh [--help]"
			echo "help: reads hook JSON on stdin; appends session audit log"
			exit 0
			;;
	esac
done

INPUT=$(cat)

EVENT=$(echo "$INPUT" | grep -o '"hookEventName":"[^"]*"' | sed 's/"hookEventName":"//;s/"$//' || true)
SESSION=$(echo "$INPUT" | grep -o '"sessionId":"[^"]*"' | sed 's/"sessionId":"//;s/"$//' || true)
CWD=$(echo "$INPUT" | grep -o '"cwd":"[^"]*"' | sed 's/"cwd":"//;s/"$//' || true)
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

LOG_FILE="${HOME}/.grok/session-audit.log"
mkdir -p "$(dirname "$LOG_FILE")"

echo "{\"timestamp\":\"${TIMESTAMP}\",\"event\":\"${EVENT}\",\"session\":\"${SESSION}\",\"cwd\":\"${CWD}\"}" >>"$LOG_FILE"
exit 0
