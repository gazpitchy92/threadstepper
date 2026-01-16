#!/bin/bash

# main test runner
runTests(){
    local core=$1
    if [[ "$type" == "cores" ]]; then
        # cores
        stressNgCore $core
    else
        # threads
        stressNgThread $core
    fi
    if (( browsers != 0 )); then
        # launch browsers
        browserTest
        if [[ "$type" == "cores" ]]; then
            # cores
            stressNgCore $core
        else
            # threads
            stressNgThread $core
        fi
        # close browsers
        stopBrowserTest
    fi 
}