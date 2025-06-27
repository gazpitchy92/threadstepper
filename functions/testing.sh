#!/bin/bash

# main test running function
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

# rapid thread tests
rapidStressNgThread() {
    rapid_num_cores=$(nproc)
    echo "$(tput setaf 4)-- Testing all threads with rapid $rapid for $rapid_tests loops $(tput sgr0)" | tee -a log.txt
    for ((core=$start_core; core<rapid_num_cores; core++)); do
        echo "$(tput setaf 2)- Testing with method $rapid on thread $core for $rapid_time (rapid) $(tput sgr0)" | tee -a log.txt
        stress-ng --cpu 1 --taskset $core --timeout $rapid_time --cpu-method "$rapid"
    done
}
# rapid core tests
rapidStressNgCore() {
    rapid_num_cores=$(nproc)
    echo "$(tput setaf 4)-- Testing all cores with rapid $rapid for $rapid_tests loops $(tput sgr0)" | tee -a log.txt
    for ((core=$start_core; core<rapid_num_cores; core+=2)); do
        core_second=$((core + 1))
        echo "$(tput setaf 2)- Testing with method $rapid on core core ( $core + $core_second ) for $rapid_time (rapid) $(tput sgr0)" | tee -a log.txt
        stress-ng --cpu 2 --taskset $core,$core_second --timeout $rapid_time --cpu-method "$rapid"
    done
}

# stress-ng testing of threads
stressNgThread() {
    local core=$1
    echo "$(tput setaf 4)-- Testing thread $core with stress-ng $(tput sgr0)" | tee -a log.txt
    for method in "${light[@]}"; do
        # light tests
        echo "$(tput setaf 2)- Testing with method $method on thread $core for $light_time (light) $(tput sgr0)" | tee -a log.txt
        stress-ng --cpu 1 --taskset $core --timeout $light_time  --cpu-method "$method"
        sleep $light_time
    done
    for method in "${mixed[@]}"; do
        # medium tests
        echo "$(tput setaf 2)- Testing with method $method on thread $core for $medium_time (medium) $(tput sgr0)" | tee -a log.txt
        stress-ng --cpu 1 --taskset $core --timeout $medium_time --cpu-method "$method"
        sleep $medium_time
    done
    for method in "${heavy[@]}"; do
        # heavy tests
        echo "$(tput setaf 2)- Testing with method $method on thread $core for $heavy_time (heavy) $(tput sgr0)" | tee -a log.txt
        stress-ng --cpu 1 --taskset $core --timeout $heavy_time --cpu-method "$method"
        sleep $rest_time
    done
}
# stress-ng testing of cores
stressNgCore() {
    local core=$1
    local core_second=$((core + 1))
    echo "$(tput setaf 4)-- Testing core ( $core + $core_second ) with stress-ng $(tput sgr0)" | tee -a log.txt
    for method in "${light[@]}"; do
        # light tests
        echo "$(tput setaf 2)- Testing with method $method on core ( $core + $core_second ) for $light_time (light) $(tput sgr0)" | tee -a log.txt
        stress-ng --cpu 2 --taskset $core,$core_second --timeout $light_time --cpu-method "$method"
        sleep $light_time
    done
    for method in "${mixed[@]}"; do
        # medium tests
        echo "$(tput setaf 2)- Testing with method $method on core ( $core + $core_second ) for $medium_time (medium) $(tput sgr0)" | tee -a log.txt
        stress-ng --cpu 2 --taskset $core,$core_second --timeout $medium_time --cpu-method "$method"
        sleep $medium_time
    done
    for method in "${heavy[@]}"; do
        # heavy tests
        echo "$(tput setaf 2)- Testing with method $method on core ( $core + $core_second ) for $heavy_time (heavy) $(tput sgr0)" | tee -a log.txt
        stress-ng --cpu 2 --taskset $core,$core_second --timeout $heavy_time --cpu-method "$method"
        sleep $rest_time
    done
}

# full cpu 7zip stress
allCoreTest() {
    all_core_time=15
    echo "$(tput setaf 4)-- Running 7z warmup on all cores $(tput sgr0)" | tee -a log.txt
    for i in $(seq 1 $all_core_time); do
        # increase test time by 1s until $all_core_time
        echo "$(tput setaf 2)- Running 7z for $i seconds $(tput sgr0)" | tee -a log.txt
        7z b > /dev/null 2>&1 &
        sleep "$i"
        pkill 7z
        sleep $rest_time
    done
}

# open browsers for web-gl cpu stress
browserTest() {
    current_dir=$(pwd)
    for ((i = 0; i < browsers; i++)); do
        random_page=$((RANDOM % 6 + 1))
        file_path="file://$current_dir/tests/browser/pages/$random_page.html"
        if [[ "$first_half" == true || "$second_half" == true ]]; then
            # testing half of cpu
            num_cores=$(nproc)
            half_cores=$((num_cores / 2))
            if [[ "$first_half" == true ]]; then
                # first half of cpu
                echo "$(tput setaf 4)-- Launching $browsers browsers on cores ( 0-$((half_cores - 1)) )$(tput sgr0)" | tee -a log.txt
                taskset -c 0-$((half_cores - 1)) ./tests/browser/ungoogled-chromium_133.0.6943.126-1.AppImage --new-window --disable-gpu --disable-accelerated-video-decode "$file_path" > /dev/null 2>&1 &
            fi
            if [[ "$second_half" == true ]]; then
                # second half of cpu
                echo "$(tput setaf 4)-- Launching $browsers browsers on cores ( $half_cores-$((num_cores - 1)) )$(tput sgr0)" | tee -a log.txt
                taskset -c $half_cores-$((num_cores - 1)) ./tests/browser/ungoogled-chromium_133.0.6943.126-1.AppImage --new-window --disable-gpu --disable-accelerated-video-decode "$file_path" > /dev/null 2>&1 &
            fi
        else
            # testing all cpu
            echo "$(tput setaf 4)-- Launching $browsers browsers on all cores$(tput sgr0)" | tee -a log.txt
            ./tests/browser/ungoogled-chromium_133.0.6943.126-1.AppImage --new-window --disable-gpu --disable-accelerated-video-decode "$file_path" > /dev/null 2>&1 &
            sleep $rest_time
        fi
    done
}
stopBrowserTest(){
    # kill running browser tests
    pgrep -f "ungoogled-chromium_133.0.6943.126-1.AppImage" | while read -r pid; do
        kill -9 "$pid" &>/dev/null
    done
    pkill ungoogled-chromium_133.0.6943.126-1.AppImage &>/dev/null
    pkill chrome &>/dev/null
}