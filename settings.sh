#!/bin/bash

# stress test types from stress-ng
light=("bitops" "pi" "gcd" "sieve")
mixed=("prime" "matrixprod" "fft" "loop")
heavy=("ackermann" "factorial")
rapid="bitops"

# stress test times
light_time="2s"
medium_time="5s"
heavy_time="15s"
all_core_time=15
rapid_tests=4
rapid_time="1s"
rest_time=5
