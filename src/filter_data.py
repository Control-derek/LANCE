'''
{
    "prompt": str
    "response": str
    "review": [str1, str2, str3]
    "score": int
    "new_prompt": [str, ...]  # new data: N, new res: 1
    "new_response": [
        [str1, ...],
        [str2, ...],
        ...  # N*M/1*M
    ]
    "new_review": [
        [[], ...],
        [[], ...]
    ]  # N*M*3/1*M*3
}
'''

import os
import json
from typing import Any
from tqdm import tqdm
from rouge import Rouge
import seaborn as sns
import matplotlib.pyplot as plt
from datetime import datetime

class DataFilter:
    """
    Filter data by ROUGE-L similarity check, Keyword filtering and length filtering.
    """
    def __init__(
            self, 
            data_path: str=None,
            output_path: str=None,
        ) -> None:
        with open(data_path, 'r', encoding='utf-8') as json_file:
            self.raw_data = json.load(json_file)
            print(f"{data_path} read successfully")
        self.output_path = output_path
        self.rouge = Rouge(metrics=["rouge-l"])

    def similar(self, rouge_score, threshold=0.70) -> bool:
        """
        Filter similar data using the ROUGE-L score.
        """
        return any(rouge_score[0]['rouge-l'][metric] > threshold for metric in ['r', 'p', 'f'])
                
    def length_filter(
        self,
        instance: str,
        min: int=10,
        max: int=4096,
    ) -> bool:
        return len(instance.split()) < min or len(instance.split()) > max

    def process(
            self, 
            data,
        ) -> None:
        """
        Check the similarity between new_prompts,
        the similarity between new_responses,
        and the similarity between old and new prompts and responses.
        """
        # 1. Similarity between new and old prompts, and among new prompts
        if "new_prompt" not in data or "new_response" not in data:
            return False
        data_batch = data['new_prompt']
        reference = data['prompt']
        if len(data_batch) > 1:
            for i in reversed(range(len(data_batch))):
                if self.length_filter(data_batch[i], min=5):  # Length filtering
                    # Delete the prompt and its corresponding response
                    del data_batch[i]
                    del data['new_response'][i]   
            for i in reversed(range(len(data_batch))):
                rl = self.rouge.get_scores(data_batch[i], reference)
                if self.similar(rl):
                    # Delete the prompt and its corresponding response
                    del data_batch[i]
                    del data['new_response'][i]                
                    continue
                for j in range(i):
                    rl = self.rouge.get_scores(data_batch[i], data_batch[j])
                    if self.similar(rl):
                        # Delete the prompt and its corresponding response
                        del data_batch[i]
                        del data['new_response'][i]
                        break  
        if data['new_prompt'] == []:
            return False
                
        # 2. Similarity between new and old responses, and among new responses
        reference = data['response']
        for k in reversed(range(len(data['new_response']))):
            data_batch = data['new_response'][k]
            for i in reversed(range(len(data_batch))):
                if self.length_filter(data_batch[i]):  # Length filtering
                    # Delete the response
                    del data_batch[i]
            for i in reversed(range(len(data_batch))):
                rl = self.rouge.get_scores(data_batch[i], reference)
                if self.similar(rl):
                    del data_batch[i]
                    continue
                for j in range(i):
                    rl = self.rouge.get_scores(data_batch[i], data_batch[j])
                    if self.similar(rl):
                        del data_batch[i]
                        break  
            if data['new_response'][k] == []:
                # If the response corresponding to the k-th prompt is empty, delete the prompt as well
                del data['new_response'][k]
                del data['new_prompt'][k]
        if data['new_response'] == []:
            return False
        return True

    def __call__(self) -> Any:
        self.raw_data = [data for data in tqdm(self.raw_data, desc="Filtering") if self.process(data)]
        with open(self.output_path, 'w', encoding='utf-8') as outfile:
            json.dump(self.raw_data, outfile, indent=4, ensure_ascii=False)