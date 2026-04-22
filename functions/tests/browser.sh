#!/bin/bash

# launch browsers for stressng
browserTest() {
    current_dir=$(pwd)
    rm -rf "${current_dir}/tests/browser/tmp"
    rm -rf "${current_dir}/tests/browser/tmpfile:"
    mkdir -p "${current_dir}/tests/browser/tmp"

    echo "$(tput setaf 4)Launching $browsers browsers on all cores$(tput sgr0)" | tee -a $output_log_file
    echo "$(tput setaf 8)[DEBUG] Appimage $current_dir/tests/browser/$chromium_appimage"
    echo "$(tput setaf 8)[DEBUG] $chromium_flags --user-data-dir=$current_dir/tests/browser/tmp"
    
    for ((i = 0; i < browsers; i++)); do
        random_page=$((RANDOM % 6 + 1))
        file_path="file://$current_dir/tests/browser/pages/$random_page.html"
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
    done
}

stopBrowserTest(){
    # Terminate chrome first, avoiding coredump cause by Appimage FUSE teardown race condition
    pkill chrome &>/dev/null
    sleep 1
    
    # kill running browser tests
    pgrep -f "$chromium_appimage" | while read -r pid; do
        kill -9 "$pid" &>/dev/null
    done
    pkill $chromium_appimage &>/dev/null
}
