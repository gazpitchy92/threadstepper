#!/usr/bin/env bash

set -euo pipefail

TERM_FILE=$(mktemp)
cleanup_term_file() {
    rm -f "$TERM_FILE"
}
trap cleanup_term_file EXIT

cleanup() {
    echo "Terminating benchmark..." >&2
    pkill -P $$ 2>/dev/null || true
    kill -TERM -$$ 2>/dev/null || true
    sleep 0.1
    kill -KILL -$$ 2>/dev/null || true
    exit 1
}

trap cleanup SIGTERM SIGINT SIGHUP

CORE_ID="${1:?Usage: rank.sh <core_id> <thread1> [thread2 ...]}"
shift
THREADS=("$@")

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_FILE="${SCRIPT_DIR}/../../logs/ranks.log"

mkdir -p "$(dirname "$LOG_FILE")"

source "${SCRIPT_DIR}/tests.sh"
source "${SCRIPT_DIR}/cpu.sh"
source "${SCRIPT_DIR}/output.sh" 

SETTINGS_FILE="${SCRIPT_DIR}/../../settings"
if [[ -f "$SETTINGS_FILE" ]]; then
    source "$SETTINGS_FILE"
fi

DURATION=5
RUNS=3
REST=1

THREAD_COUNT=${#THREADS[@]}
[[ "$THREAD_COUNT" -eq 0 ]] && THREAD_COUNT=1

CPU_LIST=$(IFS=,; echo "${THREADS[*]}")

vals=()
for ((r = 0; r < RUNS; r++)); do
    [[ $r -gt 0 ]] && sleep "$REST"
    raw=$(timeout --kill-after=1 $((DURATION + 2)) taskset -c "$CPU_LIST" bash -c "
        $(declare -f bench)
        bench $THREAD_COUNT $DURATION
    " 2>/dev/null) || {
        exit_code=$?
        if [[ $exit_code -eq 124 ]] || [[ $exit_code -eq 137 ]]; then
            cleanup
        fi
        continue
    }
    
    vals+=("$raw")
done

if [[ ${#vals[@]} -eq "$RUNS" ]]; then
    RAW_MEDIAN=$(median "${vals[@]}")
    SCORE=$(( RAW_MEDIAN / DURATION / 1000 ))
    
    echo "${CORE_ID},${SCORE}" >> "$LOG_FILE"
    echo "$SCORE"
else
    echo "Benchmark incomplete - terminated" >&2
    exit 1
fi