#!/usr/bin/env bash

# Print single-core config
print_single_info() {
    DISPLAY_CORE=$(get_display_core)
    echo "error ◫ Testing Single Core $DISPLAY_CORE [$CORE_GROUP] for ${SINGLE_DURATION_PRINT}"
}

# Print multi-core config
print_multi_info() {
    echo "error ▦ Testing All Cores for ${MULTI_DURATION_PRINT}"
}

# Save results
save_results() {
    local single_score=$((single / SINGLE_DURATION / 1000))
    local multi_score=$((multi / MULTI_DURATION / 1000))
    local timestamp=$(date +"%d %b %H:%M")
    local display_core=$(get_display_core)
    echo "${display_core},${single_score},${multi_score},${timestamp}" >> "$OUTPUT_LOG"
    tail -n 7 "$OUTPUT_LOG" > "${OUTPUT_LOG}.tmp" && mv "${OUTPUT_LOG}.tmp" "$OUTPUT_LOG"
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

# Parse core number from threads
get_display_core() {
    echo "$CORE_GROUP" | tr ' ' '\n' | sort -n | head -n 1
}

# format printing time
format_time() {
  local t=$1
  local m=$((t / 60))
  local s=$((t % 60))
  printf "%02d:%02d" "$m" "$s"
}