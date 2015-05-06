#!/bin/sh
{% if CIS_QUEUE is defined %}
#PBS -q @@{CIS_QUEUE}
{% endif %}

echo "Hello World from PartB" > output_B.dat
echo "Message from PartA:" >> output_B.dat
cat "@@{CIS_CHAIN0}/output_A.dat" >> output_B.dat

exit $?

