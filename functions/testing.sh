#!/bin/bash

# main test runner
runTests(){
    local core=$1
    update_progress "Single Core Tests" $loop_counter $loops 
    singleCoreTests $core
    check_errors
    if (( browsers != 0 )); then
        appimages=(./tests/browser/*.AppImage)
        if [ ${#appimages[@]} -gt 0 ]; then
            # browsers
            update_progress "Browser Tests" $loop_counter $loops
            browserTest
            singleCoreTests $core
            stopBrowserTest
            check_errors
        else
            echo "$(tput setaf 8)[DEBUG] Skipping browser tests: no AppImage found in ./tests/browser" | tee -a "$output_log_file"
        fi
    fi
}

# Updates progress file for UI
update_progress(){ 
    local test=$1
    local all_loop=$2
    local all_outof=$3
    echo "${test}" > "$output_progress_file"
    echo "Test Run ${all_loop}/${all_outof}" >> "$output_progress_file"
}

# Update current threads being tested
update_threads(){
    local threads=$1
    echo "${threads}" > "$output_threads_file"
}