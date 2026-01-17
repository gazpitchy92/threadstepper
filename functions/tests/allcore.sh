#!/bin/bash

# full cpu 7zip stress
allCoreTest() {
    echo "$(tput setaf 4)Running 7z warmup on all cores $(tput sgr0)" | tee -a $output_log_file
    for i in $(seq 1 $all_core_time); do
        # increase test time by 1s until $all_core_time
        echo "$(tput setaf 2)Running 7z for $i seconds $(tput sgr0)" | tee -a $output_log_file
        7z b > /dev/null 2>&1 &
        sleep "$i"
        pkill 7z
        check_errors
        sleep $rest_time
    done
}