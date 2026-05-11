#!/bin/bash

random_stress() {
    # CPU info
    num_cores=$(nproc)
    max_parallel=$(( num_cores / 4 ))
    # Shuffle helper
    fisher_yates_shuffle() {
        local -n arr=$1
        local n=${#arr[@]}
        for ((i = n - 1; i > 0; i--)); do
            j=$(( RANDOM % (i + 1) ))
            tmp="${arr[$i]}"
            arr[$i]="${arr[$j]}"
            arr[$j]="$tmp"
        done
    }
    # Cycle through cores
    for (( parallel = 1; parallel <= max_parallel; parallel++ )); do
        # Randomize thread selection
        core_list=($(seq 0 $((num_cores - 1))))
        fisher_yates_shuffle core_list
        saved_core_list=("${core_list[@]}")
        for (( i = 0; i < num_cores; i += parallel )); do
            # Check blacklist
            slice=("${saved_core_list[@]:$i:$parallel}")
            filtered=()
            if [[ ${#slice[@]} -eq 0 ]]; then
                continue
            fi
            ifs=',' read -ra bl <<< "$core_blacklist"
            for core in "${slice[@]}"; do
                blacklisted=false
                for b in "${bl[@]}"; do
                    [[ -n "$b" && "$core" == "$b" ]] && blacklisted=true && break
                done
                [[ "$blacklisted" == false ]] && filtered+=("$core")
            done
            if [[ ${#filtered[@]} -eq 0 ]]; then
                echo "$(tput setaf 1)Skipping thread(s) [${slice[*]}] due to as disabled$(tput sgr0)" | tee -a "$output_log_file"
                continue
            fi
            # Run stressor
            taskset_cores=$(ifs=,; echo "${filtered[*]}")
            vm_count=${#filtered[@]}
            echo "$(tput setaf 2)Testing high load on thread(s) [$taskset_cores] for ${random_time}s$(tput sgr0)" | tee -a "$output_log_file"
            update_threads "$taskset_cores"
            run_phase "$taskset_cores" high
            sleep "$random_time"
            kill_phase
            check_errors
        done
    done
}