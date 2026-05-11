#!/bin/bash

# setup clean log files
setup_logs() {
    echo ""
    rm -f $output_log_file
    rm -f prime.txt
    touch $output_log_file
}

# initial test output
initial_output() {
    output_options
    print_topology
    check_deps
    echo "STARTING TESTS IN ${rest_time} seconds..."
    sleep $rest_time
    setup_logs
    start_logger
}

# output usage help
usage_text() {
    echo "Usage: $0 [-l loops] [-t type (cores|threads)] [-b number of WebGL tests] [--second-half] [--first-half]"
}

# check dependencies
check_deps() {
    if command -v $(compgen -c | grep '^electron[0-9]' | sort -V | tail -1) &>/dev/null; then
        echo "$(tput setaf 2)Electron Found - WebGL Tests Enabled$(tput sgr0)"
        echo "$(tput setaf 2)Using version: $(which $electon_bin)"
    else
        echo "$(tput setaf 1)!!!!! Electron not found !!!!!$(tput sgr0)"
        echo "$(tput setaf 1)!!!!! WebGL Tests are Disabled !!!!!$(tput sgr0)"
        echo "$(tput setaf 1)!!!!! Please select the 'Install Dependencies' button (top right) !!!!!$(tput sgr0)"
    fi
    echo ""
}

# output selected options and settings
output_options() {
    echo ""
    echo "$(tput setaf 6)Options" | tee -a $output_log_file
    echo "$(tput setaf 5)Loops: ${loops:-Not specified} $(tput sgr0)" | tee -a $output_log_file
    echo "$(tput setaf 5)Browsers: ${browsers:-Not specified} $(tput sgr0)" | tee -a $output_log_file
    echo "$(tput setaf 5)Core blacklist: ${core_blacklist} $(tput sgr0)" | tee -a $output_log_file
    echo "$(tput setaf 5)CPU topology: ${cpu_topology} $(tput sgr0)" | tee -a $output_log_file
    echo ""
    echo "$(tput setaf 6)Test Settings" | tee -a $output_log_file
    echo "$(tput setaf 5)Light time: ${light_time}s $(tput sgr0)" | tee -a $output_log_file
    echo "$(tput setaf 5)Medium time: ${medium_time}s $(tput sgr0)" | tee -a $output_log_file
    echo "$(tput setaf 5)Heavy time: ${heavy_time}s $(tput sgr0)" | tee -a $output_log_file
    echo "$(tput setaf 5)All core time: ${all_core_time}s $(tput sgr0)" | tee -a $output_log_file
    echo "$(tput setaf 5)All core time: ${all_core_tests}s $(tput sgr0)" | tee -a $output_log_file
    echo "$(tput setaf 5)Rapid tests: ${rapid_tests} $(tput sgr0)" | tee -a $output_log_file
    echo "$(tput setaf 5)Rapid time: ${rapid_time}s $(tput sgr0)" | tee -a $output_log_file
    echo "$(tput setaf 5)Random tests: ${random_tests} $(tput sgr0)" | tee -a $output_log_file
    echo "$(tput setaf 5)Random time: ${random_time}s $(tput sgr0)" | tee -a $output_log_file
    echo "$(tput setaf 5)Rest time: ${rest_time}s $(tput sgr0)" | tee -a $output_log_file
}

# cleanup exit of program
cleanup() {
    if [[ -z "$cleaned_up" ]]; then
        cleaned_up=1
        stop_logger
        stop_stressor
        kill_phase
        stop_browser_test
        pkill -f "launch.js"
        pkill -f "bash -c"
        pkill -f "load_test.sh"
        pkill -f "load_worker.sh"
        exit
    fi
}

# keep a log of the highest CPU clock
start_logger() {
    current_dir=$(pwd)
    bash "$current_dir/functions/logger.sh" &
    echo $! > "$current_dir/logs/logger.pid"
}
stop_logger() {
    if [[ -f "$current_dir/logs/logger.pid" ]]; then
        kill "$(cat "$current_dir/logs/logger.pid")" 2>/dev/null
        rm -f "$current_dir/logs/logger.pid"
    fi
}

# Sleep function
rest() {
    echo "$(tput setaf 3)Resting for ${rest_time}s$(tput sgr0)" 
    sleep $rest_time
}

