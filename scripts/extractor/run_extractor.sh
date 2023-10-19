python extractor.py \
    --model_name_or_path models/checkpoint-700 \
    --test_file data/extractor_dataset_val.csv \
    --do_predict \
    --output_dir results \
    --text_column response \
    --predict_with_generate \
    --max_target_length 10
