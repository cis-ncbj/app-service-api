#!/bin/sh
{% if CIS_QUEUE is defined %}
#PBS -q @@{CIS_QUEUE}
{% endif %}

echo "Hello World from PartA" > output_A.dat
sleep 2

exit $?

