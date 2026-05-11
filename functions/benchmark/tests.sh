#!/usr/bin/env bash

# Run benchmark
bench() {
    local cores=$1
    local bench_duration=$2
    local temp_dir=$(mktemp -d)
    for ((c=0; c<cores; c++)); do
        (
            local bench_end=$((SECONDS + bench_duration))
            local ops=0
            local x=123456789
            for ((i=0; i<50000; i++)); do
                x=$(( (x * 1103515245 + 12345) & 0x7fffffff ))
            done
            while [ $SECONDS -lt $bench_end ]; do
                for ((i=0; i<5000; i++)); do
                    x=$(( (x * 1103515245 + 12345) & 0x7fffffff ))
                    ((ops++))
                done
            done
            printf "%s" "$ops" > "$temp_dir/thread_$c"
        ) &
    done
    wait
    local total=0
    for f in "$temp_dir"/thread_*; do
        total=$((total + $(<"$f")))
    done
    rm -rf "$temp_dir"
    echo "$total"
}
export -f bench

# Single core test
run_single() {
    single_vals=()
    echo "Core count $((core_count))"
    for ((r=0; r<single_runs; r++)); do
        sleep "$rest_duration"
        taskset -c "$cpus" bash -c "bench $core_count $single_duration" > /tmp/_single_out &
        local bench_pid=$!
        sample_cpu "$bench_pid"
        wait "$bench_pid"
        single_vals+=($(<"/tmp/_single_out"))
    done
    single=$(median "${single_vals[@]}")
    echo "◫ Single Core score is $((single / single_duration / 1000))"
}

# Multi core test
run_multi() {
    multi_vals=()
    for ((r=0; r<multi_runs; r++)); do
        sleep "$rest_duration"
        bench $ncpu $multi_duration > /tmp/_multi_out &
        local bench_pid=$!
        sample_cpu "$bench_pid"
        wait "$bench_pid"
        multi_vals+=($(<"/tmp/_multi_out"))
    done
    multi=$(median "${multi_vals[@]}")
    echo "▦ All Core score is $((multi / multi_duration / 1000))"
}

# Sample clock in background
sample_cpu() {
    local pid=$1
    while kill -0 "$pid" 2>/dev/null; do
        local mhz=$(get_clock_mhz)
        local temp=$(get_cpu_temp)
        if [[ -n "$mhz" && "$mhz" -gt "$peak_mhz" ]]; then
            peak_mhz=$mhz
        fi
        if [[ -n "$temp" && "$temp" -gt "$peak_temp" ]]; then
            peak_temp=$temp
        fi
        sleep 0.25
    done
}