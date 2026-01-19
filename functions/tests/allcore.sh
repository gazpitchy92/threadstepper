#!/bin/bash

allCoreTest() {
    echo "$(tput setaf 4)Running cumulative all core test$(tput sgr0)" | tee -a "$output_log_file"
    total_cores=$(nproc)
    
    for core in $(seq 0 $((total_cores - 1))); do
        cores_list=$(seq -s, 0 "$core")
        echo "$(tput setaf 2)Stressing cores $cores_list for $all_core_time seconds$(tput sgr0)" | tee -a "$output_log_file"
        taskset -c "$cores_list" 7z b > /dev/null 2>&1 &
        disown
        sleep "$all_core_time"
        check_errors
        pkill -9 7z > /dev/null 2>&1
    done
    
    for core in $(seq $((total_cores - 1)) -1 0); do
        cores_list=$(seq -s, 0 "$core")
        echo "$(tput setaf 2)Stressing cores $cores_list for $all_core_time seconds$(tput sgr0)" | tee -a "$output_log_file"
        taskset -c "$cores_list" 7z b > /dev/null 2>&1 &
        disown
        sleep "$all_core_time"
        check_errors
        pkill -9 7z > /dev/null 2>&1
    done
    
    for core in $(seq $((total_cores - 1)) -1 0); do
        cores_list=$(seq -s, "$core" $((total_cores - 1)))
        echo "$(tput setaf 2)Stressing cores $cores_list for $all_core_time seconds$(tput sgr0)" | tee -a "$output_log_file"
        taskset -c "$cores_list" 7z b > /dev/null 2>&1 &
        disown
        sleep "$all_core_time"
        check_errors
        pkill -9 7z > /dev/null 2>&1
    done
    
    for core in $(seq 0 $((total_cores - 1))); do
        cores_list=$(seq -s, "$core" $((total_cores - 1)))
        echo "$(tput setaf 2)Stressing cores $cores_list for $all_core_time seconds$(tput sgr0)" | tee -a "$output_log_file"
        taskset -c "$cores_list" 7z b > /dev/null 2>&1 &
        disown
        sleep "$all_core_time"
        check_errors
        pkill -9 7z > /dev/null 2>&1
    done
}