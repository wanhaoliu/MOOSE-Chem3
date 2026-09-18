# !/bin/bash

for i in {1..1}
do
    echo "$i"
    mkdir -p "./output/Output_0420-4o-min/$i"
    python ./Method/method.py --num $i > ./output/Output_0420-4o-min/$i/$i.txt &
    # python ./Method/method_alone_batch.py --num $i > ./output/Output_031111-4o-min/$i/$i.txt &

done

