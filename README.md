# LANCE

## Abstract

Large Language Models (LLMs) have demonstrated remarkable capabilities on various tasks, while the further evolvement is limited to the lack of high-quality training data. In addition, traditional training approaches rely too much on expert-labeled data, setting a ceiling on the performance of LLMs. To address this issue, we propose a novel paradigm named **LANCE** (**LAN**guage models as **C**ontinuous self-**E**volving data engineers) that enables LLMs to train themselves by autonomously generating, cleaning, reviewing, and annotating data with preference information. Our approach demonstrates that LLMs can serve as continuous self-evolving data engineers, significantly reducing the time and cost of the post-training data construction. Through iterative fine-tuning on Qwen2 series models, we validate the effectiveness of LANCE across various tasks, showing that it can maintain high-quality data generation and continuously improve model performance. Across multiple benchmark dimensions, LANCE result in an average score enhancement of **3.64** for Qwen2-7B and **1.75** for Qwen2-7B-Instruct. This training paradigm with autonomous data construction not only reduces the reliance on human experts or external models but also ensures that the data aligns with human preferences, paving the way for the development of future superintelligent systems that can exceed human capabilities.

## key contribution

- 🚀 We propose **LANCE** , a new approach for LLMs to autonomously generate and refine data, reducing post-training preparation costs.
- 🛠️ LANCE automates the entire data construction process, improving efficiency, quality, and model performance.
- 🧮 LANCE boosts mathematical reasoning and multilingual proficiency using only general-purpose training data.

## Quick Start

### 1. Installation

Before proceeding, ensure that you have [Conda](https://docs.conda.io/en/latest/) installed on your system. Follow these steps to set up the environment:

```bash
# Step 1: Create a new Conda environment with Python 3.10
conda create --name LANCE python=3.10

# Step 2: Activate the environment
conda activate LANCE

# Step 3: Install required dependencies
pip install -r requirements.txt
```

This will create and activate a Conda environment named `LANCE` and install all necessary dependencies listed in `requirements.txt`.

### 2. Generate Iteration 1 Data

To generate the initial dataset for iteration 1, run the following script:

```bash
bash run_iter1.sh
```

This script will generate the data required for the first iteration of the process. The generated datasets (`sft_iter1_gathered.json` and `dpo_iter1_gathered.json`) are already formatted to comply with the input requirements of [LLaMA-Factory](https://github.com/hiyouga/LLaMA-Factory).

### 3. Train the Model Using LLaMA-Factory

We use the [LLaMA-Factory](https://github.com/hiyouga/LLaMA-Factory) framework to train our models. The generated datasets are located as follows:

- **SFT Data**: `dataset/sft/sft_iter1_gathered.json`
- **DPO Data**: `dataset/dpo/dpo_iter1_gathered.json`

Refer to the [LLaMA-Factory documentation](https://github.com/hiyouga/LLaMA-Factory) for detailed instructions on how to train the model using these datasets.

### N. Generate Iteration N Data

For subsequent iterations (e.g., iteration 2, 3, ..., N), you can generate the corresponding datasets by running the following script:

```bash
bash run_itern.sh
```

This script will generate the data required for the current iteration. The generated datasets (`sft_iterN_gathered.json` and `dpo_iterN_gathered.json`) are automatically formatted to meet the requirements of [LLaMA-Factory](https://github.com/hiyouga/LLaMA-Factory).

### N+1. Train the Model Using LLaMA-Factory

After generating the dataset for iteration N, proceed to train the model using the [LLaMA-Factory](https://github.com/hiyouga/LLaMA-Factory) framework. Use the generated datasets (`sft_iterN_gathered.json` and `dpo_iterN_gathered.json`) for training.

Refer to the [LLaMA-Factory documentation](https://github.com/hiyouga/LLaMA-Factory) for detailed instructions on model training.

## Acknowledgments

This work would not have been possible without the support of the following open-source projects:

- We used [LLaMA-Factory ](https://github.com/hiyouga/LLaMA-Factory)for model training.
- We used [OpenCompass ](https://github.com/open-compass/opencompass)and [Qwen2.5-Math ](https://github.com/QwenLM/Qwen2.5-Math)for model evaluation.

We deeply appreciate the incredible work done by the developers behind these projects!