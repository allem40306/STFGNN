generate(){
    python3 main_4n0_3layer_12T_res.py --config config/$1/individual_3layer_12T.json --save > $1.txt
    python3 result.py --config config/$1/individual_3layer_12T.json
    mv *$1* $2_$1
}

experiment(){
    echo $1
    mkdir $2_$1
    generate $2 $1
    ls $1
}

experiment r01 Youbike_2
# experiment r02 Youbike_2
# experiment r03 Youbike_2
# experiment r04 Youbike_2
# experiment r05 Youbike_2

# cd data
# python Temporal_Graph_gen.py --dataset Youbike --lag 6 --period 24
# cd ..