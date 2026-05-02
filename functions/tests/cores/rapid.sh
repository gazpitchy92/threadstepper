# rapid core tests
rapidStressNgCore() {
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
                echo "$(tput setaf 0)Skipping core $core due to core_blacklist$(tput sgr0)" | tee -a "$output_log_file"
            fi
            if [[ ",$core_blacklist," != *",$core_second,"* ]]; then
                active_cores+=("$core_second")
            else
                echo "$(tput setaf 0)Skipping core $core_second due to core_blacklist$(tput sgr0)" | tee -a "$output_log_file"
            fi
            
            if [[ ${#active_cores[@]} -eq 0 ]]; then
                echo "$(tput setaf 0)Skipping test - both cores blacklisted$(tput sgr0)" | tee -a "$output_log_file"
            else
                taskset_cores=$(IFS=,; echo "${active_cores[*]}")
                num_cores=${#active_cores[@]}
                echo "$(tput setaf 2)Testing with method $rapid on core(s) $taskset_cores for $rapid_time (rapid) $(tput sgr0)" | tee -a "$output_log_file"
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
                    echo "$(tput setaf 0)Skipping core $core due to core_blacklist$(tput sgr0)" | tee -a "$output_log_file"
                fi
                if [[ ",$core_blacklist," != *",$core_next,"* ]]; then
                    active_cores+=("$core_next")
                else
                    echo "$(tput setaf 0)Skipping core $core_next due to core_blacklist$(tput sgr0)" | tee -a "$output_log_file"
                fi
                
                if [[ ${#active_cores[@]} -eq 0 ]]; then
                    echo "$(tput setaf 0)Skipping test - both cores blacklisted$(tput sgr0)" | tee -a "$output_log_file"
                else
                    taskset_cores=$(IFS=,; echo "${active_cores[*]}")
                    num_cores=${#active_cores[@]}
                    echo "$(tput setaf 2)Testing with method $rapid on core(s) $taskset_cores for $rapid_time (rapid) $(tput sgr0)" | tee -a "$output_log_file"
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
                    echo "$(tput setaf 0)Skipping core $core_second due to core_blacklist$(tput sgr0)" | tee -a "$output_log_file"
                fi
                if [[ ",$core_blacklist," != *",$core_last,"* ]]; then
                    active_cores+=("$core_last")
                else
                    echo "$(tput setaf 0)Skipping core $core_last due to core_blacklist$(tput sgr0)" | tee -a "$output_log_file"
                fi
                
                if [[ ${#active_cores[@]} -eq 0 ]]; then
                    echo "$(tput setaf 0)Skipping test - both cores blacklisted$(tput sgr0)" | tee -a "$output_log_file"
                else
                    taskset_cores=$(IFS=,; echo "${active_cores[*]}")
                    num_cores=${#active_cores[@]}
                    echo "$(tput setaf 2)Testing with method $rapid on core(s) $taskset_cores for $rapid_time (rapid) $(tput sgr0)" | tee -a "$output_log_file"
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