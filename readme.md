# Thread Stepper

A stability and stress tester for AMD Curve Optimizer and PBO on Linux.

Designed specifically for testing undervolting and boost stability, where conventional stress tests often fail.

## Latest Updates - Version 2.15

- Replaced 7z and Stress-ng with our own tests
- Improved UI and easier settings
- Error testing now shows which core/thread failed
- CPU topology detection (detection of threads per core)
- New dark and light mode theme
- Easier core/thread selection

### To-Do List

- Add installer to AUR
- Add benchmark UI to show score history

## Screenshots

![running](https://i.ibb.co/MyxL83XT/Screenshot-20260502-205501-1.png)
![errors](https://i.ibb.co/n97s589/Screenshot-20260502-030048-1.png)
![threads](https://i.ibb.co/0yhzGcKY/cores.png)
![benchmark](https://i.ibb.co/6dxq7t9/Screenshot-20260502-205753-1.png)


## Methodology

### Problem with Traditional Stress Tests

Most stress tests (mprime, systester, y-cruncher etc.) apply continuous, predictable load across all cores simultaneously. This is good for thermal testing but misses instabilities that appear during normal use, particularly with undervolting.

### How Thread Stepper Works

**Variable Load Patterns**  
Applies low, medium, and high loads in varying durations and rapid transitions. This forces voltage/frequency changes where instability typically occurs.

**Sequential Core Testing**  
Tests individual cores and thread groups in sequence rather than loading all cores uniformly. Isolates per-core curve optimizer issues.

**Randomized Background Load**  
Uses 3D WebGL browser tests to generate unpredictable background activity during testing. Mimics real usage patterns where undervolts typically fail.

**Test Patterns**  
Cycles through different load combinations on each core and thread group, with configurable durations for low/medium/high workloads and rest periods between tests.

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

- python
- Linux

## Installation

1. **Clone the repository:**
```bash
   git clone https://github.com/gazpitchy92/threadstepper.git
   cd threadstepper
   chmod +x launch.sh
   ./launch.sh
```

2. **Install dependencies:**
   Via GUI (top right) or terminal:
```bash
   chmod +x install.sh
   sudo ./install.sh
```

Downloads ungoogled-chromium AppImage for WebGL tests.

## Settings

All times in seconds. Default settings work for most users.


**Test Runs**: How many times to run the entire test suite.

**High Load**: Tests that test all-core loads.

- **All Core Time**: How long each change in CPU load is applied for. (seconds)

- **All Core Tests**: The amount of times to run the all core tests. (number)

**Low Load**: Tests that apply a low load tests.

- **Rapid Tests**: The rapid test applies a rapid load to each core in order. (number)

- **Rapid Time**: How long to apply the rapid load for. (seconds)

- **Rand Tests**: The random test applies a light load to random threads.

**Single Core**: These tests go through each core with a variatey of tests.

- **Low Time**: How long to test each core with low load tests. (seconds)

- **Medium Time**: How long to test each core with medium load tests. (seconds)

- **High Time**: How long to test each core with medium load tests. (seconds)

**Browser Tests**: Repeats single core tests, with a number of browsers running variable cpu loads.

- **Instances**: How many browsers to open for each test. 

**Advanced Options**

- **Rest Time**: How much time to rest for between test types. (seconds)