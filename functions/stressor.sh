#!/usr/bin/env bash

_STRESS_PIDS=()

_calc_prng() {
    local x=123456789
    for ((i=0; i<100000; i++)); do
        x=$(( (x * 1103515245 + 12345) & 0x7fffffff ))
    done
    echo $x
}

_calc_sum() {
    local x=0
    for ((i=1; i<=100000; i++)); do
        x=$(( (x + i * 31337) & 0x7fffffff ))
    done
    echo $x
}

_calc_div() {
    local x=2147483647
    for ((i=1; i<=100000; i++)); do
        x=$(( ((x * 1664525) & 0x7fffffff) / (i % 97 + 1) ))
        x=$(( (x + i) & 0x7fffffff ))
    done
    echo $x
}

export -f _calc_prng _calc_sum _calc_bitwise _calc_div

_stress_worker() {
    local worker_index=$1

    local calcs=(
        "prng:1866790773"
        "sum:1864924624"
        "div:12260201"
    )
    local entry="${calcs[$((worker_index % ${#calcs[@]}))]}"
    local name="${entry%%:*}"
    local expected="${entry##*:}"
    local cpu
    cpu=$(taskset -cp $$ 2>/dev/null | awk -F': ' '{print $2}')

    while true; do
        local result
        result=$(bash -c "_calc_${name}")
        if [[ "$result" -ne "$expected" ]]; then
            logger -p err "Thread Stepper: arithmetic error [$name] on CPU $cpu — expected $expected, got $result"
        fi
    done
}
export -f _stress_worker


start_stressor() {
    local cores_list=$1
    local thread_count
    thread_count=$(echo "$cores_list" | tr ',' '\n' | wc -l)

    for ((c=0; c<thread_count; c++)); do
        taskset -c "$cores_list" bash -c "_stress_worker $c" &
        _STRESS_PIDS+=($!)
    done
}

stop_stressor() {
    for pid in "${_STRESS_PIDS[@]}"; do
        kill "$pid" 2>/dev/null
        wait "$pid" 2>/dev/null
    done
    _STRESS_PIDS=()
}