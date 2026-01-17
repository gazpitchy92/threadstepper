# ThreadStepper

A stability and stress tester, with an easy to use GUI, for AMD Curve Optimizer and PBO.

This tool was developed specifically for testing undervolting and boost stability, where conventional stress tests often fail.

![running](https://iili.io/fUTdO21.png)
![errors](https://iili.io/fUT27wJ.png)

## Latest Updates - Version 2.0

- New GUI interface!
- Better live error checking.
- Logging of highest CPU clocks.
- Improved CPU topology testing.
- Improved settings and install.sh script.
- Improved testing methods for faster error detection.

## Requirements

- stress-ng
- p7zip
- python

## Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/gazpitchy92/threadstepper.git
   cd threadstepper
   python start.py
   ```

2. **Install dependencies:**
   This can be done through the GUI (top right), or through a terminal using:
   ```bash
   chmod +x install.sh
   sudo ./install.sh
   ```
   The install script will automatically install stress-ng, p7zip, and download the required ungoogled-chromium AppImage for WebGL tests.

### Test Setup
The GUI gives you the following settings. All times are in seconds. 
If you are unsure, leave it as the default. 

- Loops: The amount of times Thread Stepper will loop.
- Light: How long a light test will run. 
- Medium: How long a medium test will run.
- Heavy: How long a heavy test will run.
- Browsers: How many browsers to launch in the test. 
- All Core: How long to run the all core test.
- Rapid Time: How long to run each rapid test.
- Rest: The time to rest between each test.
- Core Blacklist: An array of cores to not test (1,5,10,14)