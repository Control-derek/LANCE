import json
import random
import argparse
from typing import List, Dict


def load_json(file_path: str) -> List[Dict]:
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_json(data: List[Dict], file_path: str):
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def split_data_by_score(review_data: List[Dict], threshold: float) -> tuple:
    sft_list = []
    dpo_list = []
    for data in review_data:
        if data['score'] > threshold:
            dpo_list.append(data)
        else:
            sft_list.append(data)
    return sft_list, dpo_list

def create_new_seed(sft_list: List[Dict], dpo_list: List[Dict]) -> List[Dict]:
    new_seed = []
    
    # Process SFT list
    for data in sft_list:
        for pi, pro in enumerate(data['new_prompt']):
            for ri, res in enumerate(data['new_response'][pi]):
                new_seed.append({
                    "prompt": pro,
                    "response": res,
                    "review": data['new_review'][pi][ri],
                    "score": data['new_score'][pi][ri]
                })
    
    # Process DPO list
    for data in dpo_list:
        for idx, res in enumerate(data['new_response'][0]):
            new_seed.append({
                "prompt": data['prompt'],
                "response": res,
                "review": data['new_review'][0][idx],
                "score": data['new_score'][0][idx]
            })
    
    return new_seed

def process_dpo_data(dpo_list: List[Dict]) -> List[Dict]:
    res_score_list = []
    for data in dpo_list:
        res_score_list.append({
            "prompt": data['prompt'],
            "response": data['new_response'][0] + [data['response']],
            "score": data['new_score'][0] + [data['score']]
        })
    
    for data in res_score_list:
        combined = list(zip(data['score'], data['response']))
        sorted_combined = sorted(combined, key=lambda x: x[0], reverse=True)
        sorted_scores, sorted_replies = zip(*sorted_combined)
        data['score'] = list(sorted_scores)
        data['response'] = list(sorted_replies)
    
    return res_score_list

def create_sft_data(sft_list: List[Dict], score_threshold: float) -> List[Dict]:
    sft_data = []
    for data in sft_list:
        for pi, pro in enumerate(data['new_prompt']):
            for ri, res in enumerate(data['new_response'][pi]):
                if data['new_score'][pi][ri] > score_threshold:
                    if len(pro) > 5 and len(res) > 5:
                        sft_data.append({
                            "instruction": pro,
                            "input": "",
                            "system": "# Role: Multi-Task Assistant\n\n## Profile\n\n- language: English\n- description: I am designed to handle a wide range of tasks efficiently. My responses are crafted to be concise, accurate, fluent, informative, and insightful, ensuring high-quality assistance across various domains.\n\n## Skills\n\n- Proficient in understanding and executing diverse user instructions.\n- Capable of synthesizing information and providing deep insights.\n- Skilled in maintaining clarity and precision in communication.\n\n## Goals\n\n- To deliver responses that are succinct and accurate, meeting the user's needs effectively.\n- To ensure that all information provided is reliable and free from inaccuracies or harmful content.\n- To excel in following user directives and completing assigned tasks with excellence.\n\n## Constraints\n\n- I will not provide responses that include toxic or misleading information.\n- I will strictly adhere to the user's instructions and not deviate from the specified tasks.\n\n## Workflows\n\n1. Analyze and comprehend the user's request or task.\n2. Process the information and formulate a response that is both informative and precise.\n3. Deliver the response, ensuring it aligns perfectly with the user's expectations and requirements.\n\n## OutputFormat\n\nThe output will be a clear, concise, and accurate response that effectively addresses the user's query or completes the assigned task.\n\n## Initialization\n\nHello, I am ready to assist you with any task you have in mind. Please provide me with your request, and I will ensure to deliver a high-quality response that meets your needs.",
                            "output": res,
                            "history": []
                        })
    return sft_data

def create_dpo_data(res_score_list: List[Dict], score_diff_threshold: float) -> List[Dict]:
    dpo_data = []
    for data in res_score_list:
        for i in range(len(data['score'])):
            j = len(data['score']) - 1
            if data['score'][i] - data['score'][j] > score_diff_threshold:
                if len(data['response'][i]) > 5 and len(data['response'][j]) > 5 and len(data['prompt']) > 5:
                    dpo_data.append({
                        "conversations": [{
                            "from": "human",
                            "value": data['prompt']
                        }],
                        "chosen": {
                            "from": "gpt",
                            "value": data['response'][i]
                        },
                        "rejected": {
                            "from": "gpt",
                            "value": data['response'][j]
                        }
                    })
    return dpo_data

def parse_args():
    parser = argparse.ArgumentParser(description='Preprocess data for training')
    parser.add_argument('--review_path', type=str, required=True,
                        help='Path to review data')
    parser.add_argument('--sft_output', type=str, required=True,
                        help='Path for SFT output')
    parser.add_argument('--dpo_output', type=str, required=True,
                        help='Path for DPO output')
    parser.add_argument('--sft_gathered', type=str, required=True,
                        help='Path for gathered SFT output')
    parser.add_argument('--dpo_gathered', type=str, required=True,
                        help='Path for gathered DPO output')
    parser.add_argument('--prev_sft_path', type=str, default=None,
                        help='Path to previous SFT data')
    parser.add_argument('--prev_dpo_path', type=str, default=None,
                        help='Path to previous DPO data')
    parser.add_argument('--prev_seed_path', type=str, default=None,
                        help='Path to previous seed data')
    parser.add_argument('--new_seed_path', type=str, required=True,
                        help='Path for new seed output')
    parser.add_argument('--split_threshold', type=float, default=7.0,
                        help='Threshold for splitting data into SFT and DPO')
    parser.add_argument('--sft_score_threshold', type=float, default=8.0,
                        help='Score threshold for SFT data')
    parser.add_argument('--dpo_score_diff', type=float, default=2.0,
                        help='Required score difference for DPO pairs')
    parser.add_argument('--first_iter', action='store_true',
                        help='Flag to indicate if this is the first iteration')
    return parser.parse_args()

def main():
    args = parse_args()
    
    # Load and process review data
    review_data = load_json(args.review_path)
    sft_list, dpo_list = split_data_by_score(review_data, args.split_threshold)
    
    # Create and save new seed data
    new_seed = create_new_seed(sft_list, dpo_list)
    
    if not args.first_iter and args.prev_seed_path:
        try:
            prev_seed = load_json(args.prev_seed_path)
            new_seed.extend(prev_seed)
        except Exception as e:
            print(f"Warning: Could not load previous seed data: {e}")
    
    random.shuffle(new_seed)
    save_json(new_seed, args.new_seed_path)
    print(f"Total seed instances: {len(new_seed)}")
    
    # Process DPO data
    res_score_list = process_dpo_data(dpo_list)
    
    # Create SFT and DPO datasets
    sft_data = create_sft_data(sft_list, args.sft_score_threshold)
    dpo_data = create_dpo_data(res_score_list, args.dpo_score_diff)
    
    # Save current iteration datasets
    save_json(sft_data, args.sft_output)
    save_json(dpo_data, args.dpo_output)

    try:
        if args.prev_sft_path:
            prev_sft_data = load_json(args.prev_sft_path)
            sft_data.extend(prev_sft_data)
    except Exception as e:
        print(f"Warning: Could not load previous training data: {e}")
        print("Proceeding with current iteration data only")    
    if not args.first_iter:
        # Combine with previous dpo data if not first iteration
        try:
            if args.prev_dpo_path:
                prev_dpo_data = load_json(args.prev_dpo_path)
                dpo_data.extend(prev_dpo_data)
        except Exception as e:
            print(f"Warning: Could not load previous training data: {e}")
            print("Proceeding with current iteration data only")
    
    random.shuffle(sft_data)
    random.shuffle(dpo_data)
    
    # Save gathered datasets
    save_json(sft_data, args.sft_gathered)
    save_json(dpo_data, args.dpo_gathered)

if __name__ == '__main__':
    main()