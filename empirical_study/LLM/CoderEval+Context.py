import json
import re
import ast
import os
from tqdm import tqdm  # 引入 tqdm 进度条库
from gemini import gemini
from openai import call_openai_api

output_file = 'current_file_result.jsonl'

# 加载数据
with open("CoderEval4Python.json", "r", encoding="utf-8") as f:
    content_json = json.load(f)

records = content_json["RECORDS"]
filtered_data = [r for r in records if r["project"] == "MozillaSecurity/lithium"]

# 初始化总结果列表
all_generated_codes = []

with open(output_file, 'w', encoding='utf-8') as jsonl_file:
    with tqdm(total=len(filtered_data), desc="Processing", unit="task") as pbar:
        for data in filtered_data:
            gt = data["code"]

            code_str = data["code"]
            file_content = data["file_content"]  # 获取 file_content

            triple_quotes_positions = [m.start() for m in re.finditer(r'"""', code_str)]

            if len(triple_quotes_positions) >= 2:
                start_index = 0
                end_index = triple_quotes_positions[1]
                target_function_prompt = code_str[start_index:end_index]
            else:
                target_function_prompt = code_str
            target_function_prompt = target_function_prompt + "\"\"\""

            # 查找 target_function_prompt 在 file_content 中的位置
            start_pos = file_content.find(target_function_prompt)
                # 截取 file_content 中从头到 target_function_prompt 结束的部分
            current_file_prompt = file_content[:start_pos + len(target_function_prompt)]
            

            prompt_template = """You are an expert Python programmer. Your task is to complete the target Python function for a repository under development.\n
Current File:\n
{current_file_prompt}\n

Target Function:\n
{target_function_prompt}\n
Please only provide the complete target function and don't include anything else.


"""
            prompt = prompt_template.format(
                current_file_prompt=current_file_prompt,
                target_function_prompt=target_function_prompt
            )
            sys_prompt = "You are a Python engineer; your job is to complete the function."
            #print(prompt)
            generated_codes = []
            for _ in range(5):
                generate_results = gemini(prompt)
                match = re.search(r'```python\s*(.*?)\s*```', generate_results, re.DOTALL)
                if match:
                    cleaned_code = match.group(1).strip()
                else:
                    cleaned_code = generate_results
                # result_code=target_function_prompt.lstrip()+"\n    "+cleaned_code
                # generated_codes.append(result_code)
                generated_codes.append(cleaned_code)

            # 组织 JSONL 数据
            jsonl_entry = {
                "_id": data["_id"],
                "generate_results": generated_codes
            }
            jsonl_file.write(json.dumps(jsonl_entry, ensure_ascii=False) + '\n')

            pbar.update(1)

