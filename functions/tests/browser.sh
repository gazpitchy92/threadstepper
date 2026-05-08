#!/bin/bash
browser_pids=()

browserTest() {
    current_dir=$(pwd)
    rm -rf "${current_dir}/tests/browser/tmp"
    rm -rf "${current_dir}/tests/browser/tmpfile:"
    mkdir -p "${current_dir}/tests/browser/tmp"
    echo "$(tput setaf 4)Launching $browsers browsers on all cores$(tput sgr0)" | tee -a $output_log_file
    echo "$(tput setaf 8)[DEBUG] Using electron: $(which $ELECTRON_BIN)"

    for ((i = 0; i < browsers; i++)); do
        random_page=$((RANDOM % 10 + 1))
        file_path="$current_dir/tests/browser/pages/$random_page.html"
        num_cores=$(nproc)
        half_cores=$((num_cores / 2))

        if (( browsers > 1 )); then
            if (( i % 2 == 0 )); then
                echo "$(tput setaf 3)[DEBUG Browser $((i+1))] taskset --cpu-list 0-$((half_cores - 1)) $file_path$(tput sgr0)" | tee -a $output_log_file
                update_threads "0-$((half_cores - 1))"
                taskset --cpu-list 0-$((half_cores - 1)) "$ELECTRON_BIN" "$current_dir/tests/browser/launch.js" "$file_path" > /dev/null 2>&1 &
                browser_pids+=($!)
            else
                echo "$(tput setaf 3)[DEBUG Browser $((i+1))] taskset --cpu-list $half_cores-$((num_cores - 1)) $file_path$(tput sgr0)" | tee -a $output_log_file
                update_threads "$half_cores-$((num_cores - 1))"
                taskset --cpu-list $half_cores-$((num_cores - 1)) "$ELECTRON_BIN" "$current_dir/tests/browser/launch.js" "$file_path" > /dev/null 2>&1 &
                browser_pids+=($!)
            fi
        else
            echo "$(tput setaf 8)[DEBUG] taskset --cpu-list 0-$((num_cores - 1)) $file_path$(tput sgr0)" | tee -a $output_log_file
            update_threads "0-$((num_cores - 1))"
            taskset --cpu-list 0-$((num_cores - 1)) "$ELECTRON_BIN" "$current_dir/tests/browser/launch.js" "$file_path" > /dev/null 2>&1 &
            browser_pids+=($!)
        fi
        rest
    done
}

stopBrowserTest() {
    for pid in "${browser_pids[@]}"; do
        kill "$pid" &>/dev/null
    done
    sleep 1
    for pid in "${browser_pids[@]}"; do
        kill -9 "$pid" &>/dev/null
    done
    browser_pids=()
}