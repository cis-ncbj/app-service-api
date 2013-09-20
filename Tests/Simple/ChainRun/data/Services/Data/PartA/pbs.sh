#!/bin/sh
#PBS -q @@{CIS_QUEUE}

echo "Hello World from PartA" > output_A.dat
sleep 2

exit $?

