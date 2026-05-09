#!/usr/bin/env bash

# Run benchmark
bench() {
    local cores=$1
    local duration=$2
    local temp_dir=$(mktemp -d)

    for ((c=0; c<cores; c++)); do
        (
            local end=$((SECONDS + duration))
            local ops=0
            local x=123456789

            while [ $SECONDS -lt $end ]; do
                for ((i=0; i<100000; i++)); do
                    x=$(( (x * 1103515245 + 12345) & 0x7fffffff ))
                    ((ops++))
                done
            done

            echo $ops > "$temp_dir/thread_$c"
        ) &
    done

    wait

    local total=0
    for f in "$temp_dir"/thread_*; do
        total=$((total + $(cat "$f")))
    done

    rm -rf "$temp_dir"
    echo $total
}

export -f bench

# Single core test
run_single() {
    single_vals=()

    for ((r=0; r<RUNS; r++)); do
        single_vals+=($(taskset -c "$CPUS" bash -c "bench $CORE_COUNT $DURATION"))
    done

    single=$(median "${single_vals[@]}")
    echo "Single Core: $((single / DURATION / 1000))"
}

# Multi core test
run_multi() {
    multi_vals=()

    for ((r=0; r<RUNS; r++)); do
        multi_vals+=($(bench $NCPU $DURATION))
    done

    multi=$(median "${multi_vals[@]}")
    echo "Multi Core: $((multi / DURATION / 1000))"
}
