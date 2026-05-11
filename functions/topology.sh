#!/bin/bash

# Output topology
print_topology() {
    echo ""
    echo "============"
    echo "CPU Topology"
    echo "============"
    for core_dir in /sys/devices/system/cpu/cpu[0-9]*/topology/core_id; do
        cpu=$(echo "$core_dir" | grep -oP 'cpu\K[0-9]+')
        core_id=$(cat "$core_dir")
        siblings_raw=$(cat "/sys/devices/system/cpu/cpu${cpu}/topology/thread_siblings_list")
        first_sibling=$(echo "$siblings_raw" | tr ',' '\n' | sed 's/-.*//g' | sort -n | head -1)
        if [ "$cpu" -eq "$first_sibling" ]; then
            type="P"
        else
            type="HT"
        fi
        echo "Core ${core_id}  |  Thread ${cpu} (${type})"
    done | sort -t'|' -k1,1V -k2,2V
    echo "============"
    echo ""
}

# Set topology in settings
set_topology() {
    for core_dir in /sys/devices/system/cpu/cpu[0-9]*/topology/core_id; do
        cpu=$(echo "$core_dir" | grep -oP 'cpu\K[0-9]+')
        core_id=$(cat "$core_dir")
        siblings_raw=$(cat "/sys/devices/system/cpu/cpu${cpu}/topology/thread_siblings_list")
        first_sibling=$(echo "$siblings_raw" | tr ',' '\n' | sed 's/-.*//g' | sort -n | head -1)
        if [ "$cpu" -eq "$first_sibling" ]; then
            type="P"
        else
            type="HT"
        fi
        echo "Core ${core_id}  |  Thread ${cpu} (${type})"
    done | sort -t'|' -k1,1V -k2,2V
}