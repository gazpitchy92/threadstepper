
#!/bin/bash

# stress-ng testing of cores
stressNgCore() {
    local core=$1
    local physical_cores=$(($(nproc) / 2))
    local core_second=$((core + physical_cores))
    local core_next=$((core + 1))
    local core_last=$((core_second + 1))
    
    # Test C0+C8, C1+C9, etc. (cross-die pairs)
    if [[ ",$cpu_topology," == *"0"* || ",$cpu_topology," == *"1"* ]]; then
        echo "$(tput setaf 4)Testing core $core + $core_second with stress-ng $(tput sgr0)" | tee -a "$output_log_file"
        for method in "${light[@]}"; do
            if [[ ",$core_blacklist," == *",$core,"* || ",$core_blacklist," == *",$core_second,"* ]]; then
                echo "$(tput setaf 0)Skipping test for core $core + $core_second $(tput sgr0)" | tee -a "$output_log_file"
            else
                echo "$(tput setaf 2)Testing with method $method on core $core + $core_second for $light_time (light) $(tput sgr0)" | tee -a "$output_log_file"
                stress-ng --cpu 2 --taskset "$core,$core_second" --timeout "$light_time"s --cpu-method "$method" --vm 2 --vm-bytes "$max_ram"G > /dev/null 2>&1
                check_errors
                sleep "$rest_time"
            fi
        done
        for method in "${mixed[@]}"; do
            if [[ ",$core_blacklist," == *",$core,"* || ",$core_blacklist," == *",$core_second,"* ]]; then
                echo "$(tput setaf 0)Skipping test for core $core + $core_second $(tput sgr0)" | tee -a "$output_log_file"
            else
                echo "$(tput setaf 2)Testing with method $method on core $core + $core_second for $medium_time (medium) $(tput sgr0)" | tee -a "$output_log_file"
                stress-ng --cpu 2 --taskset "$core,$core_second" --timeout "$medium_time"s --cpu-method "$method" --vm 2 --vm-bytes "$max_ram"G > /dev/null 2>&1
                check_errors
                sleep "$rest_time"
            fi
        done
        for method in "${heavy[@]}"; do
            if [[ ",$core_blacklist," == *",$core,"* || ",$core_blacklist," == *",$core_second,"* ]]; then
                echo "$(tput setaf 0)Skipping test for core $core + $core_second $(tput sgr0)" | tee -a "$output_log_file"
            else
                echo "$(tput setaf 2)Testing with method $method on core $core + $core_second for $heavy_time (heavy) $(tput sgr0)" | tee -a "$output_log_file"
                stress-ng --cpu 2 --taskset "$core,$core_second" --timeout "$heavy_time"s --cpu-method "$method" --vm 2 --vm-bytes "$max_ram"G > /dev/null 2>&1
                check_errors
                sleep "$rest_time"
            fi
        done
    fi
    
    # Test C0+C1, C1+C2, etc. (adjacent core pairs)
    if [[ ",$cpu_topology," == *"0"* || ",$cpu_topology," == *"2"* ]]; then
        if [[ $core_next -lt $physical_cores ]]; then
            echo "$(tput setaf 4)Testing core $core + $core_next with stress-ng $(tput sgr0)" | tee -a "$output_log_file"
            for method in "${light[@]}"; do
                if [[ ",$core_blacklist," == *",$core,"* || ",$core_blacklist," == *",$core_next,"* ]]; then
                    echo "$(tput setaf 0)Skipping test for core $core + $core_next $(tput sgr0)" | tee -a "$output_log_file"
                else
                    echo "$(tput setaf 2)Testing with method $method on core $core + $core_next for $light_time (light) $(tput sgr0)" | tee -a "$output_log_file"
                    stress-ng --cpu 2 --taskset "$core,$core_next" --timeout "$light_time"s --cpu-method "$method" --vm 2 --vm-bytes "$max_ram"G > /dev/null 2>&1
                    check_errors
                    sleep "$rest_time"
                fi
            done
            for method in "${mixed[@]}"; do
                if [[ ",$core_blacklist," == *",$core,"* || ",$core_blacklist," == *",$core_next,"* ]]; then
                    echo "$(tput setaf 0)Skipping test for core $core + $core_next $(tput sgr0)" | tee -a "$output_log_file"
                else
                    echo "$(tput setaf 2)Testing with method $method on core $core + $core_next for $medium_time (medium) $(tput sgr0)" | tee -a "$output_log_file"
                    stress-ng --cpu 2 --taskset "$core,$core_next" --timeout "$medium_time"s --cpu-method "$method" --vm 2 --vm-bytes "$max_ram"G > /dev/null 2>&1
                    check_errors
                    sleep "$rest_time"
                fi
            done
            for method in "${heavy[@]}"; do
                if [[ ",$core_blacklist," == *",$core,"* || ",$core_blacklist," == *",$core_next,"* ]]; then
                    echo "$(tput setaf 0)Skipping test for core $core + $core_next $(tput sgr0)" | tee -a "$output_log_file"
                else
                    echo "$(tput setaf 2)Testing with method $method on core $core + $core_next for $heavy_time (heavy) $(tput sgr0)" | tee -a "$output_log_file"
                    stress-ng --cpu 2 --taskset "$core,$core_next" --timeout "$heavy_time"s --cpu-method "$method" --vm 2 --vm-bytes "$max_ram"G > /dev/null 2>&1
                    check_errors
                    sleep "$rest_time"
                fi
            done
        fi
    fi

    # Test C8+C9, C9+C10, etc. (adjacent core pairs on second die)
    if [[ ",$cpu_topology," == *"0"* || ",$cpu_topology," == *"2"* ]]; then
        if [[ $core_last -lt $(nproc) ]]; then
            echo "$(tput setaf 4)Testing core $core_second + $core_last with stress-ng $(tput sgr0)" | tee -a "$output_log_file"
            for method in "${light[@]}"; do
                if [[ ",$core_blacklist," == *",$core_second,"* || ",$core_blacklist," == *",$core_last,"* ]]; then
                    echo "$(tput setaf 0)Skipping test for core $core_second + $core_last $(tput sgr0)" | tee -a "$output_log_file"
                else
                    echo "$(tput setaf 2)Testing with method $method on core $core_second + $core_last for $light_time (light) $(tput sgr0)" | tee -a "$output_log_file"
                    stress-ng --cpu 2 --taskset "$core_second,$core_last" --timeout "$light_time"s --cpu-method "$method" --vm 2 --vm-bytes "$max_ram"G > /dev/null 2>&1
                    check_errors
                    sleep "$rest_time"
                fi
            done
            for method in "${mixed[@]}"; do
                if [[ ",$core_blacklist," == *",$core_second,"* || ",$core_blacklist," == *",$core_last,"* ]]; then
                    echo "$(tput setaf 0)Skipping test for core $core_second + $core_last $(tput sgr0)" | tee -a "$output_log_file"
                else
                    echo "$(tput setaf 2)Testing with method $method on core $core_second + $core_last for $medium_time (medium) $(tput sgr0)" | tee -a "$output_log_file"
                    stress-ng --cpu 2 --taskset "$core_second,$core_last" --timeout "$medium_time"s --cpu-method "$method" --vm 2 --vm-bytes "$max_ram"G > /dev/null 2>&1
                    check_errors
                    sleep "$rest_time"
                fi
            done
            for method in "${heavy[@]}"; do
                if [[ ",$core_blacklist," == *",$core_second,"* || ",$core_blacklist," == *",$core_last,"* ]]; then
                    echo "$(tput setaf 0)Skipping test for core $core_second + $core_last $(tput sgr0)" | tee -a "$output_log_file"
                else
                    echo "$(tput setaf 2)Testing with method $method on core $core_second + $core_last for $heavy_time (heavy) $(tput sgr0)" | tee -a "$output_log_file"
                    stress-ng --cpu 2 --taskset "$core_second,$core_last" --timeout "$heavy_time"s --cpu-method "$method" --vm 2 --vm-bytes "$max_ram"G > /dev/null 2>&1
                    check_errors
                    sleep "$rest_time"
                fi
            done
        fi
    fi
}