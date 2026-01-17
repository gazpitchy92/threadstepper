#!/bin/bash

ts_version="2.0"
settings_dir=$(pwd)
output_log_file="$settings_dir/logs/output.log"

# test settings
loops=1
type="cores"
second_half=false
first_half=false
browsers=4

# stress test types from stress-ng
light=("bitops" "pi" "gcd" "sieve")
mixed=("prime" "matrixprod" "fft" "loop")
heavy=("ackermann" "factorial")
rapid="bitops"

# stress test times
light_time="5s" 
medium_time="10s" 
heavy_time="10s" 
all_core_time=10
rapid_tests=5
rapid_time="1s"
rest_time=2

# chromium browser test config
# re-install dependancies if changed
chromium_version="144.0.7559.59-1"
chromium_appimage="ungoogled-chromium-$chromium_version-x86_64.AppImage"
chromium_domain="https://github.com/ungoogled-software/ungoogled-chromium-portablelinux/releases/download"
chromium_flags="--new-window --ozone-platform=x11 --no-sandbox --disable-gpu-sandbox --disable-dev-shm-usage --disable-gpu-compositing --disable-accelerated-2d-canvas --disable-accelerated-video-decode --disable-accelerated-video-encode --disable-webgl2 --num-raster-threads=1 --incognito"


