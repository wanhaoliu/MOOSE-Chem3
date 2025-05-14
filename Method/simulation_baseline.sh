#!/bin/bash

for rep in {1..2}
do
    echo "Starting repetition $rep"
    for i in 1
    do
        echo "  Processing simulation $i (Repeat $rep)"
        mkdir -p "./output/output-baseline2/$i-$rep"


  
        python ./Method/simulation_baseline.py --num $i --rep $rep --baseline 2 > "./output/output-baseline2/$i-$rep/$i-$rep.txt" &

    done

    echo "Repetition $rep completed"
done