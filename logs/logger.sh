#!/bin/bash

SEARCH_PATTERN='Hardware Error|mce:|EDAC|Machine Check Exception|CPU.*thermal|thermal.*throttle|Out of memory|OOM|killed process|segmentation fault|general protection fault|BUG:|kernel panic|NMI watchdog|soft lockup|hard lockup|RIP:|Call Trace'
LOG_PRIORITY="err"
CURRENT_DIR=$(pwd)
ERROR_LOG="$CURRENT_DIR/logs/errors.log"
CLOCK_LOG="$CURRENT_DIR/logs/clock.log"
START_TIME=$(date +%s)

mkdir -p "$CURRENT_DIR/logs"
echo "0" > "$CLOCK_LOG"
echo "false" > "$ERROR_LOG"

loggerCpuClock() {
  max=0
  for f in /sys/devices/system/cpu/cpu*/cpufreq/scaling_cur_freq; do
    v=$(<"$f")
    (( v > max )) && max=$v
  done
  ghz=$(awk "BEGIN { printf \"%.3f\", $max / 1000000 }")
  last=$(<"$CLOCK_LOG")
  awk -v cur="$ghz" -v last="$last" 'BEGIN { exit !(cur > last) }' && {
    printf "%s\n" "$ghz" > "$CLOCK_LOG"
  }
}

loggerErrorCheck() {
  ERRORS=$(journalctl --since="@${START_TIME}" -p "$LOG_PRIORITY" --no-pager -q 2>/dev/null | grep -Ei "$SEARCH_PATTERN")
  ERRORS_DUMPED=$(journalctl --since="@${START_TIME}" --no-pager | grep -i "dumped core")
  ERRORS_SEGFAULT=$(journalctl --since="@${START_TIME}" --no-pager | grep -i "segfault")

  if [ -n "$ERRORS" ] || [ -n "$ERRORS_DUMPED" ] || [ -n "$ERRORS_SEGFAULT" ]; then
    {
      echo "true"
      echo "=== Errors detected at $(date -Iseconds) ==="
      [ -n "$ERRORS" ] && echo "$ERRORS"
      [ -n "$ERRORS_DUMPED" ] && echo "$ERRORS_DUMPED"
      [ -n "$ERRORS_SEGFAULT" ] && echo "$ERRORS_SEGFAULT"
      echo "========================================"
    } > "$ERROR_LOG"
    exit 1
  fi
}

while :; do
  loggerCpuClock
  loggerErrorCheck
  sleep 2
done