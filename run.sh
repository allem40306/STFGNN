grpah(){
    cd data
    python Temporal_Graph_gen.py --dataset $1 --lag 6 --period 24
    cd ..
}

experiment(){
    echo $1_$2
    mkdir $1_$2
    python3 main_4n0_3layer_12T_res.py --config config/$1/individual_3layer_12T.json --save  --folder $1_$2 --test > $1_$2/$1.txt
}

experiment Youbike_1 r01