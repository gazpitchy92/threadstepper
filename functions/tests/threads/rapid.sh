#!/bin/bash

# rapid thread tests
rapidStressNgThread() {
    rapid_num_cores=$(nproc)
    echo "$(tput setaf 4)Testing all threads with rapid $rapid for $rapid_tests loops $(tput sgr0)" | tee -a $output_log_file
    for ((core=$start_core; core<rapid_num_cores; core++)); do
        echo "$(tput setaf 2)Testing with method $rapid on thread $core for "$rapid_time"s (rapid) $(tput sgr0)" | tee -a $output_log_file
        stress-ng --cpu 1 --taskset $core --timeout "$rapid_time"s --cpu-method "$rapid"
        check_errors
    done
}

