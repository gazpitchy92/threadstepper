# ThreadStepper

A stability and stress tester for linux which applies varying levels of stress to individual CPU cores or threads to emulate real-world usage patterns. Utilizes 7z benchmarking, stress-ng, and WebGL browser tests built with three.js.

This tool was developed specifically for testing undervolting and Ryzen Curve Optimizer (CO) configurations, where conventional stress tests often fail to detect instabilities.

![threadstepper](https://iili.io/KVveDMl.png)
![terminal](https://iili.io/KVvUF5P.png)

## Requirements

- Linux system
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

### Stress Test Methods
```bash
light=("bitops" "pi" "gcd" "sieve")
mixed=("prime" "matrixprod" "fft" "loop")
heavy=("ackermann" "factorial")
rapid="bitops"
```

### Test Durations
```bash
light_time="1s"
medium_time="5s" 
heavy_time="15s"
all_core_time=15
rapid_tests=2
rapid_time="2s"
rest_time=5
```

## Logging

Test logs are generated in `./log.txt` and replaced with each new run.

## Additional Notes

While stress-ng includes built-in test validation (used by ThreadStepper), running OCCT in Monitor mode alongside the tests can improve error detection capabilities.
