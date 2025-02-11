import os
import re
import json
from tqdm import tqdm
from vllm import LLM, SamplingParams
from transformers import AutoTokenizer
from langchain.prompts import PromptTemplate

import prompt_template

import contextlib
import gc

import torch
from vllm.distributed import (destroy_distributed_environment,
                              destroy_model_parallel)
from vllm.utils import is_cpu

def cleanup():
    destroy_model_parallel()
    destroy_distributed_environment()
    with contextlib.suppress(AssertionError):
        torch.distributed.destroy_process_group()
    gc.collect()
    if not is_cpu():
        torch.cuda.empty_cache()

class DataReviewer:
    """
    Review data and score it
    """
    def __init__(
            self, 
            model_path: str, 
            data_path: str,
            output_path: str,
            seed: bool, # review seed data or not
            num_gpu: int=1,
            gpu_memory_utilization: float=0.9,
        ) -> None:
        cleanup()
        ## 1.init LLM
        self.model = LLM(
            model=model_path, 
            gpu_memory_utilization=gpu_memory_utilization, 
            tensor_parallel_size=num_gpu)
        self.tokenizer = AutoTokenizer.from_pretrained(
            model_path, 
            padding_side="left"
        )
        ## 2.read data
        with open(data_path, 'r', encoding='utf-8') as json_file:
            self.origin_data = json.load(json_file)
        self.skip_len = 0
        if os.path.exists(output_path):
            with open(output_path, 'r', encoding='utf-8') as json_file:
                reviewed_data = json.load(json_file)
            self.skip_len = len(reviewed_data)
            self.origin_data[:self.skip_len] = reviewed_data
            print(f'{self.skip_len} pieces of data were skipped') 
        self.output_path = output_path
        self.seed = seed
        self.pt = PromptTemplate.from_template(template=prompt_template.ReviewPrompt)

    def sample(
            self, 
            prompt: str, 
            N: int=3,
            max_new_tokens: int=512,
            top_p: float=0.9,
            temperature: float=0.7
        ) -> str:
        '''
        Sample a batch reviews to be more scientific
        '''
        message_batch = [
                {'role': 'system', 'content': prompt_template.SYS_PROMPT},
                {"role": "user", "content": prompt}
        ]
        text_batch = self.tokenizer.apply_chat_template(
            message_batch,
            tokenize=False,
            add_generation_prompt=True,
        )
        sampling_params = SamplingParams(
            n=N,
            max_tokens=max_new_tokens,
            temperature=temperature, 
            top_p=top_p
        )
        outputs = self.model.generate(text_batch, sampling_params, use_tqdm=False)
        response_batch = [output.text for output in outputs[0].outputs]
        
        return response_batch

    def extract_score(
            self,
            review_batch
        ):
        pattern = r'score: (\d+(\.\d+)?)'
        score_list = []
        for review in review_batch:
            match = re.search(pattern, review, re.IGNORECASE)
            if not match:
                continue
            score = float(match[1])
            if 0 <= score <= 10:
                score_list.append(score)
        avg_score = sum(score_list) / len(score_list) if score_list else 0
        return avg_score
    
    def save(self, idx) -> None:
        with open(self.output_path, 'w', encoding='utf-8') as outfile:
            json.dump(self.origin_data[:idx+1], outfile, indent=4, ensure_ascii=False)
    
    def __call__(self) -> None:
        if self.seed:
            for idx, data in enumerate(tqdm(self.origin_data)):
                if self.skip_len > 0:
                    self.skip_len -= 1
                    continue
                prompt = self.pt.format(prompt=data['prompt'], response=data['response'])
                review_batch = self.sample(prompt=prompt)
                avg_score = self.extract_score(review_batch)
                data['review'] = review_batch
                data['score'] = avg_score
                if idx % 10 == 0:
                    self.save(idx)
        else:
            for idx, data in enumerate(tqdm(self.origin_data)):
                if self.skip_len > 0:
                    self.skip_len -= 1
                    continue
                pro_review = []
                pro_score = []
                for i in range(len(data['new_prompt'])):
                    res_review = []
                    res_score = []
                    for j in range(len(data['new_response'][i])):
                        prompt = self.pt.format(prompt=data['new_prompt'][i], response=data['new_response'][i][j])
                        review_batch = self.sample(prompt=prompt)
                        avg_score = self.extract_score(review_batch)
                        res_review.append(review_batch)
                        res_score.append(avg_score)
                    pro_review.append(res_review)
                    pro_score.append(res_score)
                data['new_review'] = pro_review
                data['new_score'] = pro_score
                if idx % 5 == 0:
                    self.save(idx)
        self.save(len(self.origin_data))
        del self.model
        cleanup()