#!/bin/bash

# stress-ng testing of threads
stressNgThread() {
    local core=$1
    echo "$(tput setaf 4)-- Testing thread $core with stress-ng $(tput sgr0)" | tee -a $output_log_file
    for method in "${light[@]}"; do
        # light tests
        echo "$(tput setaf 2)- Testing with method $method on thread $core for $light_time (light) $(tput sgr0)" | tee -a $output_log_file
        stress-ng --cpu 1 --taskset $core --timeout $light_time  --cpu-method "$method"
        check_errors
        sleep $light_time
    done
    for method in "${mixed[@]}"; do
        # medium tests
        echo "$(tput setaf 2)- Testing with method $method on thread $core for $medium_time (medium) $(tput sgr0)" | tee -a $output_log_file
        stress-ng --cpu 1 --taskset $core --timeout $medium_time --cpu-method "$method"
        check_errors
        sleep $medium_time
    done
    for method in "${heavy[@]}"; do
        # heavy tests
        echo "$(tput setaf 2)- Testing with method $method on thread $core for $heavy_time (heavy) $(tput sgr0)" | tee -a $output_log_file
        stress-ng --cpu 1 --taskset $core --timeout $heavy_time --cpu-method "$method"
        check_errors
        sleep $rest_time
    done
}