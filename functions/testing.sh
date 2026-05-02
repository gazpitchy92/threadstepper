#!/bin/bash

# main test runner
runTests(){
    local core=$1
    update_progress "Singlew Core Tests" $loop_counter $loops 
    stressNgCore $core
    check_errors
    if (( browsers != 0 )); then
        # browsers
        update_progress "Browser Tests" $loop_counter $loops 
        browserTest
        stressNgCore $core
        stopBrowserTest
        check_errors
    fi 
}

# Updates progress file for UI
update_progress(){ 
    local test=$1
    local all_loop=$2
    local all_outof=$3
    echo "${test}" > "$output_progress_file"
    echo "Full Test Loop ${all_loop}/${all_outof}" >> "$output_progress_file"
}