#!/bin/bash

# stress-ng testing of cores
stressNgCore() {
    local core=$1
    local physical_cores=$(($(nproc) / 2))
    local core_second=$((core + physical_cores))
    local core_next=$((core + 1))
    
    # Test C0+C8, C1+C9, etc. (cross-die pairs)
    echo "$(tput setaf 4)-- Testing core ( $core + $core_second ) with stress-ng $(tput sgr0)" | tee -a $output_log_file
    for method in "${light[@]}"; do
        echo "$(tput setaf 2)- Testing with method $method on core ( $core + $core_second ) for $light_time (light) $(tput sgr0)" | tee -a $output_log_file
        stress-ng --cpu 2 --taskset $core,$core_second --timeout $light_time --cpu-method "$method"
        check_errors
        sleep $rest_time
    done
    for method in "${mixed[@]}"; do
        echo "$(tput setaf 2)- Testing with method $method on core ( $core + $core_second ) for $medium_time (medium) $(tput sgr0)" | tee -a $output_log_file
        stress-ng --cpu 2 --taskset $core,$core_second --timeout $medium_time --cpu-method "$method"
        sleep $rest_time
    done
    for method in "${heavy[@]}"; do
        echo "$(tput setaf 2)- Testing with method $method on core ( $core + $core_second ) for $heavy_time (heavy) $(tput sgr0)" | tee -a $output_log_file
        stress-ng --cpu 2 --taskset $core,$core_second --timeout $heavy_time --cpu-method "$method"
        check_errors
        sleep $rest_time
    done
    
    # Test C0+C1, C1+C2, etc. (adjacent core pairs)
    echo "$(tput setaf 4)-- Testing core ( $core + $core_next ) with stress-ng $(tput sgr0)" | tee -a $output_log_file
    for method in "${light[@]}"; do
        echo "$(tput setaf 2)- Testing with method $method on core ( $core + $core_next ) for $light_time (light) $(tput sgr0)" | tee -a $output_log_file
        stress-ng --cpu 2 --taskset $core,$core_next --timeout $light_time --cpu-method "$method"
        check_errors
        sleep $rest_time
    done
    for method in "${mixed[@]}"; do
        echo "$(tput setaf 2)- Testing with method $method on core ( $core + $core_next ) for $medium_time (medium) $(tput sgr0)" | tee -a $output_log_file
        stress-ng --cpu 2 --taskset $core,$core_next --timeout $medium_time --cpu-method "$method"
        sleep $rest_time
    done
    for method in "${heavy[@]}"; do
        echo "$(tput setaf 2)- Testing with method $method on core ( $core + $core_next ) for $heavy_time (heavy) $(tput sgr0)" | tee -a $output_log_file
        stress-ng --cpu 2 --taskset $core,$core_next --timeout $heavy_time --cpu-method "$method"
        check_errors
        sleep $rest_time
    done
}