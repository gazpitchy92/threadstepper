### About ThreadStepper:
ThreadStepper is a stability and stress tester.
It applies a varying level of stress to individual cores or threads to emulate real world low, medium and heavy usage. Utilizing 7z benchmarking, stress-ng and WebGL browser tests written with three.js. 

This tool was developed for testing undervolting and Ryzen CO, where conventional stress tests fail to find instabilities

### Installation:
ThreadStepper requires stress-ng and p7zip to be installed. Aswell as a copy of ungoogle-chroium Appimage.

The ./install.sh script can be used to help install these dependancies. 
This script will also download the required ungoogled-chroium for our WebGL tests. 

```bash
git clone https://github.com/gazpitchy92/threadstepper.git
cd threadstepper
chmod +x install
sudo ./install
```

### Usage: 
```bash
./threadstepper [-l loops] [-t type (cores|threads)] [-b number of browsers] [--second-half] [--first-half]
```

#### Basic Example: 
```bash
./threadstepper -l 2 -t threads -b 2
```
Running just threadstepper, without arguments, will also run one loop with the default values. 

#### Options:
```bash
./threadstepper --help
```
- `-l`                number of test loops to perform (default: 1)
- `-t`                'cores' tests all cores  
                      'threads' tests all threads (default: cores)
- `-b`                number of browsers to launch (default: 2) (0 to skip test)
- `--first-half`      tests the first half of the cores/threads (skips 7z tests)
- `--second-half`     tests the second half of the cores/threads (skips 7z tests)
- `--help`            show this help menu

#### Settings

Additional test settings can be found in `settings.sh`

The defaults here are fine, only change them if you have a specific use case. 

```bash
These are stress-ng methods used for each stage of testing:

light=("bitops" "pi" "gcd" "sieve")
mixed=("prime" "matrixprod" "fft" "loop")
heavy=("ackermann" "factorial")
rapid="bitops"
```
```bash
The following times relate to how long each test is ran:

light_time="1s"
medium_time="5s"
heavy_time="15s"
all_core_time=15
rapid_tests=2
rapid_time="2s"
rest_time=5
```

#### Logging:

Logs are generated and replaced each run in ./log.txt

### Other Notes:

Whilst stress-ng runs it's own test validation, which is used in threadstepper. It can be helpful to run OCCT in Monitor mode, to improve any error detection. 

