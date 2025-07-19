import json
from openai import call_openai_api
from gemini import gemini
from tqdm import tqdm  # 导入 tqdm 库
import re
import difflib

# 打开 JSONL 文件并逐行读取
with open("prompts/gt-one-gram-ws-20-ss-2.jsonl", 'r') as infile:
    lines = infile.readlines()  # 读取所有行
    total_lines = len(lines)  # 获取总行数
    
    with open('results/result.jsonl', 'w') as outfile:
        # 使用 tqdm 创建进度条，total 参数表示总行数
        for line in tqdm(lines, total=total_lines, desc="Processing prompts"):
            data = json.loads(line.strip())  # 逐行加载 JSON 对象
            
            # 提取 prompt
            prompt = data['prompt']
            ground_truth = data['metadata']['ground_truth']
            # 从 ground_truth 中提取 ground_truth_body
            index = ground_truth.rfind('"""\n')
            if index != -1:
                ground_truth_body = ground_truth[index + len('"""\n'):]
            else:
                ground_truth_body = ground_truth

            def remove_matching_substrings(text, pattern):
                matcher = difflib.SequenceMatcher(None, text, pattern)
                output = []
                i = 0
                for block in matcher.get_matching_blocks():
                    start = block.a
                    end = block.a + block.size
                    if start > i:
                        output.append(text[i:start])
                    i = end
                if i < len(text):
                    output.append(text[i:])
                return ''.join(output)
            # 从 prompt 中删除与 ground_truth 匹配的部分
            prompt = remove_matching_substrings(prompt, ground_truth_body)
            #print(prompt)
            prompt += "## Complete the unfinished function.\n"
            prompt += "## Ensure that you provide the **full** function, including both the function signature and the function body.\n"
            prompt += "## Do **not** include anything else—only the complete function.\n\n"
            
            sys_prompt = "You are a python engineer. Your job is to complete the python function and provide the complete function."
            
            # 调用 generate 函数生成五次结果
            results = []
            for _ in range(5):
                result = gemini(prompt)
                match = re.search(r'```python\s*(.*?)\s*```', result, re.DOTALL)
                if match:
                    cleaned_code = match.group(1).strip()  # 提取并去除多余的空格
                else:
                    cleaned_code = result.strip()  # 如果没有找到代码块，则直接使用整个结果
                results.append(cleaned_code)
            
            # 构建输出数据
            output_data = {
                "prompt": prompt,
                "choices": results,
                "metadata": {
                    "task_id": data['metadata']['task_id'],
                    "ground_truth": data['metadata']['ground_truth'],
                    "function_name": data['metadata']['function_name'],
                    "_id": data['metadata']['_id'],
                    "fpath_tuple": data['metadata']['fpath_tuple'],
                    "lineno": data['metadata']['lineno'],
                    "context_start_lineno": data['metadata']['context_start_lineno'],
                }
            }
            
            # 将结果写入到 JSONL 文件
            outfile.write(json.dumps(output_data) + "\n")