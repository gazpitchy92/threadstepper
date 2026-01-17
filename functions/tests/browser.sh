#!/bin/bash

# launch browsers for stressng
browserTest() {
    current_dir=$(pwd)
    rm -rf "${current_dir}/tests/browser/tmp"
    rm -rf "${current_dir}/tests/browser/tmpfile:"
    mkdir -p "${current_dir}/tests/browser/tmp"

    if [[ "$first_half" == true ]]; then
        echo "$(tput setaf 4)Launching $browsers browsers on cores ( 0-$((half_cores - 1)) )$(tput sgr0)" | tee -a $output_log_file
    elif [[ "$second_half" == true ]]; then
        echo "$(tput setaf 4)Launching $browsers browsers on cores ( $half_cores-$((num_cores - 1)) )$(tput sgr0)" | tee -a $output_log_file
    else
        echo "$(tput setaf 4)Launching $browsers browsers on all cores$(tput sgr0)" | tee -a $output_log_file
    fi
    echo "$(tput setaf 8)[DEBUG] Appimage $current_dir/tests/browser/$chromium_appimage"
    echo "$(tput setaf 8)[DEBUG] $chromium_flags --user-data-dir=$current_dir/tests/browser/tmp"
    
    for ((i = 0; i < browsers; i++)); do
        random_page=$((RANDOM % 6 + 1))
        file_path="file://$current_dir/tests/browser/pages/$random_page.html"
        if [[ "$first_half" == true || "$second_half" == true ]]; then
            # testing half of cpu
            num_cores=$(nproc)
            half_cores=$((num_cores / 2))
            if [[ "$first_half" == true ]]; then
                # first half of cpu
                echo "$(tput setaf 4)Launching $browsers browsers on cores ( 0-$((half_cores - 1)) )$(tput sgr0)" | tee -a $output_log_file
                echo "$(tput setaf 8)[DEBUG] taskset --cpu-list 0-$((half_cores - 1)) $file_path$(tput sgr0)" | tee -a $output_log_file
                taskset --cpu-list 0-$((half_cores - 1)) $current_dir/tests/browser/$chromium_appimage $chromium_flags --user-data-dir=$current_dir/tests/browser/tmp "$file_path" > /dev/null 2>&1 &
            fi
            if [[ "$second_half" == true ]]; then
                # second half of cpu
                echo "$(tput setaf 4)Launching $browsers browsers on cores ( $half_cores-$((num_cores - 1)) )$(tput sgr0)" | tee -a $output_log_file
                echo "$(tput setaf 8)[DEBUG] taskset --cpu-list $half_cores-$((num_cores - 1)) $file_path$(tput sgr0)" | tee -a $output_log_file
                taskset --cpu-list $half_cores-$((num_cores - 1)) $current_dir/tests/browser/$chromium_appimage $chromium_flags --user-data-dir=$current_dir/tests/browser/tmp "$file_path" > /dev/null 2>&1 &
            fi
            sleep $rest_time
        else
            # testing all cpu
            num_cores=$(nproc)
            half_cores=$((num_cores / 2))
            if (( browsers > 1 )); then
                if (( (i + 1) % 2 == 0 )); then
                    echo "$(tput setaf 3)[DEBUG Browser $((i+1))] taskset --cpu-list 0-$((half_cores - 1)) $file_path$(tput sgr0)" | tee -a $output_log_file
                    taskset --cpu-list 0-$((half_cores - 1)) $current_dir/tests/browser/$chromium_appimage $chromium_flags --user-data-dir=$current_dir/tests/browser/tmp "$file_path" > /dev/null 2>&1 &
                else
                    echo "$(tput setaf 3)[DEBUG Browser $((i+1))] taskset --cpu-list $half_cores-$((num_cores - 1)) $file_path$(tput sgr0)" | tee -a $output_log_file
                    taskset --cpu-list $half_cores-$((num_cores - 1)) $current_dir/tests/browser/$chromium_appimage $chromium_flags --user-data-dir=$current_dir/tests/browser/tmp "$file_path" > /dev/null 2>&1 &
                fi
            else
                echo "$(tput setaf 8)[DEBUG] taskset --cpu-list 0-$((num_cores - 1)) $file_path$(tput sgr0)" | tee -a $output_log_file
                taskset --cpu-list 0-$((num_cores - 1)) $current_dir/tests/browser/$chromium_appimage $chromium_flags --user-data-dir=$current_dir/tests/browser/tmp "$file_path" > /dev/null 2>&1 &
            fi
            sleep $rest_time
        fi
    done
}

stopBrowserTest(){
    # kill running browser tests
    pgrep -f "$chromium_appimage" | while read -r pid; do
        kill -9 "$pid" &>/dev/null
    done
    pkill $chromium_appimage &>/dev/null
    pkill chrome &>/dev/null
}