#!/bin/bash

# stress test types from stress-ng
light=("bitops" "pi" "gcd" "sieve")
mixed=("prime" "matrixprod" "fft" "loop")
heavy=("ackermann" "factorial")
rapid="bitops"

# stress test times - # 280s - 560s - 9m (74m (1.25h) 8 cores) (149m (2.5h) 16 threads) - 9800X3d example times
light_time="5s" # 40s - 80s
medium_time="15s" # 120s - 240s
heavy_time="30s" # 120s - 240s
all_core_time=5
rapid_tests=1
rapid_time="1s"
rest_time=3
