# review seed data and generate iter1 training data
mkdir -p dataset/review
mkdir -p dataset/sft
mkdir -p dataset/dpo
mkdir -p dataset/gen

python src/gen_iter1.py \
    --cuda_devices "0,1" \
    --worker_method "spawn" \
    --num_gpu 2 \
    --gpu_memory_utilization 0.95 \
    --model_path "/path/to/iter0/model" \
    --seed_path "dataset/seed/UltraChat3k.json" \
    --review_path "dataset/review/review_seed.json" \
    --new_instances_path "dataset/gen/new_instances_iter1.json" \
    --filtered_path "dataset/gen/new_instances_iter1_filtered.json" \
    --new_review_path "dataset/review/review_iter1.json" \
    --threshold 7.0

python src/preprocess.py \
    --review_path "dataset/review/review_iter1.json" \
    --prev_sft_path "dataset/seed/UltraChat3k_eft_llama3_sys.json" \
    --sft_output "dataset/sft/sft_iter1.json" \
    --dpo_output "dataset/dpo/dpo_iter1.json" \
    --sft_gathered "dataset/sft/sft_iter1_gathered.json" \
    --dpo_gathered "dataset/dpo/dpo_iter1_gathered.json" \
    --prev_seed_path "dataset/review/review_seed.json" \
    --new_seed_path "dataset/seed/seed_iter1.json" \
    --split_threshold 7.0 \
    --sft_score_threshold 8.0 \
    --dpo_score_diff 2.0 \
    --first_iter