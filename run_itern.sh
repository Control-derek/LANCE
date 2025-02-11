# replace "n" to 2, 3, 4...
round="n"
pround=$((round - 1))

python src/gen_itern.py \
    --cuda_devices "0,1" \
    --worker_method "spawn" \
    --num_gpu 2 \
    --gpu_memory_utilization 0.95 \
    --model_path "/path/to/prev_iter/model" \
    --seed_path "dataset/seed/seed_iter${pround}.json" \
    --new_instances_path "dataset/gen/new_instances_iter${round}.json" \
    --filtered_path "dataset/gen/new_instances_iter${round}_filtered.json" \
    --review_path "dataset/review/review_iter${round}.json" \
    --threshold 7.0 \

python src/preprocess.py \
    --review_path "dataset/review/review_iter${round}.json" \
    --prev_sft_path "dataset/sft/sft_iter${pround}_gathered.json" \
    --prev_dpo_path "dataset/dpo/dpo_iter${pround}_gathered.json" \
    --sft_output "dataset/sft/sft_iter${round}.json" \
    --dpo_output "dataset/dpo/dpo_iter${round}.json" \
    --sft_gathered "dataset/sft/sft_iter${round}_gathered.json" \
    --dpo_gathered "dataset/dpo/dpo_iter${round}_gathered.json" \
    --prev_seed_path "dataset/review/review_seed.json" \
    --new_seed_path "dataset/seed/seed_iter${round}.json" \
    --split_threshold 7.0 \
    --sft_score_threshold 8.0 \
    --dpo_score_diff 2.0