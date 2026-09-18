#!/bin/bash

for rep in {1..1}
do
    echo "Starting repetition $rep"
    for i in 0 
    do
        echo "  Processing simulation $i (Repeat $rep)"
        mkdir -p "./output/output/$i-$rep"
        # mkdir -p "Data/simulation_validation/output/output-simulation0422/$i-$rep"

  
        python ./Method/simulation_validation.py --num $i --rep $rep  --correction_factor 0 > "./output/output/$i-$rep/$i-$rep.txt" &
    
    done

    echo "Repetition $rep completed"
done