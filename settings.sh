#!/bin/bash

# stress test types from stress-ng
light=("bitops" "pi" "gcd" "sieve")
mixed=("prime" "matrixprod" "fft" "loop")
heavy=("ackermann" "factorial")
rapid="bitops"

# stress test times
# Defaults (with browsers): 336s (per core or thread) - (45m for 8 cores) - (90m for 16 threads)
light_time="5s" # 32s - (64s browsers)
medium_time="15s" # 72s - (144s browsers)
heavy_time="30s" # 63s - (126s browsers)
all_core_time=15 # 120s
rapid_tests=5 # 80s (8 cores) - 160s (16 cores)
rapid_time="2s"
rest_time=3

# browser config
chromium_version="144.0.7559.59-1"
chromium_appimage="ungoogled-chromium-$chromium_version-x86_64.AppImage"
chromium_domain="https://github.com/ungoogled-software/ungoogled-chromium-portablelinux/releases/download"
