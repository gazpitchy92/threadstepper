#!/usr/bin/env bash

# Init
SELECTED_CORE="$1"
DURATION=15
RUNS=4
NCPU=$(nproc)
CURRENT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OUTPUT_LOG="$(dirname "$CURRENT_DIR")/../logs/benchmark.log"

# functions
source "$(dirname "$CURRENT_DIR")/benchmark/cpu.sh"
source "$(dirname "$CURRENT_DIR")/benchmark/output.sh"
source "$(dirname "$CURRENT_DIR")/benchmark/tests.sh"

# Setup
mkdir -p "$(dirname "$OUTPUT_LOG")"
if [ ! -f "$OUTPUT_LOG" ]; then
    > "$OUTPUT_LOG"
fi

# ---------------- MAIN ----------------
select_core
resolve_threads
print_single_info
run_single
print_multi_info
run_multi
save_results