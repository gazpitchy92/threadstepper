#!/bin/bash

check_errors() {
    current_dir=$(pwd)
    error_log="$current_dir/logs/errors.log"
    first_line=$(head -n 1 "$error_log")
    if [ "$first_line" != "false" ]; then
        echo "$(tput setaf 1)ERROR FOUND - STOPPING TEST!$(tput sgr0)" | tee -a $output_log_file
        tail -n +2 "$error_log" | while IFS= read -r line; do
            echo "$(tput setaf 1)$line$(tput sgr0)" | tee -a $output_log_file
        done
        cleanup
    fi
}