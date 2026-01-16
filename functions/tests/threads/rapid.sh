#!/bin/bash

# rapid thread tests
rapidStressNgThread() {
    rapid_num_cores=$(nproc)
    echo "$(tput setaf 4)-- Testing all threads with rapid $rapid for $rapid_tests loops $(tput sgr0)" | tee -a log.txt
    for ((core=$start_core; core<rapid_num_cores; core++)); do
        echo "$(tput setaf 2)- Testing with method $rapid on thread $core for $rapid_time (rapid) $(tput sgr0)" | tee -a log.txt
        stress-ng --cpu 1 --taskset $core --timeout $rapid_time --cpu-method "$rapid"
        check_errors
    done
}

