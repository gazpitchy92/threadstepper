#!/bin/bash

# setup clean log files
setupLogs(){
    echo ""
    rm -f $output_log_file
    rm -f prime.txt
    touch $output_log_file
}

# initial test output
initial_output() {
    outputOptions
    print_topology
    checkDeps
    echo "STARTING TESTS IN ${rest_time} SECONDS..."
    sleep $rest_time
    setupLogs
    starLogger
}

# output help
helpText(){
    echo ""
    usageText
    echo ""
    echo "-l                number of Test Runs to perform (default: 1)"
    echo "-t                'cores' tests all cores"
    echo "                  'threads' tests all threads (default: cores)"
    echo "-b                number of browsers to launch (default: 2) (0 to skip test)"
    echo "--first-half      tests the first half of the cores/threads"
    echo "--second-half     tests the second half of the cores/threads"
    echo "--help            show this help menu"
    echo ""
    echo "Additional test settings can be found in settings"
    echo ""
}

# output usage help
usageText(){
    echo "Usage: $0 [-l loops] [-t type (cores|threads)] [-b number of browsers] [--second-half] [--first-half]"
}

# check dependencies
checkDeps(){
    if command -v $(compgen -c | grep '^electron[0-9]' | sort -V | tail -1) &>/dev/null; then
        echo "$(tput setaf 2)Electron Found - Browser Tests Enabled$(tput sgr0)"
    else
        echo "$(tput setaf 1)!!!!! Electron not found !!!!!$(tput sgr0)"
        echo "$(tput setaf 1)!!!!! Browser Tests are Disabled !!!!!$(tput sgr0)"
        echo "$(tput setaf 1)!!!!! Please select the 'Install Dependencies' button (top right) !!!!!$(tput sgr0)"
    fi
    echo ""
}

# output selected options and settings
outputOptions(){
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
    if [[ -z "$CLEANED_UP" ]]; then
        CLEANED_UP=1
        echo "$(tput setaf 5)Stopping tests and cleaning up $(tput sgr0)" | tee -a $output_log_file
        stopLogger
        stop_stressor
        kill_phase
        pkill load_worker.sh
        stopBrowserTest
        pkill -f "launch.js"
        exit
    fi
}

# keep a log of the highest CPU clock
starLogger() {
    current_dir=$(pwd)
    bash "$current_dir/logs/logger.sh" &
    echo $! > "$current_dir/logs/logger.pid"
}
stopLogger() {
    if [[ -f "$current_dir/logs/logger.pid" ]]; then
        kill "$(cat "$current_dir/logs/logger.pid")"
        rm -f "$current_dir/logs/logger.pid"
    fi
}

rest() {
    echo "$(tput setaf 3)Resting for ${rest_time}s$(tput sgr0)" 
    sleep $rest_time
}

