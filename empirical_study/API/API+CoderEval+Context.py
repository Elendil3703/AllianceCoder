import json
import re
import ast
import os
from tqdm import tqdm  # 引入 tqdm 进度条库
from openai import call_openai_api
from gemini import gemini

class APICallExtractor(ast.NodeVisitor):
    def __init__(self):
        self.api_calls = []

    def visit_Call(self, node):
        if isinstance(node.func, ast.Name):
            self.api_calls.append(node.func.id)
        elif isinstance(node.func, ast.Attribute):
            self.api_calls.append(f"{ast.unparse(node.func)}")
        self.generic_visit(node)

def extract_api_calls(code_snippet):
    try:
        tree = ast.parse(code_snippet)
        extractor = APICallExtractor()
        extractor.visit(tree)
        return extractor.api_calls
    except Exception as e:
        print(f"Error parsing code snippet: {e}")
        return []

# 加载函数信息
with open('repo_funcs_summary/function_details.json', 'r', encoding='utf-8') as f:
    function_details_list = json.load(f)

function_details_map = {item['name']: item for item in function_details_list}

def build_provided_functions_info(api_names):
    info_list = []
    for name in api_names:
        if name in function_details_map:
            detail = function_details_map[name]
            func_str = (
                f"Function Name: {detail['name']}\n"
                f"Docstring: {detail['docstring']}\n"
                f"Args: {detail['args']}\n"
                f"Defaults: {detail['defaults']}\n"
                f"Class: {detail['class']}\n"
                f"File: {detail['file']}\n"
                "Code:\n"
                "```\n"
                f"{detail['code']}\n"
                "```\n"
                f"Path: {detail['file']}\n"
            )
            info_list.append(func_str)
        else:
            info_list.append(f"Function Name: {name} (No detailed info found)")
    return "\n\n".join(info_list)


output_file = 'API+CoderEval+CurrentFile.jsonl'

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
            function_name=data["name"]
            oracle_function_names = extract_api_calls(gt)
            for i in oracle_function_names:
                if i == function_name:
                    oracle_function_names.remove(i)
            oracle_function_info = build_provided_functions_info(oracle_function_names)
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
            

            prompt_template = """You are an expert Python programmer. Your task is to complete the target Python function for a repository under development.You can use the functions provided below to help you.\n
Provided Functions:\n

{oracle_function_info}
\n\n

Current File Content:\n
{current_file_prompt}

Target Function:\n
{target_function_prompt}
Please only provide the complete target function and don't include anything else.


"""
            prompt = prompt_template.format(
                oracle_function_info=oracle_function_info,
                target_function_prompt=target_function_prompt,
                current_file_prompt=current_file_prompt
            )
            sys_prompt = "You are a Python engineer; your job is to complete the function."
            generated_codes = []
            for _ in range(5):
                generate_results = gemini(prompt)
                match = re.search(r'```python\s*(.*?)\s*```', generate_results, re.DOTALL)
                if match:
                    cleaned_code = match.group(1).strip()
                else:
                    cleaned_code = generate_results
                generated_codes.append(cleaned_code)

            # 组织 JSONL 数据
            jsonl_entry = {
                "_id": data["_id"],
                "generate_results": generated_codes
            }
            jsonl_file.write(json.dumps(jsonl_entry, ensure_ascii=False) + '\n')

            pbar.update(1)

