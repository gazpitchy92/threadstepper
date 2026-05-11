#!/bin/bash

# main test runner
run_tests() {
    local core=$1
    update_progress "Single Core Tests" $loop_counter $loops 
    single_core_tests $core
    check_errors
    if (( browsers != 0 )); then
        if compgen -c | grep -q '^electron[0-9]'; then
            update_progress "WebGL Tests" $loop_counter $loops
            if will_run_browser_test "$core"; then
                browser_test
                single_core_tests $core
                stop_browser_test
            fi
            check_errors
        else
            echo "$(tput setaf 8)[DEBUG] Skipping WebGL tests: Electron not found$(tput sgr0)" | tee -a "$output_log_file"
        fi
    fi
}

# All core test
all_core_runner() {
    for ((all_core_counter=1; all_core_counter<=all_core_tests; all_core_counter++)); do
        update_progress "All Core ${all_core_counter}/${all_core_tests}" $loop_counter $loops 
        alkl_core_test
        check_errors
        rest
    done
}

# Rapid tests
rapid_runner() {
    for ((rapid_counter=1; rapid_counter<=rapid_tests; rapid_counter++)); do
        echo "$(tput setaf 4)Running rapid test "$rapid_counter"/"$rapid_tests"$(tput sgr0)" | tee -a "$output_log_file"
        update_progress "Rapid Tests ${rapid_counter}/${rapid_tests}" $loop_counter $loops 
        rapid_test
        check_errors
        rest
    done
}

# Rand tests
rand_runner() {
    for ((random_counter=1; random_counter<=random_tests; random_counter++)); do
        echo "$(tput setaf 4)Running random test "$random_counter"/"$random_tests"$(tput sgr0)" | tee -a "$output_log_file"
        update_progress "Rand Tests ${random_counter}/${random_tests}" $loop_counter $loops 
        random_stress
        check_errors
        rest
    done
}

single_core_runner() {
    local start_core=$1
    local end_core=$2
    for ((core=start_core; core<=end_core; core++)); do
        # Vars
        local core_second=$((core + physical_cores))
        local core_next=$((core + 1))
        local core_last=$((core_second + 1))
        # Start output
        if [[ ",$cpu_topology," == *"0"* ]]; then
            echo "$(tput setaf 3)Starting tests for threads [$core + $core_next + $core_second + $core_last] of core [$core]$(tput sgr0)" | tee -a "$output_log_file"
        fi
        if [[ ",$cpu_topology," == *"1"* ]]; then
            echo "$(tput setaf 3)Starting tests for threads [$core + $core_second] of core [$core]$(tput sgr0)" | tee -a "$output_log_file"
        fi
        if [[ ",$cpu_topology," == *"2"* ]]; then
            echo "$(tput setaf 3)Starting tests for threads [$core + $core_next] of core [$core]$(tput sgr0)" | tee -a "$output_log_file"
        fi
        # Start on core
        rest
        run_tests "$core"
        highest_clock="$(<"$current_dir/logs/clock.log") Ghz"
        # End output
        if [[ ",$cpu_topology," == *"0"* ]]; then
            echo "$(tput setaf 3)Finished tests for threads [$core + $core_next + $core_second + $core_last] of core [$core]$(tput sgr0)" | tee -a "$output_log_file"
        fi
        if [[ ",$cpu_topology," == *"1"* ]]; then
            echo "$(tput setaf 3)Finished tests for threads [$core + $core_second] of [core $core]$(tput sgr0)" | tee -a "$output_log_file"
        fi
        if [[ ",$cpu_topology," == *"2"* ]]; then
            echo "$(tput setaf 3)Finished tests for threads [$core + $core_next] of core [$core]$(tput sgr0)" | tee -a "$output_log_file"
        fi
        # Finish with core
        echo "$(tput setaf 8)[DEBUG] Highest CPU Clock: $highest_clock" | tee -a "$output_log_file"
        check_errors
        rest
    done
}

# Updates progress file for UI
update_progress() { 
    local test=$1
    local all_loop=$2
    local all_outof=$3
    echo "${test}" > "$output_progress_file"
    echo "Test Run ${all_loop}/${all_outof}" >> "$output_progress_file"
}

# Update current threads being tested
update_threads() {
    local threads=$1
    echo "${threads}" > "$output_threads_file"
}