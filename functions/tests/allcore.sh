allCoreTest() {
    echo "$(tput setaf 4)Running cumulative all core test$(tput sgr0)" | tee -a "$output_log_file"
    total_cores=$(nproc)

    is_blacklisted() {
        local core=$1
        IFS=',' read -ra bl <<< "$core_blacklist"
        for b in "${bl[@]}"; do
            [[ "$core" == "$b" ]] && return 0
        done
        return 1
    }

    filter_cores() {
        local input=$1
        local filtered=()
        IFS=',' read -ra cores <<< "$input"
        for core in "${cores[@]}"; do
            is_blacklisted "$core" || filtered+=("$core")
        done
        echo "${filtered[*]}" | tr ' ' ','
    }

    for core in $(seq 0 $((total_cores - 1))); do
        cores_list=$(seq -s, 0 "$core")
        cores_list=$(filter_cores "$cores_list")
        [[ -z "$cores_list" ]] && echo "$(tput setaf 0)Skipping cores $cores_list due to core_blacklist$(tput sgr0)" | tee -a "$output_log_file" && continue
        echo "$(tput setaf 2)Stressing cores $cores_list for $all_core_time seconds$(tput sgr0)" | tee -a "$output_log_file"
        update_threads "$cores_list"
        taskset -c "$cores_list" 7z b > /dev/null 2>&1 &
        disown
        sleep "$all_core_time"
        check_errors
        pkill -9 7z > /dev/null 2>&1
    done

    for core in $(seq $((total_cores - 2)) -1 0); do
        cores_list=$(seq -s, 0 "$core")
        cores_list=$(filter_cores "$cores_list")
        [[ -z "$cores_list" ]] && echo "$(tput setaf 0)Skipping cores $cores_list due to core_blacklist$(tput sgr0)" | tee -a "$output_log_file" && continue
        echo "$(tput setaf 2)Stressing cores $cores_list for $all_core_time seconds$(tput sgr0)" | tee -a "$output_log_file"
        update_threads "$cores_list"
        taskset -c "$cores_list" 7z b > /dev/null 2>&1 &
        disown
        sleep "$all_core_time"
        check_errors
        pkill -9 7z > /dev/null 2>&1
    done

    for core in $(seq $((total_cores - 1)) -1 0); do
        cores_list=$(seq -s, "$core" $((total_cores - 1)))
        cores_list=$(filter_cores "$cores_list")
        [[ -z "$cores_list" ]] && echo "$(tput setaf 0)Skipping cores $cores_list due to core_blacklist$(tput sgr0)" | tee -a "$output_log_file" && continue
        echo "$(tput setaf 2)Stressing cores $cores_list for $all_core_time seconds$(tput sgr0)" | tee -a "$output_log_file"
        update_threads "$cores_list"
        taskset -c "$cores_list" 7z b > /dev/null 2>&1 &
        disown
        sleep "$all_core_time"
        check_errors
        pkill -9 7z > /dev/null 2>&1
    done
}