#!/usr/bin/env bash

# Print single-core config
print_single_info() {
    DISPLAY_CORE=$(get_display_core)
    echo "◫ Testing Single Core $DISPLAY_CORE [$CORE_GROUP]"
}

# Print multi-core config
print_multi_info() {
    echo "▦ Testing All Cores"
}

# Save results
save_results() {
    local single_score=$((single / DURATION / 1000))
    local multi_score=$((multi / DURATION / 1000))
    local timestamp=$(date +"%d %b %H:%M")
    echo "${BASE_CORE},${single_score},${multi_score},${timestamp}" >> "$OUTPUT_LOG"
    tail -n 5 "$OUTPUT_LOG" > "${OUTPUT_LOG}.tmp" && mv "${OUTPUT_LOG}.tmp" "$OUTPUT_LOG"
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