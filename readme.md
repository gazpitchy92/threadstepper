# Thread Stepper 
![icon](https://i.ibb.co/9kmwL1p1/favicon.png)

A stability and stress testing tool for AMD Curve Optimizer and PBO on Linux. Designed for testing undervolting and boost stability, where conventional stress tests can miss instability.

Most stress tests (mprime, systester, y-cruncher, etc.) apply a continuous, predictable load across all cores at the same time. This works well for thermal testing, but it can miss instability that appears during normal use, especially when undervolting.

## Latest Updates - Version 3.8

- Replaced 7z and Stress-ng with our own testing engine
- Browser (WebGL) tests no longer require ungoogled-chromium
- Improved UI and simplified settings
- Improved core failure and error detection
- Simplified core/thread selection
- New benchmarking tool

### To-Do List

- Add installer to AUR
- Add installer for Flatpak

## How Thread Stepper Works

**Variable Load Patterns**  
Applies low, medium, and high loads with varying durations and rapid transitions. This forces voltage and frequency changes, where instability commonly appears.

**Sequential Core Testing**  
Tests individual cores and thread groups in sequence instead of applying the same load across all cores. This helps isolate per-core Curve Optimizer instability.

**Randomized Background Load**  
Uses 3D WebGL browser tests to generate unpredictable background activity during testing. This better reflects normal usage patterns, where undervolts are more likely to fail.

**Test Patterns**  
Cycles through different load combinations on each core and thread group, with configurable durations for low, medium, and high workloads.

## Screenshots

![running](https://i.ibb.co/kgNmWwp7/Screenshot-20260510-065718-1.png)

### Error Detection

![errors](https://i.ibb.co/vFzz9LF/Screenshot-20260510-065850-1.png)

### Benchmarking (all core and individual cores)

![benchmark](https://i.ibb.co/BHXxCB0G/Screenshot-20260509-235622-1.png)

### WebGL Tests

![browser](https://i.ibb.co/zTT4LvRG/Screenshot-20260509-003545-1.png)

### CPU Load examples

#### All Cores

![full](https://i.ibb.co/cKCKc3wh/Screenshot-20260501-223547.png)

#### Single Core
- **Low**

![low](https://i.ibb.co/JWKq5XbL/s-low.png)
- **Medium**

![medium](https://i.ibb.co/N6byGwNH/Screenshot-20260509-024326.png)
- **High**

![high](https://i.ibb.co/4R57V25Z/s-high.png)

#### Low Load
- **Rand Test**

![random](https://i.ibb.co/3th93hd/random.png)
- **Rapid Test**

![rapid](https://i.ibb.co/2YL2hKf0/rapid.png)


## Requirements

- python 3
- electron41 (or above)
- journalctl

## Installation

1. **Clone the repository:**
```bash
   git clone https://github.com/gazpitchy92/threadstepper.git
   cd threadstepper
```

2. **Install (optional) dependencies:**

   Installs the Electron for WebGL Tests

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

**All Cores**: Tests that apply an all-core load.
- **Time**: How long each CPU load level is sustained.
- **Tests**: How many times to repeat the all-core tests.

**Low Load**: Tests that apply a reduced load across cores.
- **Rapid Tests**: How many times to run the rapid test, which applies a brief load to each core in sequence.
- **Rapid Time**: How long the rapid load is applied per core.
- **Rand Tests**: How many times to run the random test, which applies a light load to random threads.
- **Rand Time**: How long the random load is applied per core.

**Single Core**: Tests that cycle through each core individually with varying load levels.
- **Low Time**: How long to test each core at low load [10%-40%]. 
- **Medium Time**: How long to test each core at medium load [50%-70%].
- **High Time**: How long to test each core at high load [80%-100%].

**WebGL Tests**: Repeats the single-core tests with a number of WebGL instances running variable CPU loads.
- **Instances**: How many browser instances to open during each test.

**Advanced Options**
- **Rest Time**: How long to pause between test types.