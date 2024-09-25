import json
import re
from chatgpt import call_openai_api  # 使用前面定义的 call_openai_api 函数
from tqdm import tqdm  # 引入 tqdm 用于进度条

if __name__ == "__main__":
    # 读取 dependencies.jsonl 并将内容存储在字典中
    dependencies_records = {}
    with open("LLM_doublecheck/function_list.jsonl", 'r', encoding='utf-8') as f:
        for line in f:
            record = json.loads(line)
            _id = record["_id"]
            dependencies_records[_id] = record["function_list"]

    # 读取 possible_body.jsonl 并将内容存储在字典中
    possible_bodies = {}
    with open("ask_dependencies/possible_body.jsonl", 'r', encoding='utf-8') as file1:
        for line in file1:
            record = json.loads(line)
            _id = record["_id"]
            possible_bodies[_id] = record["possible_body"]

    # 初始化结果列表，用于保存生成的结果
    all_results = []

    # 读取 target_function.jsonl 并生成新的 output
    with open("input/input.jsonl", "r", encoding='utf-8') as file2:
        # 使用 tqdm 为文件中的记录添加进度条
        total_lines = sum(1 for line in open("input/input.jsonl", "r", encoding='utf-8'))
        for line in tqdm(file2, total=total_lines, desc="Processing Records"):
            record = json.loads(line)
            _id = record["metadata"]["_id"]
            target_function = record["prompt"]

            # 检查 _id 是否在 possible_bodies 和 dependencies_records 中
            if _id in possible_bodies and _id in dependencies_records:
                possible_body = possible_bodies[_id]
                dependencies = dependencies_records[_id]

                # 构建新的系统和用户提示
                sys_prompt = (
                    "You are a Python engineer. Your job is to complete the target function."
                )
                prompt = (
                    "Complete the target function based on the given possible body. You can use the functions in the function list to help you when needed. Please only write the complete target function and don't include anything else.\n"
                    f"Target Function: {target_function}\n"
                    f"Possible body of the function: {possible_body}\n"
                    f"Function List: {dependencies}\n"
                    f"Please complete the target function."
                )

                # 初始化用于存储生成的代码的列表
                generated_codes = []

                # 调用 GPT-3.5-turbo 模型生成结果 5 次
                for _ in range(5):
                    generate_results = call_openai_api(prompt, sys_prompt)
                    match = re.search(r'```python\s*(.*?)\s*```', generate_results, re.DOTALL)
                    if match:
                        cleaned_code = match.group(1).strip()  # 提取并去除多余的空格
                    else:
                        cleaned_code = generate_results
                    
                    # 将生成的代码加入列表
                    generated_codes.append(cleaned_code)

                # 将生成的代码加入结果列表
                all_results.append(generated_codes)

    # 将生成结果保存到 gpt_result.json 文件中
    with open("ACR_result.json", 'w', encoding='utf-8') as out_file:
        json.dump(all_results, out_file, indent=4)

    print("Summaries have been saved to gpt_result.json")