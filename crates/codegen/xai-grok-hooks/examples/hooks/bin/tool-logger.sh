#!/usr/bin/env bash
# -----------------------------------------------------------------------------
# Goal     : Append one JSON line per tool call to a local activity log.
# Purpose  : Example grok hook — read hook envelope from stdin and record
#             event name, resolved toolName, timestamp under ~/.grok/.
# Consumers: grok hook runner; complete-e2e CLI contract (--help).
# Inputs   : --help | hook JSON on stdin.
# Outputs  : usage/help on --help; append-only log line.
# Exit codes: 0 success or --help
# Side effects: creates ~/.grok/tool-activity.log if missing.
# [ai] Revised: --help before cat so fleet-all iterator stdin is not drained.
# -----------------------------------------------------------------------------
set -uo pipefail

for _arg in "$@"; do
	case "$_arg" in
		-h | --help)
			echo "usage: tool-logger.sh [--help]"
			echo "help: reads hook JSON on stdin; appends tool activity log"
			exit 0
			;;
	esac
done

INPUT=$(cat)

EVENT=$(echo "$INPUT" | grep -o '"hookEventName":"[^"]*"' | sed 's/"hookEventName":"//;s/"$//' || true)
TOOL=$(echo "$INPUT" | grep -o '"toolName":"[^"]*"' | head -1 | sed 's/"toolName":"//;s/"$//' || true)
BACKGROUNDED=$(echo "$INPUT" | grep -o '"isBackgrounded":[a-z]*' | sed 's/"isBackgrounded"://' || true)
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

LOG_FILE="${HOME}/.grok/tool-activity.log"
mkdir -p "$(dirname "$LOG_FILE")"

echo "{\"timestamp\":\"${TIMESTAMP}\",\"event\":\"${EVENT}\",\"tool\":\"${TOOL}\",\"backgrounded\":${BACKGROUNDED:-false}}" >>"$LOG_FILE"
exit 0
