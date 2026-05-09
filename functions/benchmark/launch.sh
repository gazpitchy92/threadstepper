#!/usr/bin/env bash

# Init vars
NCPU=$(nproc)
CORES_COUNT=$(( NCPU / 2 ))
CURRENT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OUTPUT_LOG="$(dirname "$CURRENT_DIR")/../logs/benchmark.log"
SELECTED_CORE="$1"

# Functions
source "$(dirname "$CURRENT_DIR")/benchmark/cpu.sh"
source "$(dirname "$CURRENT_DIR")/benchmark/output.sh"
source "$(dirname "$CURRENT_DIR")/benchmark/tests.sh"

# Rest time
REST_DURATION=2

# All Core
MULTI_DURATION=$(( 15 ))
MULTI_RUNS=$(( CORES_COUNT ))
MULTI_REST_DURATION=$(( MULTI_RUNS * REST_DURATION ))
TOTAL_MULTI_DURATION=$(( MULTI_DURATION * MULTI_RUNS ))
MULTI_DURATION_ESTIMATE=$(( (TOTAL_MULTI_DURATION + MULTI_REST_DURATION) ))
MULTI_DURATION_PRINT=$(printf "%dm %02ds" \
  "$(( MULTI_DURATION_ESTIMATE / 60 ))" \
  "$(( MULTI_DURATION_ESTIMATE % 60 ))")
echo "debug All core duration: ${MULTI_DURATION}$(tput sgr0)"
echo "debug All core tests: ${MULTI_RUNS}$(tput sgr0)"

# Single Core
SINGLE_DURATION=$(( TOTAL_MULTI_DURATION / ((CORES_COUNT +1) * (2)) ))
SINGLE_RUNS=$(( CORES_COUNT * 2 ))
SINGLE_REST_DURATION=$(( SINGLE_RUNS * REST_DURATION ))
TOTAL_SINGLE_DURATION=$(( SINGLE_DURATION * SINGLE_RUNS ))
SINGLE_DURATION_ESTIMATE=$(( (TOTAL_SINGLE_DURATION + SINGLE_REST_DURATION) ))
SINGLE_DURATION_PRINT=$(printf "%dm %02ds" \
  "$(( SINGLE_DURATION_ESTIMATE / 60 ))" \
  "$(( SINGLE_DURATION_ESTIMATE % 60 ))")
echo "debug Single core duration:  ${SINGLE_DURATION}"
echo "debug Single core tests: ${SINGLE_RUNS}"

# Time calculations
TOTAL_RUNS=$(( SINGLE_RUNS + MULTI_RUNS ))
TOTAL_REST_DURATION=$(( TOTAL_RUNS * REST_DURATION ))
TOTAL_DURATION_SECONDS=$(( TOTAL_REST_DURATION + TOTAL_SINGLE_DURATION + TOTAL_MULTI_DURATION ))

# Total time output
mins=$(( TOTAL_DURATION_SECONDS / 60 ))
secs=$(( TOTAL_DURATION_SECONDS % 60 ))
echo "info Benchmark started at $(date +%H:%M:%S)"
echo "info This will take approx. ${mins}m ${secs}s"

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