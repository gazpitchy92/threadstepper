
#!/bin/bash

single_core_tests() {
    # Init vars
    local core=$1
    local physical_cores=$(($(nproc) / 2))
    local core_second=$((core + physical_cores))
    local core_next=$((core + 1))
    local core_last=$((core_second + 1))
    # Test C0+C8, C1+C9, etc. (cross-die pairs)
    if [[ ",$cpu_topology," == *"0"* || ",$cpu_topology," == *"1"* ]]; then
        echo "$(tput setaf 4)Testing thread(s) [$core + $core_second] of core [$core] with increasing load$(tput sgr0)" | tee -a "$output_log_file"
        # Low Load
        if [[ ",$core_blacklist," == *",$core,"* || ",$core_blacklist," == *",$core_second,"* ]]; then
            echo "$(tput setaf 0)Skipping low load test for thread(s) [$core + $core_second] of core [$core] as disabled$(tput sgr0)" | tee -a "$output_log_file"
        else
            echo "$(tput setaf 2)Testing low load on thread(s) [$core + $core_second] of core [$core] for ${light_time}s$(tput sgr0)" | tee -a "$output_log_file"
            update_threads "$core,$core_second"
            run_phase "$core,$core_second" low
            sleep "$light_time"
            kill_phase
            check_errors
            rest
        fi
        # Medium Load
        if [[ ",$core_blacklist," == *",$core,"* || ",$core_blacklist," == *",$core_second,"* ]]; then
            echo "$(tput setaf 0)Skipping medium load test for thread(s) [$core + $core_second] of core [$core] as disabled$(tput sgr0)" | tee -a "$output_log_file"
        else
            echo "$(tput setaf 2)Testing medium load on thread(s) [$core + $core_second] of core [$core] for ${medium_time}s$(tput sgr0)" | tee -a "$output_log_file"
            update_threads "$core,$core_second"
            run_phase "$core,$core_second" medium
            sleep "$medium_time"
            kill_phase
            check_errors
            rest
        fi
        # High Load
        if [[ ",$core_blacklist," == *",$core,"* || ",$core_blacklist," == *",$core_second,"* ]]; then
            echo "$(tput setaf 0)Skipping high load test for thread(s) [$core + $core_second] of core [$core] as disabled$(tput sgr0)" | tee -a "$output_log_file"
        else
            echo "$(tput setaf 2)Testing high load on thread(s) [$core + $core_second] of core [$core] for ${heavy_time}s$(tput sgr0)" | tee -a "$output_log_file"
            update_threads "$core,$core_second"
            run_phase "$core,$core_second" high
            sleep "$heavy_time"
            kill_phase
            check_errors
            rest
        fi
    fi
    # Test C0+C1, C1+C2, etc. (adjacent core pairs)
    if [[ ",$cpu_topology," == *"0"* || ",$cpu_topology," == *"2"* ]]; then
        if [[ $core_next -le $physical_cores ]]; then
            echo "$(tput setaf 4)Testing core $core + $core_next with increasing load$(tput sgr0)" | tee -a "$output_log_file"
            # Low Load
            if [[ ",$core_blacklist," == *",$core,"* || ",$core_blacklist," == *",$core_next,"* ]]; then
                echo "$(tput setaf 0)Skipping light load test for core $core + $core_next $(tput sgr0)" | tee -a "$output_log_file"
            else
                echo "$(tput setaf 2)Testing light load on core $core + $core_next for ${light_time}s$(tput sgr0)" | tee -a "$output_log_file"
                update_threads "$core,$core_next"
                run_phase "$core,$core_next" low
                sleep "$light_time"
                kill_phase
                check_errors
                rest
            fi
            # Medium Load
            if [[ ",$core_blacklist," == *",$core,"* || ",$core_blacklist," == *",$core_next,"* ]]; then
                echo "$(tput setaf 0)Skipping medium load test for core $core + $core_next $(tput sgr0)" | tee -a "$output_log_file"
            else
                echo "$(tput setaf 2)Testing medium load on core $core + $core_next for ${medium_time}s$(tput sgr0)" | tee -a "$output_log_file"
                update_threads "$core,$core_next"
                run_phase "$core,$core_next" medium
                sleep "$medium_time"
                kill_phase
                check_errors
                rest
            fi
            # High Load
            if [[ ",$core_blacklist," == *",$core,"* || ",$core_blacklist," == *",$core_next,"* ]]; then
                echo "$(tput setaf 0)Skipping heavy load test for core $core + $core_next $(tput sgr0)" | tee -a "$output_log_file"
            else
                echo "$(tput setaf 2)Testing heavy load on core $core + $core_next for ${heavy_time}s$(tput sgr0)" | tee -a "$output_log_file"
                update_threads "$core,$core_next"
                run_phase "$core,$core_next" high
                sleep "$heavy_time"
                kill_phase
                check_errors
                rest
            fi
        fi
    fi
    # Test C8+C9, C9+C10, etc. (adjacent core pairs on second die)
    if [[ ",$cpu_topology," == *"0"* || ",$cpu_topology," == *"2"* ]]; then
        if [[ $core_last -le $(nproc) ]]; then
            echo "$(tput setaf 4)Testing core $core_second + $core_last with increasing load$(tput sgr0)" | tee -a "$output_log_file"
            # Low Load
            if [[ ",$core_blacklist," == *",$core_second,"* || ",$core_blacklist," == *",$core_last,"* ]]; then
                echo "$(tput setaf 0)Skipping light load test for core $core_second + $core_last $(tput sgr0)" | tee -a "$output_log_file"
            else
                echo "$(tput setaf 2)Testing light load on core $core_second + $core_last for ${light_time}s$(tput sgr0)" | tee -a "$output_log_file"
                update_threads "$core_second,$core_last"
                run_phase "$core_second,$core_last" low
                sleep "$light_time"
                kill_phase
                check_errors
                rest
            fi
            # Medium Load
            if [[ ",$core_blacklist," == *",$core_second,"* || ",$core_blacklist," == *",$core_last,"* ]]; then
                echo "$(tput setaf 0)Skipping medium load test for core $core_second + $core_last $(tput sgr0)" | tee -a "$output_log_file"
            else
                echo "$(tput setaf 2)Testing medium load on core $core_second + $core_last for ${medium_time}s$(tput sgr0)" | tee -a "$output_log_file"
                update_threads "$core_second,$core_last"
                run_phase "$core_second,$core_last" medium
                sleep "$medium_time"
                kill_phase
                check_errors
                rest
            fi
            # High Load
            if [[ ",$core_blacklist," == *",$core_second,"* || ",$core_blacklist," == *",$core_last,"* ]]; then
                echo "$(tput setaf 0)Skipping high load test for core $core_second + $core_last $(tput sgr0)" | tee -a "$output_log_file"
            else
                echo "$(tput setaf 2)Testing high load on core $core_second + $core_last for ${high_time}s$(tput sgr0)" | tee -a "$output_log_file"
                update_threads "$core_second,$core_last"
                run_phase "$core_second,$core_last" high
                sleep "$high_time"
                kill_phase
                check_errors
                rest
            fi
        fi
    fi
}