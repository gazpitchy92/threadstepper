#!/usr/bin/env bash


# Init vars
source "$(dirname "$current_dir")/config/user.settings"
ncpu=$(nproc)
cores_count=$(( ncpu / 2 ))
current_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
output_log="$(dirname "$current_dir")/../logs/benchmark.log"
selected_core="$1"

# Setup
mkdir -p "$(dirname "$output_log")"
if [ ! -f "$output_log" ]; then
    > "$output_log"
fi

# Functions
source "$(dirname "$current_dir")/benchmark/cpu.sh"
source "$(dirname "$current_dir")/benchmark/output.sh"
source "$(dirname "$current_dir")/benchmark/tests.sh"

# ------ Calculate Times
# Rest time
rest_duration=$(( bm_rest_duration ))
# All Core
multi_duration=$(( bm_all_duration ))
multi_runs=$(( bm_all_tests ))
multi_rest_duration=$(( multi_runs * rest_duration ))
total_multi_duration=$(( multi_duration * multi_runs ))
multi_duration_estimate=$(( (total_multi_duration + multi_rest_duration) ))
multi_duration_print=$(printf "%dm %02ds" \
  "$(( multi_duration_estimate / 60 ))" \
  "$(( multi_duration_estimate % 60 ))")
# Single Core
single_duration=$(( bm_single_duration ))
single_runs=$(( bm_single_tests ))
single_rest_duration=$(( single_runs * rest_duration ))
total_single_duration=$(( single_duration * single_runs ))
single_duration_estimate=$(( (total_single_duration + single_rest_duration) ))
single_duration_print=$(printf "%dm %02ds" \
  "$(( single_duration_estimate / 60 ))" \
  "$(( single_duration_estimate % 60 ))")
# Time calculations
total_runs=$(( single_runs + multi_runs ))
total_rest_duration=$(( total_runs * rest_duration ))
total_duration_seconds=$(( total_rest_duration + total_single_duration + total_multi_duration ))
# Total time output
mins=$(( total_duration_seconds / 60 ))
secs=$(( total_duration_seconds % 60 ))
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
