#!/bin/bash

randomStressNgCore() {
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
            taskset_cores=$(IFS=,; echo "${core_list[*]:$i:$parallel}")

            echo "$(tput setaf 2)Testing with method $rapid on core(s) $taskset_cores for ${random_time}s [${parallel} at a time]$(tput sgr0)" | tee -a "$output_log_file"
            stress-ng --cpu "$parallel" --taskset "$taskset_cores" --timeout "${random_time}s" --cpu-method "$rapid" > /dev/null 2>&1
            check_errors
        done
        echo "$(tput setaf 3)Finished pass $parallel/$max_parallel$(tput sgr0)" | tee -a "$output_log_file"
    done
}