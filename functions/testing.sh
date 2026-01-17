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