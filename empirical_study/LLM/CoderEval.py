import json
import re
import ast
import os
from tqdm import tqdm  # 引入 tqdm 进度条库
from gemini import gemini

output_file = 'gpt_result.jsonl'

# 自定义函数：API 提取器
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



# 加载数据
with open("CoderEval4Python.json", "r", encoding="utf-8") as f:
    content_json = json.load(f)

records = content_json["RECORDS"]
filtered_data = [r for r in records if r["project"] == "neo4j/neo4j-python-driver"]

# 初始化总结果列表
all_generated_codes = []

with open(output_file, 'w', encoding='utf-8') as jsonl_file:
    with tqdm(total=len(filtered_data), desc="Processing", unit="task") as pbar:
        for data in filtered_data:
            gt = data["code"]
            oracle_function_names = extract_api_calls(gt)

            code_str = data["code"]
            triple_quotes_positions = [m.start() for m in re.finditer(r'"""', code_str)]

            if len(triple_quotes_positions) >= 2:
                start_index = 0
                end_index = triple_quotes_positions[1]
                target_function_prompt = code_str[start_index:end_index]
            else:
                target_function_prompt = code_str
            target_function_prompt = target_function_prompt + "\"\"\""

            prompt_template = """You are an expert Python programmer. Your task is to complete the target Python function for a repository under development.\n


Target Function:\n
{target_function_prompt}


"""
            prompt = prompt_template.format(
                target_function_prompt=target_function_prompt
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