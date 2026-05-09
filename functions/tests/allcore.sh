allCoreTest() {

    local total_threads
    total_threads=$(nproc)
    local physical_cores=$((total_threads / 2))

    local topo=$cpu_topology
    [[ "$topo" == "0" ]] && topo=2

    declare -a core_pairs
    for (( i=0; i<physical_cores; i++ )); do
        if [[ "$topo" == "1" ]]; then
            core_pairs+=("$i,$((i + physical_cores))")
        else
            core_pairs+=("$((i * 2)),$((i * 2 + 1))")
        fi
    done

    is_blacklisted() {
        local core=$1
        IFS=',' read -ra bl <<< "$core_blacklist"
        for b in "${bl[@]}"; do
            [[ "$core" == "$b" ]] && return 0
        done
        return 1
    }

    filter_cores() {
        local filtered=()
        IFS=',' read -ra cores <<< "$1"
        for core in "${cores[@]}"; do
            is_blacklisted "$core" || filtered+=("$core")
        done
        echo "${filtered[*]}" | tr ' ' ','
    }

    declare -a stress_sets
    local cumulative=""
    for (( i=0; i<physical_cores; i++ )); do
        if [[ -z "$cumulative" ]]; then
            cumulative="${core_pairs[$i]}"
        else
            cumulative="${cumulative},${core_pairs[$i]}"
        fi
        stress_sets[$i]="$cumulative"
    done

    for load in low medium high; do
        echo "$(tput setaf 4)Running ${load} load all core tests$(tput sgr0)" | tee -a "$output_log_file"

        run_step() {
            local threads="$1"
            local filtered
            filtered=$(filter_cores "$threads")

            if [[ -z "$filtered" ]]; then
                echo "$(tput setaf 0)Skipping thread(s) $threads as disabled$(tput sgr0)" | tee -a "$output_log_file"
                return
            fi

            echo "$(tput setaf 2)Stressing thread(s) [$filtered] with ${load} load for $all_core_time seconds$(tput sgr0)" | tee -a "$output_log_file"

            update_threads "$filtered"
            start_stressor "$filtered" "$load"
            sleep "$all_core_time"
            stop_stressor
            check_errors
        }

        # Forward
        for (( i=0; i<physical_cores; i++ )); do
            run_step "${stress_sets[$i]}"
        done

        # Reverse
        for (( i=physical_cores-1; i>=0; i-- )); do
            run_step "${stress_sets[$i]}"
        done

        # Middle-out
        local mid=$(( (physical_cores - 1) / 2 ))
        local mo_cumulative="${core_pairs[$mid]}"
        local -a mo_sets=("$mo_cumulative")

        local lo=$(( mid - 1 ))
        local hi=$(( mid + 1 ))

        while (( lo >= 0 || hi < physical_cores )); do
            if (( hi < physical_cores )); then
                mo_cumulative="${core_pairs[$hi]},$mo_cumulative"
            fi
            if (( lo >= 0 )); then
                mo_cumulative="${core_pairs[$lo]},$mo_cumulative"
            fi
            mo_sets+=("$mo_cumulative")
            (( lo-- ))
            (( hi++ ))
        done

        for set in "${mo_sets[@]}"; do
            run_step "$set"
        done

        # Outside-in
        local oi_cumulative="${core_pairs[0]}"
        local -a oi_sets=("$oi_cumulative")

        local oi_lo=$(( physical_cores - 1 ))
        local oi_hi=1

        while (( oi_hi <= oi_lo )); do
            oi_cumulative="${oi_cumulative},${core_pairs[$oi_lo]}"
            if (( oi_hi <= oi_lo )); then
                oi_cumulative="${oi_cumulative},${core_pairs[$oi_hi]}"
            fi
            oi_sets+=("$oi_cumulative")
            (( oi_lo-- ))
            (( oi_hi++ ))
        done

        for set in "${oi_sets[@]}"; do
            run_step "$set"
        done

    done
}