#!/bin/bash


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
  LOG_PRIORITY="err"

  ERRORS=$(journalctl --since="@${START_TIME}" -p "$LOG_PRIORITY" --no-pager -q 2>/dev/null)
  [ "$ERRORS" = "-- No entries --" ] && ERRORS=""

  ERRORS_DUMPED=$(journalctl --since="@${START_TIME}" --no-pager | grep -i "dumped core")
  ERRORS_SEGFAULT=$(journalctl --since="@${START_TIME}" --no-pager | grep -i "segfault")

  COREDUMPS=$(coredumpctl --since "@${START_TIME}" list --no-pager 2>/dev/null)
  [ -z "$COREDUMPS" ] && COREDUMPS=""

  if [ -n "$ERRORS" ] || [ -n "$ERRORS_DUMPED" ] || [ -n "$ERRORS_SEGFAULT" ] || [ -n "$COREDUMPS" ]; then
    {
      echo "true"
      echo "=== Errors detected at $(date -Iseconds) ==="
      [ -n "$ERRORS" ] && echo "$ERRORS"
      [ -n "$ERRORS_DUMPED" ] && echo "$ERRORS_DUMPED"
      [ -n "$ERRORS_SEGFAULT" ] && echo "$ERRORS_SEGFAULT"
      [ -n "$COREDUMPS" ] && echo "=== Coredumps ===" && echo "$COREDUMPS"
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