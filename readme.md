# Thread Stepper

A stability and stress tester for AMD Curve Optimizer and PBO on Linux.

Designed specifically for testing undervolting and boost stability, where conventional stress tests often fail.

## Latest Updates - Version 2.1

- New GUI interface!
- Better live error checking.
- Logging of highest CPU clocks.
- Improved CPU topology testing.
- Improved settings and install.sh script.
- Improved testing methods for faster error detection.

## Screenshots

![running](https://iili.io/fUTdO21.png)
![errors](https://iili.io/fUT27wJ.png)

## Methodology

### Problem with Traditional Stress Tests

Most stress tests (Prime95, OCCT) apply continuous, predictable load across all cores simultaneously. This is good for thermal testing but misses instabilities that appear during normal use, particularly with undervolting.

### How Thread Stepper Works

**Variable Load Patterns**  
Applies light, medium, and heavy loads in varying durations and rapid transitions. This forces voltage/frequency changes where instability typically occurs.

**Sequential Core Testing**  
Tests individual cores and thread groups in sequence rather than loading all cores uniformly. Isolates per-core curve optimizer issues.

**Randomized Background Load**  
Uses 3D WebGL browser tests to generate unpredictable background activity during testing. Mimics real usage patterns where undervolts typically fail.

**Test Patterns**  
Cycles through different load combinations on each core and thread group, with configurable durations for light/medium/heavy workloads and rest periods between tests.

## Requirements

- stress-ng
- p7zip
- python
- Linux

## Installation

1. **Clone the repository:**
```bash
   git clone https://github.com/gazpitchy92/threadstepper.git
   cd threadstepper
   python start.py
```

2. **Install dependencies:**
   Via GUI (top right) or terminal:
```bash
   chmod +x install.sh
   sudo ./install.sh
```
   Installs stress-ng, p7zip, and downloads ungoogled-chromium AppImage for WebGL tests.

## Test Setup

All times in seconds. Default settings work for most users.

- **Loops**: Number of full test cycles
- **Light**: Duration of light load tests
- **Medium**: Duration of medium load tests
- **Heavy**: Duration of heavy load tests
- **Browsers**: Number of browser instances for background load
- **All Core**: Duration of all-core stress test
- **Rapid Time**: Duration of each rapid transition test
- **Rest**: Pause between tests
- **Core Blacklist**: Cores to skip (format: 1,5,10,14)