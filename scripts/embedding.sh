WORD2VEC=../../opensrc/word2vec
BIN_DIR=$WORD2VEC/bin
OUTPUT_DIR=./output
vector_size=300

WINDOW_SIZE=8
NUM_THREADS=15
MAX_ITER=15

CORPUS=output/wiki+reuters.txt
output_file=$OUTPUT_DIR/vectors.txt


echo "Training size: $vector_size, save to: $output_file"
/usr/bin/time -f "%C - %E" -a -o $OUTPUT_DIR/log.txt \
        $BIN_DIR/word2vec -train $CORPUS \
        -output $output_file \
        -cbow 0 \
        -size $vector_size \
        -window $WINDOW_SIZE \
        -negative 25 \
        -hs 0 \
        -sample 1e-4 \
        -threads $NUM_THREADS \
        -binary $BINARY \
        -iter $MAX_ITER