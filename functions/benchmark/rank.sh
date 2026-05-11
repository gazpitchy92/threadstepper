#!/usr/bin/env bash

set -euo pipefail

term_file=$(mktemp)
cleanup_term_file() {
    rm -f "$term_file"
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

core_id="${1:?Usage: rank.sh <core_id> <thread1> [thread2 ...]}"
shift
THREADS=("$@")

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
log_file="${script_dir}/../../logs/ranks.log"

mkdir -p "$(dirname "$log_file")"

source "${script_dir}/tests.sh"
source "${script_dir}/cpu.sh"
source "${script_dir}/output.sh" 

SETTINGS_FILE="${script_dir}/../../settings"
if [[ -f "$SETTINGS_FILE" ]]; then
    source "$SETTINGS_FILE"
fi

DURATION=5
RUNS=3
REST=1

thread_count=${#THREADS[@]}
[[ "$thread_count" -eq 0 ]] && thread_count=1

cpu_list=$(IFS=,; echo "${THREADS[*]}")

vals=()
for ((r = 0; r < RUNS; r++)); do
    [[ $r -gt 0 ]] && sleep "$REST"
    raw=$(timeout --kill-after=1 $((DURATION + 2)) taskset -c "$cpu_list" bash -c "
        $(declare -f bench)
        bench $thread_count $DURATION
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
    raw_median=$(median "${vals[@]}")
    end_score=$(( raw_median / DURATION / 1000 ))
    
    echo "${core_id},${end_score}" >> "$log_file"
    echo "$end_score"
else
    echo "Benchmark incomplete - terminated" >&2
    exit 1
fi