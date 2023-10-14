generate(){
    python3 main_4n0_3layer_12T_res.py --config config/$1/individual_3layer_12T.json --save > $1.txt
    python3 result.py --config config/$1/individual_3layer_12T.json
    mv *$1* $2
}

experiment(){
    echo $1
    mkdir $1
    generate PEMS04 $1
    generate PEMS08 $1
    ls $1
}

experiment result01

# cd data
# python Temporal_Graph_gen.py --dataset Youbike --lag 6 --period 24
# cd ..