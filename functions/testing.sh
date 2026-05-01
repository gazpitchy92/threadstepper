#!/bin/bash

# main test runner
runTests(){
    local core=$1
    stressNgCore $core
    check_errors
    if (( browsers != 0 )); then
        # browsers
        browserTest
        stressNgCore $core
        stopBrowserTest
        check_errors
    fi 
}

# Updates progress file for UI
update_progress(){ 
    local test=$1
    local test_loop=$2
    local test_outof=$3
    local all_loop=$4
    local all_outof=$5
    echo "${test} ${test_loop}/${test_outof} , ${all_loop}/${all_outof}" > $output_progress_file
}