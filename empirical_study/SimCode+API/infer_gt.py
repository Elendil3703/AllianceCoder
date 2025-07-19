import json
import re
import ast
from tqdm import tqdm
import difflib
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

# 读取函数详细信息
with open('repo_funcs_summary/function_details.json', 'r', encoding='utf-8') as f:
    function_details_list = json.load(f)

# 构建函数名到详细信息的映射
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

# 打开 JSONL 文件
with open("prompts/gt-one-gram-ws-20-ss-2.jsonl", 'r') as infile:
    lines = infile.readlines()
    total_lines = len(lines)

    with open('results/result.jsonl', 'w') as outfile:
        for line in tqdm(lines, total=total_lines, desc="Processing prompts"):
            data = json.loads(line.strip())
            prompt = data['prompt']
            ground_truth = data['metadata']['ground_truth']
            
            # 提取 ground_truth_body
            index = ground_truth.rfind('"""\n')
            if index != -1:
                ground_truth_body = ground_truth[index + len('"""\n'):]
            else:
                ground_truth_body = ground_truth

            # 从 prompt 中删除 ground_truth 匹配部分
            prompt = remove_matching_substrings(prompt, ground_truth_body)

            # 提取 API 调用
            gtapi = extract_api_calls(ground_truth)

            # 根据 API 调用获取详细函数信息
            oracle_function_info = build_provided_functions_info(gtapi)

            # 构建完整的 Prompt
            prompt += f"\n Your task is to complete the preceding function using the following API calls:\n{oracle_function_info}\n"
            prompt += "## Complete the unfinished function.\n"
            prompt += "## Ensure that you provide the **full** function, including both the function signature and the function body.\n"
            prompt += "## Do **not** include anything else—only the complete function.\n\n"            
            sys_prompt = "You are a python engineer. Your job is to complete the python function and provide the complete function."
            
            # 调用生成函数
            results = []
            for _ in range(5):
                result = gemini(prompt)
                match = re.search(r'```python\s*(.*?)\s*```', result, re.DOTALL)
                if match:
                    cleaned_code = match.group(1).strip()
                else:
                    cleaned_code = result.strip()
                results.append(cleaned_code)

            # 写入结果
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
            outfile.write(json.dumps(output_data) + "\n")