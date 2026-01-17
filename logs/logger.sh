#!/bin/bash

SEARCH_PATTERN='Hardware Error.*CPU|Hardware Error.*Machine Check|mce:.*error|mce:.*exception|EDAC.*corrected|EDAC.*uncorrected|Machine Check Exception|CPU.*thermal|thermal.*throttle|Out of memory|OOM|killed process|segmentation fault|general protection fault|BUG:|kernel panic|NMI watchdog|soft lockup|hard lockup|RIP:|Call Trace'
LOG_PRIORITY="err"
CURRENT_DIR=$(pwd)
ERROR_LOG="$CURRENT_DIR/logs/errors.log"
CLOCK_LOG="$CURRENT_DIR/logs/clock.log"
START_TIME=$(date +%s)

mkdir -p "$CURRENT_DIR/logs"
echo "0" > $CLOCK_LOG
echo "false" > $ERROR_LOG

# Highest CPU clock
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

# Error checking
loggerErrorCheck() {
  ERRORS=$(journalctl --since="@${START_TIME}" \
          -p "$LOG_PRIORITY" \
          -g "$SEARCH_PATTERN" \
          --no-pager \
          -q \
          2>/dev/null)
  if [ -n "$ERRORS" ]; then
    {
      echo "true"
      echo "=== Errors detected at $(date -Iseconds) ==="
      echo "$ERRORS"
      echo "========================================"
    } > "$ERROR_LOG"
  fi
}

while :; do
  loggerCpuClock
  loggerErrorCheck
  sleep 0.25
done