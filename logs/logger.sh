#!/bin/bash

current_dir=$(pwd)
last=0
echo "0.000" > "$current_dir/clock.log"

while :; do
  max=0
  for f in /sys/devices/system/cpu/cpu*/cpufreq/scaling_cur_freq; do
    v=$(<"$f")
    (( v > max )) && max=$v
  done

  ghz=$(awk "BEGIN { print $max / 1000000 }")

  awk -v cur="$ghz" -v last="$last" 'BEGIN { exit !(cur > last) }' && {
    printf "%s\n" "$ghz" > "$current_dir/clock.log"
    last="$ghz"
  }

  sleep 0.25
done