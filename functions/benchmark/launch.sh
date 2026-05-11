#!/usr/bin/env bash


# Init vars
source "$(dirname "$CURRENT_DIR")/config/user.settings"
NCPU=$(nproc)
CORES_COUNT=$(( NCPU / 2 ))
CURRENT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OUTPUT_LOG="$(dirname "$CURRENT_DIR")/../logs/benchmark.log"
SELECTED_CORE="$1"

# Setup
mkdir -p "$(dirname "$OUTPUT_LOG")"
if [ ! -f "$OUTPUT_LOG" ]; then
    > "$OUTPUT_LOG"
fi

# Functions
source "$(dirname "$CURRENT_DIR")/benchmark/cpu.sh"
source "$(dirname "$CURRENT_DIR")/benchmark/output.sh"
source "$(dirname "$CURRENT_DIR")/benchmark/tests.sh"

# ------ Calculate Times
# Rest time
REST_DURATION=$(( bm_rest_duration ))
# All Core
MULTI_DURATION=$(( bm_all_duration ))
MULTI_RUNS=$(( bm_all_tests ))
MULTI_REST_DURATION=$(( MULTI_RUNS * REST_DURATION ))
TOTAL_MULTI_DURATION=$(( MULTI_DURATION * MULTI_RUNS ))
MULTI_DURATION_ESTIMATE=$(( (TOTAL_MULTI_DURATION + MULTI_REST_DURATION) ))
MULTI_DURATION_PRINT=$(printf "%dm %02ds" \
  "$(( MULTI_DURATION_ESTIMATE / 60 ))" \
  "$(( MULTI_DURATION_ESTIMATE % 60 ))")
# Single Core
SINGLE_DURATION=$(( bm_single_duration ))
SINGLE_RUNS=$(( bm_single_tests ))
SINGLE_REST_DURATION=$(( SINGLE_RUNS * REST_DURATION ))
TOTAL_SINGLE_DURATION=$(( SINGLE_DURATION * SINGLE_RUNS ))
SINGLE_DURATION_ESTIMATE=$(( (TOTAL_SINGLE_DURATION + SINGLE_REST_DURATION) ))
SINGLE_DURATION_PRINT=$(printf "%dm %02ds" \
  "$(( SINGLE_DURATION_ESTIMATE / 60 ))" \
  "$(( SINGLE_DURATION_ESTIMATE % 60 ))")
# Time calculations
TOTAL_RUNS=$(( SINGLE_RUNS + MULTI_RUNS ))
TOTAL_REST_DURATION=$(( TOTAL_RUNS * REST_DURATION ))
TOTAL_DURATION_SECONDS=$(( TOTAL_REST_DURATION + TOTAL_SINGLE_DURATION + TOTAL_MULTI_DURATION ))
# Total time output
mins=$(( TOTAL_DURATION_SECONDS / 60 ))
secs=$(( TOTAL_DURATION_SECONDS % 60 ))
echo "info Benchmark started at $(date +%H:%M:%S)"
echo "info This will take approx. ${mins}m ${secs}s"
# ------------

# ------ Main
notify-send "Thread Stepper" "Benchmark started at $(date +%H:%M:%S)"
select_core
resolve_threads
print_single_info
run_single
print_multi_info
run_multi
save_results
echo "info Benchmark finished at $(date +%H:%M:%S)"
notify-send "Thread Stepper" "Benchmark finished at $(date +%H:%M:%S)"
# ------------
