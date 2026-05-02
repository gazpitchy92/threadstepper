# rapid core tests
rapidTest() {
    rapid_num_cores=$(nproc)
    physical_cores=$((rapid_num_cores / 2))
    
    for ((core=start_core; core<physical_cores; core++)); do
        core_second=$((core + physical_cores))
        core_next=$((core + 1))
        
        # Test C0+C8, C1+C9, etc. (cross-die pairs)
        if [[ ",$cpu_topology," == *"0"* || ",$cpu_topology," == *"1"* ]]; then
            active_cores=()
            if [[ ",$core_blacklist," != *",$core,"* ]]; then
                active_cores+=("$core")
            else
                echo "$(tput setaf 0)Skipping thread(s) [$core] as disabled$(tput sgr0)" | tee -a "$output_log_file"
            fi
            if [[ ",$core_blacklist," != *",$core_second,"* ]]; then
                active_cores+=("$core_second")
            else
                echo "$(tput setaf 0)Skipping thread(s) [$core_second] as disabled$(tput sgr0)" | tee -a "$output_log_file"
            fi
            
            if [[ ${#active_cores[@]} -eq 0 ]]; then
                echo "$(tput setaf 0)Skipping test as both thread(s) disabled$(tput sgr0)" | tee -a "$output_log_file"
            else
                taskset_cores=$(IFS=,; echo "${active_cores[*]}")
                num_cores=${#active_cores[@]}
                echo "$(tput setaf 2)Testing high load on thread(s) [$taskset_cores] of core [${active_cores[0]}] for ${rapid_time}s$(tput sgr0)" | tee -a "$output_log_file"
                update_threads "$taskset_cores"
                run_phase "$taskset_cores" high
                sleep "$rapid_time"
                kill_phase
                check_errors
            fi
        fi
        
        # Test C0+C1, C1+C2, etc. (adjacent core pairs)
        if [[ ",$cpu_topology," == *"0"* || ",$cpu_topology," == *"2"* ]]; then
            if [[ $core_next -lt $physical_cores ]]; then
                active_cores=()
                if [[ ",$core_blacklist," != *",$core,"* ]]; then
                    active_cores+=("$core")
                else
                    echo "$(tput setaf 0)Skipping thread(s) [$core] as disabled$(tput sgr0)" | tee -a "$output_log_file"
                fi
                if [[ ",$core_blacklist," != *",$core_next,"* ]]; then
                    active_cores+=("$core_next")
                else
                    echo "$(tput setaf 0)Skipping thread(s) [$core_next] as disabled$(tput sgr0)" | tee -a "$output_log_file"
                fi
                
                if [[ ${#active_cores[@]} -eq 0 ]]; then
                    echo "$(tput setaf 0)Skipping signle core test as both thread(s) disabled$(tput sgr0)" | tee -a "$output_log_file"
                else
                    taskset_cores=$(IFS=,; echo "${active_cores[*]}")
                    num_cores=${#active_cores[@]}
                    echo "$(tput setaf 2)Testing high load on thread(s) [$taskset_cores] of core [${active_cores[0]}] for ${rapid_time}s$(tput sgr0)" | tee -a "$output_log_file"
                    update_threads "$taskset_cores"
                    run_phase "$taskset_cores" high
                    sleep "$rapid_time"
                    kill_phase
                    check_errors
                fi
            fi
        fi

        # Test C8+C9, C9+C10, etc. (adjacent core pairs on second die)
        if [[ ",$cpu_topology," == *"0"* || ",$cpu_topology," == *"2"* ]]; then
            local core_last=$((core_second + 1))
            if [[ $core_last -lt $rapid_num_cores ]]; then
                active_cores=()
                if [[ ",$core_blacklist," != *",$core_second,"* ]]; then
                    active_cores+=("$core_second")
                else
                    echo "$(tput setaf 0)Skipping thread(s) [$core_second] as disabled$(tput sgr0)" | tee -a "$output_log_file"
                fi
                if [[ ",$core_blacklist," != *",$core_last,"* ]]; then
                    active_cores+=("$core_last")
                else
                    echo "$(tput setaf 0)Skipping thread(s) [$core_last] as disabled$(tput sgr0)" | tee -a "$output_log_file"
                fi
                
                if [[ ${#active_cores[@]} -eq 0 ]]; then
                    echo "$(tput setaf 0)Skipping single core test as both thread(s) are disabled$(tput sgr0)" | tee -a "$output_log_file"
                else
                    taskset_cores=$(IFS=,; echo "${active_cores[*]}")
                    num_cores=${#active_cores[@]}
                    echo "$(tput setaf 2)Testing high load on thread(s) [$taskset_cores] of core [${active_cores[0]}] for ${rapid_time}s$(tput sgr0)" | tee -a "$output_log_file"
                    update_threads "$taskset_cores"
                    run_phase "$taskset_cores" high
                    sleep "$rapid_time"
                    kill_phase
                    check_errors
                fi
            fi
        fi
    done
}