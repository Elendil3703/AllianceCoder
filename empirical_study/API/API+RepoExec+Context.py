import json
import re
from openai import call_openai_api
from tqdm import tqdm  # 引入 tqdm 进度条库
from datasets import load_dataset
import ast

output_file = 'API+RepoExec+CurrentFile.json'

class APICallExtractor(ast.NodeVisitor):
    def __init__(self):
        self.api_calls = []

    def visit_Call(self, node):
        # `node.func` represents the function being called
        if isinstance(node.func, ast.Name):
            # Direct function call like isNumber()
            self.api_calls.append(node.func.id)
        elif isinstance(node.func, ast.Attribute):
            # Method calls like obj.method()
            self.api_calls.append(f"{ast.unparse(node.func)}")
        # 继续访问子节点
        self.generic_visit(node)

def extract_api_calls(code_snippet):
    try:
        # 将代码转换为 AST
        tree = ast.parse(code_snippet)
        extractor = APICallExtractor()
        extractor.visit(tree)
        return extractor.api_calls
    except Exception as e:
        print(f"Error parsing code snippet: {e}")
        return []

# ====== 读取函数信息并构建字典以便查询 ======
with open('repo_funcs_summary/function_details.json', 'r', encoding='utf-8') as f:
    function_details_list = json.load(f)

# 将函数名与其详细信息对应起来，方便后面查找
function_details_map = {item['name']: item for item in function_details_list}

def build_provided_functions_info(api_names):
    """
    根据从 extract_api_calls(gt) 中得到的 api 名称列表，
    去 function_details_map 中匹配对应的函数信息，并拼接成字符串返回
    """
    info_list = []
    for name in api_names:
        # 如果函数名在字典中匹配到，则提取内容
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
                f"Path:{detail['file']}\n"
            )
            info_list.append(func_str)
        else:
            # 如果在 JSON 中未找到匹配，就用函数名占位
            info_list.append(f"Function Name: {name} (No detailed info found)")

    # 将所有函数信息用换行分割
    return "\n\n".join(info_list)

# 加载数据集
ds = load_dataset("Fsoft-AIC/RepoExec", split='full_context')

# 筛选出 project 等于 'test-apps/scrapy' 的数据
filtered_data = [item for item in ds if item['project'] == 'test-apps/python-string-utils']

# 初始化用于存储所有生成代码的列表
all_generated_codes = []

# 使用 tqdm 添加进度条，总数是 filtered_data 的长度
with tqdm(total=len(filtered_data), desc="Processing", unit="task") as pbar:
    for data in filtered_data:
        gt = data['solution']
        function_name=data['entry_point']
        # 提取在 ground truth 里使用过的 API 函数名
        oracle_function_names = extract_api_calls(gt)
        for name in oracle_function_names:
            if name == function_name:
                oracle_function_names.remove(name)
        # 根据函数名列表，从 JSON 中拼接对应的函数信息
        oracle_function_info = build_provided_functions_info(oracle_function_names)
        
        # 要让 GPT 补全的目标函数提示（函数签名和可选 docstring）
        target_function_prompt = data['prompt']

        # 注意：这里 prompt_template 用普通三引号字符串（没有 f 前缀）
        # 我们在后面通过 .format() 插入变量
        prompt_template = """You are an expert Python programmer. Your task is to complete the target Python function for a repository under development. You can use the functions provided below to help you.\n

Provided Functions:\n

{oracle_function_info}
\n\n
Target Function:\n
{target_function_prompt}


"""

        # 使用 format() 方法替换占位符
        prompt = prompt_template.format(
            oracle_function_info=oracle_function_info,
            target_function_prompt=target_function_prompt
        )
        
        # 系统角色提示
        sys_prompt = "You are a Python engineer; your job is to complete the function."
        
        # # （仅用于测试）可以先看看 ground truth
        # print("Ground Truth Solution:")
        # print(gt)
        # print("-----------")
        # print("Final Prompt:")
        print(prompt)
        # print("*****************")

        # 初始化用于存储当前提示的生成代码列表
        generated_codes = []
        
        for _ in range(5):
            generate_results = call_openai_api(prompt, sys_prompt)

            # 使用正则表达式提取 ```python 和 ``` 之间的内容
            match = re.search(r'```python\s*(.*?)\s*```', generate_results, re.DOTALL)
            if match:
                cleaned_code = match.group(1).strip()  # 提取并去除多余的空格
            else:
                cleaned_code = generate_results

            # 将生成的代码加入列表
            generated_codes.append(cleaned_code)

        # 将当前数据的生成代码列表加入总列表
        all_generated_codes.append(generated_codes)

        # 每处理完一条数据，更新进度条
        pbar.update(1)

# 将输出写入 'oracle_result.json'，格式为 [[pred_11, pred_12, pred_13], [pred_21, pred_22, pred_23], ...]
with open(output_file, 'w') as outfile:
    json.dump(all_generated_codes, outfile)

print(f"Results have been written to {output_file}")
