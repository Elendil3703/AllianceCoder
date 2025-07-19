# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.

import os
os.environ["TOKENIZERS_PARALLELISM"] = "false"

from make_window import MakeWindowWrapper
from build_vector import BuildVectorWrapper, BagOfWords
from search_code import CodeSearchWrapper
from build_prompt import BuildPromptWrapper

from utils import CONSTANTS, CodexTokenizer


def make_repo_window(repos, window_sizes, slice_sizes):
    MakeWindowWrapper(None, repos, window_sizes, slice_sizes).window_for_repo_files()
    vectorizer = BagOfWords
    BuildVectorWrapper(None, vectorizer, repos, window_sizes, slice_sizes).vectorize_repo_windows()


def run_RG1_and_oracle_method(benchmark, repos, window_sizes, slice_sizes):
    
    # build code snippets for vanilla retrieval-augmented approach and ground truth
    MakeWindowWrapper(benchmark, repos, window_sizes, slice_sizes).window_for_baseline_and_ground()
    # build vector for vanilla retrieval-augmented approach and ground truth
    vectorizer = BagOfWords
    BuildVectorWrapper(benchmark, vectorizer, repos, window_sizes, slice_sizes).vectorize_repo_windows()
    BuildVectorWrapper(benchmark, vectorizer, repos, window_sizes, slice_sizes).vectorize_baseline_and_ground_windows()

    # search code for vanilla retrieval-augmented approach and ground truth
    CodeSearchWrapper('one-gram', benchmark, repos, window_sizes, slice_sizes).search_baseline_and_ground()
    # build prompt for vanilla retrieval-augmented approach and ground truth
    tokenizer = CodexTokenizer
    mode = CONSTANTS.rg
    output_file_path = 'prompts/rg-one-gram-ws-20-ss-2.jsonl'
    BuildPromptWrapper('one-gram', benchmark, repos, window_sizes, slice_sizes, tokenizer).build_first_search_prompt(mode, output_file_path)

    mode = CONSTANTS.gt
    output_file_path = 'prompts/gt-one-gram-ws-20-ss-2.jsonl'
    BuildPromptWrapper('one-gram', benchmark, repos, window_sizes, slice_sizes, tokenizer).build_first_search_prompt(mode, output_file_path)


def run_RepoCoder_method(benchmark, repos, window_sizes, slice_sizes, prediction_path):
    mode = CONSTANTS.rgrg
    MakeWindowWrapper(benchmark, repos, window_sizes, slice_sizes).window_for_prediction(mode, prediction_path)
    vectorizer = BagOfWords
    BuildVectorWrapper(benchmark, vectorizer, repos, window_sizes, slice_sizes).vectorize_prediction_windows(mode, prediction_path)
    CodeSearchWrapper('one-gram', benchmark, repos, window_sizes, slice_sizes).search_prediction(mode, prediction_path)
    tokenizer = CodexTokenizer
    output_file_path = 'prompts/repocoder-one-gram-ws-20-ss-2.jsonl'
    BuildPromptWrapper('one-gram', benchmark, repos, window_sizes, slice_sizes, tokenizer).build_prediction_prompt(mode, prediction_path, output_file_path)


if __name__ == '__main__':
    

    repos = [
        'string_utils',
    ]
    window_sizes = [20]
    slice_sizes = [2]  # 20 / 2 = 10

    # build window for the repos
    make_repo_window(repos, window_sizes, slice_sizes)

    # build prompt for the RG1 and oracle methods
    run_RG1_and_oracle_method(CONSTANTS.function_benchmark, repos, window_sizes, slice_sizes)
    print("finish RG1 and oracle method")

    filename2 = 'infer_gt.py'
    with open(filename2, 'r') as file:
         script_content2 = file.read()
         exec(script_content2)
    print("finish infer_gt")

    

    filename2 = 'results/handle_result+CoderEval.py'
    with open(filename2, 'r') as file:
        script_content2 = file.read()
    exec(script_content2)
    print("finish handle result")

    