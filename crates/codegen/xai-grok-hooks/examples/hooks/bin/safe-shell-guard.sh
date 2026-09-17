#!/usr/bin/env bash
# -----------------------------------------------------------------------------
# Goal     : Deny obviously destructive shell commands at PreToolUse.
# Purpose  : Example grok hook — read PreToolUse JSON on stdin, extract
#             toolInput.command, match a blocklist, emit allow/deny JSON.
# Consumers: grok hook runner; complete-e2e CLI contract (--help).
# Inputs   : --help | PreToolUse JSON on stdin.
# Outputs  : usage/help on --help; {"decision":"..."} JSON on stdout.
# Exit codes: 0 allow or --help / 2 deny
# Side effects: none (stdin only; no files).
# [ai] Revised: --help before cat so fleet-all iterator stdin is not drained.
# -----------------------------------------------------------------------------
set -uo pipefail

for _arg in "$@"; do
	case "$_arg" in
		-h | --help)
			echo "usage: safe-shell-guard.sh [--help]"
			echo "help: reads PreToolUse JSON on stdin; deny destructive shell"
			exit 0
			;;
	esac
done

INPUT=$(cat)

# Extract the command from the toolInput JSON.
# Uses basic grep/sed since jq may not be available everywhere.
COMMAND=$(echo "$INPUT" | grep -o '"command":"[^"]*"' | head -1 | sed 's/"command":"//;s/"$//' || true)

if [[ -z "${COMMAND:-}" ]]; then
	echo '{"decision":"allow"}'
	exit 0
fi

# Blocklist patterns (case-insensitive check).
LOWER_CMD=$(echo "$COMMAND" | tr '[:upper:]' '[:lower:]')

case "$LOWER_CMD" in
	*"rm -rf /"* | *"rm -rf --no-preserve-root"*)
		echo '{"decision":"deny","reason":"Blocked: rm -rf / is not allowed"}'
		exit 2
		;;
	*"sudo rm -rf"*)
		echo '{"decision":"deny","reason":"Blocked: sudo rm -rf is not allowed"}'
		exit 2
		;;
	*"mkfs"*)
		echo '{"decision":"deny","reason":"Blocked: mkfs commands are not allowed"}'
		exit 2
		;;
	*"dd if=/dev/zero of=/dev"* | *"dd if=/dev/urandom of=/dev"*)
		echo '{"decision":"deny","reason":"Blocked: dd to device is not allowed"}'
		exit 2
		;;
	*":(){"* | *"fork bomb"*)
		echo '{"decision":"deny","reason":"Blocked: fork bomb detected"}'
		exit 2
		;;
	*"> /dev/sda"* | *"> /dev/hda"* | *"> /dev/nvme"*)
		echo '{"decision":"deny","reason":"Blocked: direct write to block device"}'
		exit 2
		;;
esac

echo '{"decision":"allow"}'
exit 0
