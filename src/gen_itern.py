import os
import argparse

def parse_args():
    parser = argparse.ArgumentParser(description='Data processing pipeline')
    
    # Environment variables
    parser.add_argument('--cuda_devices', type=str, default='0',
                        help='CUDA device ID')
    parser.add_argument('--worker_method', type=str, default='spawn',
                        help='VLLM worker multiprocessing method')
    
    # Pipeline parameters
    parser.add_argument('--num_gpu', type=int, default=1,
                        help='Number of GPUs to use')
    parser.add_argument('--gpu_memory_utilization', type=float, default=0.95,
                        help='GPU memory utilization ratio')
    parser.add_argument('--threshold', type=float, default=7.0,
                        help='Threshold for data generation')
    parser.add_argument('--ablation', type=str, default=None,
                        help='Ablation type')
    
    # Paths
    parser.add_argument('--model_path', type=str, required=True,
                        help='Path to the model')
    parser.add_argument('--seed_path', type=str, required=True,
                        help='Path to seed data')
    parser.add_argument('--new_instances_path', type=str, required=True,
                        help='Path for new instances')
    parser.add_argument('--filtered_path', type=str, required=True,
                        help='Path for filtered instances')
    parser.add_argument('--visual_path', type=str, required=True,
                        help='Path for visualization')
    parser.add_argument('--review_path', type=str, required=True,
                        help='Path for review output')

    return parser.parse_args()

if __name__ == '__main__':
    args = parse_args()
    
    # Set environment variables
    os.environ['CUDA_VISIBLE_DEVICES'] = args.cuda_devices
    os.environ["VLLM_WORKER_MULTIPROC_METHOD"] = args.worker_method
    
    from review_instances_vllm import DataReviewer
    from generate_instances_vllm import DataSource
    from filter_data import DataFilter

    gener = DataSource(
        model_path=args.model_path,
        data_path=args.seed_path,
        output_path=args.new_instances_path,
        num_gpu=args.num_gpu,
        gpu_memory_utilization=args.gpu_memory_utilization,
        threshold=args.threshold
    )
    gener(ablation=args.ablation)

    datafilter = DataFilter(
        data_path=args.new_instances_path,
        output_path=args.filtered_path,
    )
    datafilter()

    reviewer = DataReviewer(
        model_path=args.model_path,
        data_path=args.filtered_path,
        output_path=args.review_path,
        num_gpu=args.num_gpu,
        gpu_memory_utilization=args.gpu_memory_utilization,
        seed=False
    )
    reviewer()