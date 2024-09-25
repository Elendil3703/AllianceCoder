import json
import logging
import sys
import os
from tqdm import tqdm  # 导入 tqdm
from chatgpt import call_openai_api
# 现在可以导入 callLLM 下的 generate 模块了
from callLLM.callLLM import generate

# 读取函数信息
with open('repo_funcs_summary/function_details.json', 'r') as file:
    functions = json.load(file)

results = []
batch_size = 100  # 每100次写入一次

# 尝试从上次写入的位置继续
if os.path.exists('repo_funcs_summary/function_summaries.json'):
    with open('repo_funcs_summary/function_summaries.json', 'r') as out_file:
        try:
            existing_data = json.load(out_file)
            results.extend(existing_data)
            # start_index = len(existing_data)
        except json.JSONDecodeError:
            logging.warning("Failed to decode JSON, starting from scratch.")
            start_index=0
else:
    start_index = 0  

# 使用手动索引管理，避免 TqdmKeyError 错误
for i in tqdm(range(start_index, len(functions))):  # 将循环包装在 tqdm 中
    function = functions[i]
    name = function['name']
    docstring = function.get('docstring', 'No docstring provided')
    args = ', '.join(function['args'])
    defaults = ', '.join([str(d) for d in function['defaults']])
    code = function['code'].replace('\n', '\\n')  # 调整换行符以适应单行字符串
    
    # 构建 prompt
    summary = call_openai_api(f"here is the description of the function:\nFunction Name: {name}\ndocstring: {docstring}\nargs: {args}\ndefaults: {defaults}\ncode: {code}\nFor this function, please provide a brief summary of its functionality.Your answer starts with :\"This function is used to...\".[/INST]",
                             "You are a Python engineer. Your job is to analyze Python function provided, and summary its functionality")
    print(summary)
    # 保存结果
    results.append({
        "function_name": name,
        "summary": summary
    })

    # 每1000次写入一次文件
    if (i + 1) % batch_size == 0 or (i + 1) == len(functions):
        with open('repo_funcs_summary/function_summaries.json', 'w') as out_file:
            json.dump(results, out_file, indent=4)
        print(f"Progress saved at iteration {i + 1}")

print("Summaries have been saved to function_summaries.json")