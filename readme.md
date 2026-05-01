# Thread Stepper

A stability and stress tester for AMD Curve Optimizer and PBO on Linux.

Designed specifically for testing undervolting and boost stability, where conventional stress tests often fail.

## Latest Updates - Version 2.8

- Improved UI and easier settings
- CPU topology detection (detection of threads per core)
- New beanchmarking tool
- New RAM testing functionality (built into the existing tests)

![memory](https://i.ibb.co/GfJqfkJW/memory.png)

- Easier core/thread selection

![threads](https://i.ibb.co/0yhzGcKY/cores.png)


## Screenshots

![running](https://i.ibb.co/9HXcfygt/Screenshot-20260501-234328.png)
![errors](https://i.ibb.co/pjr2BpTR/errrrr.png)

## Methodology

### Problem with Traditional Stress Tests

Most stress tests (, y-cruncher etc.) apply continuous, predictable load across all cores simultaneously. This is good for thermal testing but misses instabilities that appear during normal use, particularly with undervolting.

### How Thread Stepper Works

**Variable Load Patterns**  
Applies light, medium, and heavy loads in varying durations and rapid transitions. This forces voltage/frequency changes where instability typically occurs.

**Sequential Core Testing**  
Tests individual cores and thread groups in sequence rather than loading all cores uniformly. Isolates per-core curve optimizer issues.

**Randomized Background Load**  
Uses 3D WebGL browser tests to generate unpredictable background activity during testing. Mimics real usage patterns where undervolts typically fail.

**Test Patterns**  
Cycles through different load combinations on each core and thread group, with configurable durations for light/medium/heavy workloads and rest periods between tests.

### CPU Load examples

- Full core test

![full](https://i.ibb.co/cKCKc3wh/Screenshot-20260501-223547.png)

- Single core test (both threads)

![pairs](https://i.ibb.co/BKsNJBNY/Screenshot-20260501-223108.png)

- Random test

![random](https://i.ibb.co/3th93hd/random.png)

- Rapid load test

![rapid](https://i.ibb.co/2YL2hKf0/rapid.png)

- Browser variable load test

![browser](https://i.ibb.co/zhFSPdhs/Screenshot-20260501-223807.png)

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
- **Rapid Tests**: How many times to perform the rapid transition test
- **Rapid Time**: Duration of each rapid transition test
- **Random Tests**: How many times to perform the random core load test
- **Random Time**: Duration of each random cpu load test
- **Rest**: Pause between tests
- **Core Blacklist**: Cores to skip (format: 1,5,10,14)
- **Max RAM**: The maximum memory which will be used in tests