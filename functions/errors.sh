#!/bin/bash

check_errors() {
    CURRENT_DIR=$(pwd)
    ERROR_LOG="$CURRENT_DIR/logs/errors.log"
    first_line=$(head -n 1 "$ERROR_LOG")
    if [ "$first_line" != "false" ]; then
        echo "$(tput setaf 1)ERROR FOUND - STOPPING TEST! ($elapsed_formated)$(tput sgr0)" | tee -a $output_log_file
        tail -n +2 "$ERROR_LOG" | while IFS= read -r line; do
            echo "$(tput setaf 1)$line$(tput sgr0)" | tee -a $output_log_file
        done
        cleanup
    fi
}