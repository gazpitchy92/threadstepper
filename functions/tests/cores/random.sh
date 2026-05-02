#!/bin/bash

randomStress() {
    num_cores=$(nproc)
    max_parallel=$(( num_cores / 4 ))

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

    for (( parallel = 1; parallel <= max_parallel; parallel++ )); do
        core_list=($(seq 0 $((num_cores - 1))))
        fisher_yates_shuffle core_list

        for (( i = 0; i < num_cores; i += parallel )); do
            slice=("${core_list[@]:$i:$parallel}")
            filtered=()

            for core in "${slice[@]}"; do
                IFS=',' read -ra bl <<< "$core_blacklist"
                blacklisted=false
                for b in "${bl[@]}"; do
                    [[ "$core" == "$b" ]] && blacklisted=true && break
                done
                [[ "$blacklisted" == false ]] && filtered+=("$core")
            done

            if [[ ${#filtered[@]} -eq 0 ]]; then
                echo "$(tput setaf 1)Skipping cores ${slice[*]} due to core_blacklist$(tput sgr0)" | tee -a "$output_log_file"
                continue
            fi

            taskset_cores=$(IFS=,; echo "${filtered[*]}")
            vm_count=${#filtered[@]}

            echo "$(tput setaf 2)Testing high load on core(s) $taskset_cores for ${random_time}s$(tput sgr0)" | tee -a "$output_log_file"
            update_threads "$taskset_cores"
            run_phase "$taskset_cores" high
            sleep "$rapid_time"
            kill_phase
            check_errors
        done
    done
}