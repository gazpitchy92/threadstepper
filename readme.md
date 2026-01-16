# ThreadStepper

A stability and stress tester for linux which applies varying levels of stress to individual CPU cores or threads to emulate real-world usage patterns. Utilizes 7z benchmarking, stress-ng, and WebGL browser tests built with three.js.

This tool was developed specifically for testing undervolting and Ryzen Curve Optimizer (CO) configurations, where conventional stress tests often fail to detect instabilities.

![threadstepper](https://iili.io/KVveDMl.png)
![terminal](https://iili.io/KVvUF5P.png)

## Latest Updates - Version 1.3

- Feature: Live error checking during all tests
- Feature: Logging of highest CPU clocks
- Feature: Better debug output during tests
- Feature: Improved settings and install.sh script

- Bug Fix: CPU topoloy for "cores" test is now correct
- Bug Fix: all_core_time is now correctly followed correctly
- Bug Fix: latest ungoogled-chromium setup for improved testing

## Requirements

- stress-ng
- p7zip

## Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/gazpitchy92/threadstepper.git
   cd threadstepper
   ```

2. **Install dependencies:**
   ```bash
   chmod +x install.sh
   sudo ./install.sh
   ```
   
   The install script will automatically install stress-ng, p7zip, and download the required ungoogled-chromium AppImage for WebGL tests.

## Usage

### Basic Syntax
```bash
./threadstepper [-l loops] [-t type] [-b browsers] [--first-half] [--second-half]
```

### Examples

**Basic test with default settings:**
```bash
./threadstepper
```

**Custom test with 2 loops, testing all threads, using 2 browsers:**
```bash
./threadstepper -l 2 -t threads -b 2
```

### Options

| Option | Description | Default |
|--------|-------------|---------|
| `-l` | Number of test loops to perform | 1 |
| `-t` | Test type: `cores` or `threads` | cores |
| `-b` | Number of browsers to launch (0 to skip WebGL tests) | 2 |
| `--first-half` | Tests only the first half of cores/threads (skips 7z tests) | - |
| `--second-half` | Tests only the second half of cores/threads (skips 7z tests) | - |
| `--help` | Show help menu | - |

## Configuration

Additional test settings can be modified in `settings.sh`. The defaults are suitable for most use cases.

### General
Used for base configuration
```bash
ts_version="1.3"
settings_dir=$(pwd)
output_log_file="$settings_dir/logs/output.log"
```

### Test Durations
These are the time settings for each stress type.
```bash
light_time="1s"
medium_time="5s" 
heavy_time="15s"
all_core_time=15
rapid_tests=2
rapid_time="2s"
rest_time=5
```

### Stress Test Methods
These are the test methods ran against each of the time settings, they are stress-ng methods.
```bash
light=("bitops" "pi" "gcd" "sieve")
mixed=("prime" "matrixprod" "fft" "loop")
heavy=("ackermann" "factorial")
rapid="bitops"
```

### Browser config
These are the browser test settings. Also used in install.sh
```bash
chromium_version="144.0.7559.59-1"
chromium_appimage="ungoogled-chromium-$chromium_version-x86_64.AppImage"
chromium_domain="https://github.com/ungoogled-software/ungoogled-chromium-portablelinux/releases/download"
chromium_flags="--new-window --ozone-platform=x11 --no-sandbox --disable-gpu-sandbox --disable-dev-shm-usage --disable-gpu-compositing --disable-accelerated-2d-canvas --disable-accelerated-video-decode --disable-accelerated-video-encode --disable-webgl2 --num-raster-threads=1 --incognito"
```

## Logging

Logging is processed in a background script - logs/logger.sh
All test output is saved to loged/output.log
Error logs are saved into logs/errors.log
Highest recorded CPU is logged to logs/clock.log 

## Additional Notes

While stress-ng includes built-in test validation (used by ThreadStepper), running OCCT in Monitor mode alongside the tests can improve error detection capabilities.
