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
  EXCLUDE=("libinput" "bluetooth" "cityfailed" "plasmashell" "mouse" "keyboard" "chrome" "firefox" "librewold" "floorp" "discord" "brave" "electron" "udev")

  ERRORS_HARDWARE=$(journalctl --since="@${START_TIME}" -p "$LOG_PRIORITY" -k --no-pager -q 2>/dev/null | grep -E 'MCE|Machine Check|Hardware Error|EDAC|ECC|NVRM|Xid|amdgpu|i915|GPU fault|GPU HANG')
  ERRORS_FLAG=$(journalctl --since="@${START_TIME}" -p "$LOG_PRIORITY" --no-pager -q 2>/dev/null)
  ERRORS_DUMPED=$(journalctl --since="@${START_TIME}" --no-pager | grep -i "dumped core")
  ERRORS_SEGFAULT=$(journalctl --since="@${START_TIME}" --no-pager | grep -i "segfault")

  COREDUMPS=$(coredumpctl --since "@${START_TIME}" list --no-pager 2>/dev/null | awk 'gsub(/ /,"")>=5')
  [ -z "$COREDUMPS" ] && COREDUMPS=""

  for word in "${EXCLUDE[@]}"; do
    ERRORS_HARDWARE=$(echo "$ERRORS_HARDWARE" | grep -vi "$word")
    ERRORS_FLAG=$(echo "$ERRORS_FLAG" | grep -vi "$word")
    ERRORS_DUMPED=$(echo "$ERRORS_DUMPED" | grep -vi "$word")
    ERRORS_SEGFAULT=$(echo "$ERRORS_SEGFAULT" | grep -vi "$word")
    COREDUMPS=$(echo "$COREDUMPS" | grep -vi "$word")
  done

  ERRORS_HARDWARE=$(echo "$ERRORS_HARDWARE" | awk 'gsub(/ /,"")>=5')
  ERRORS_FLAG=$(echo "$ERRORS_FLAG" | awk 'gsub(/ /,"")>=5')
  ERRORS_DUMPED=$(echo "$ERRORS_DUMPED" | awk 'gsub(/ /,"")>=5')
  ERRORS_SEGFAULT=$(echo "$ERRORS_SEGFAULT" | awk 'gsub(/ /,"")>=5')

  if [ -n "$ERRORS_DUMPED" ] || [ -n "$ERRORS_SEGFAULT" ] || [ -n "$COREDUMPS" ] || [ -n "$ERRORS_FLAG" ] || [ -n "$ERRORS_HARDWARE" ]; then
    {
      echo "=== Errors detected at $(date -Iseconds) ==="
      [ -n "$ERRORS_HARDWARE" ] && echo "$ERRORS_HARDWARE"
      [ -n "$ERRORS_FLAG" ] && echo "$ERRORS_FLAG"
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