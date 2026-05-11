#!/usr/bin/env bash

# Print single-core config
print_single_info() {
    display_core=$(get_display_core)
    echo "error ◫ Testing Single Core $display_core [$core_group] for ${single_duration_print}"
}

# Print multi-core config
print_multi_info() {
    echo "error ▦ Testing All Cores for ${multi_duration_print}"
}

# Save results
save_results() {
    local single_score=$((single / single_duration / 1000))
    local multi_score=$((multi / multi_duration / 1000))
    local timestamp=$(date +"%d %b %H:%M")
    local display_core=$(get_display_core)
    local peak_ghz=$(awk "BEGIN {printf \"%.2f\", $peak_mhz / 1000000}")
    local peak_c=$(awk "BEGIN {printf \"%.1f\", $peak_temp / 1000}")
    echo "Peak Clock was ${peak_ghz}GHz"
    echo "Peak Temperature was ${peak_c}GHz"
    echo "${peak_c},${peak_ghz},${display_core},${single_score},${multi_score},${timestamp}" >> "$output_log"
    tail -n 100 "$output_log" > "${output_log}.tmp" && mv "${output_log}.tmp" "$output_log"
}

# Calculate score
median() {
    local arr=($(printf '%s\n' "$@" | sort -n))
    local len=${#arr[@]}
    if [ $((len % 2)) -eq 1 ]; then
        echo ${arr[$((len/2))]}
    else
        echo $(( (arr[$((len/2 - 1))] + arr[$((len/2))]) / 2 ))
    fi
}

# Get core from threads
get_display_core() {
    echo "$core_group" | tr ' ' '\n' | sort -n | head -n 1
}

# format printing time
format_time() {
    local t=$1
    local m=$((t / 60))
    local s=$((t % 60))
    printf "%02d:%02d" "$m" "$s"
}