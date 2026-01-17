#!/bin/bash

# rapid core tests
rapidStressNgCore() {
    rapid_num_cores=$(nproc)
    physical_cores=$((rapid_num_cores / 2))
    echo "$(tput setaf 4)-- Testing all cores with rapid $rapid for $rapid_tests loops $(tput sgr0)" | tee -a $output_log_file
    
    for ((core=$start_core; core<physical_cores; core++)); do
        core_second=$((core + physical_cores))
        core_next=$((core + 1))
        
        # Test C0+C8, C1+C9, etc. (cross-die pairs)
        echo "$(tput setaf 2)- Testing with method $rapid on core $core ( $core + $core_second ) for $rapid_time (rapid) $(tput sgr0)" | tee -a $output_log_file
        stress-ng --cpu 2 --taskset $core,$core_second --timeout $rapid_time --cpu-method "$rapid"
        check_errors
        
        # Test C0+C1, C1+C2, etc. (adjacent core pairs)
        echo "$(tput setaf 2)- Testing with method $rapid on core $core ( $core + $core_next ) for $rapid_time (rapid) $(tput sgr0)" | tee -a $output_log_file
        stress-ng --cpu 2 --taskset $core,$core_next --timeout $rapid_time --cpu-method "$rapid"
        check_errors
    done
}