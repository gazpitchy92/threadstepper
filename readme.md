# Thread Stepper 
![icon](https://i.ibb.co/9kmwL1p1/favicon.png)

A stability and stress tester for AMD Curve Optimizer and PBO on Linux.

Designed specifically for testing undervolting and boost stability, where conventional stress tests often fail.

## Latest Updates - Version 2.17

- Replaced 7z and Stress-ng with our own tests
- Improved UI and easier settings
- Browser tests no longer require ungoogled-chromium
- Error testing now shows which core/thread failed
- Improved error detection accuracy
- CPU topology detection (detection of threads per core)
- New dark and light mode theme
- Easier core/thread selection
- Benchmarking tool added

### To-Do List

- Add installer to AUR
- Add installer for Flatpak
- Add benchmark UI to show score history

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


## Requirements

- python 3
- electron

## Installation

1. **Clone the repository:**
```bash
   git clone https://github.com/gazpitchy92/threadstepper.git
   cd threadstepper
```

2. **Install (optional) dependencies:**

   Downloads ungoogled-chromium AppImage for WebGL test, used for the Browser based single Core tests.

   These can be installed using the GUI or the install script.

   ![installer](https://i.ibb.co/YTKLSpQx/Screenshot-20260508-232724-1.png)

```bash
   chmod +x install.sh
   sudo ./install.sh
```

3. **Run the launch.sh script:**

   On the first run this will setup the python environment. Otherwise it will just launch Thread Stepper.

```bash
   chmod +x launch.sh
   ./launch.sh
```

## Settings

Default settings work for most users.

**Test Runs**: How many times to run the entire test suite.

**High Load**: Tests that apply an all-core load.
- **All Core Time**: How long each CPU load level is sustained. (seconds)
- **All Core Tests**: How many times to repeat the all-core tests. (number)

**Low Load**: Tests that apply a reduced load across cores.
- **Rapid Tests**: How many times to run the rapid test, which applies a brief load to each core in sequence. (number)
- **Rapid Time**: How long the rapid load is applied per core. (seconds)
- **Rand Tests**: How many times to run the random test, which applies a light load to random threads. (number)

**Single Core**: Tests that cycle through each core individually with varying load levels.
- **Low Time**: How long to test each core at low load. (seconds)
- **Medium Time**: How long to test each core at medium load. (seconds)
- **High Time**: How long to test each core at high load. (seconds)

**Browser Tests**: Repeats the single-core tests with a number of browser instances running variable CPU loads in the background.
- **Instances**: How many browser instances to open during each test. (number)

**Advanced Options**
- **Rest Time**: How long to pause between test types. (seconds)

## Screenshots

![running](https://i.ibb.co/wrNJdVxK/Screenshot-20260508-232048.png)
![errors](https://i.ibb.co/5hmdxBVb/Screenshot-20260508-232333-1.png)
![browser](https://i.ibb.co/mVyjrdmM/Screenshot-20260502-211611.png)