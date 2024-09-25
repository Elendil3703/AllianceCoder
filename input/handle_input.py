import json
from datasets import load_dataset
# 读取 JSON 文件内容

ds = load_dataset("Fsoft-AIC/RepoExec", split='full_context')
filtered_data = [item for item in ds if item['project'] == 'test-apps/python-string-utils']

# 打开文件，以便连续写入多行 JSON 数据
with open('input/input.jsonl', 'w', encoding='utf-8') as jsonl_file:
    # 初始化计数器
    idx_counter = 1

    # 遍历每个 record
    for data in filtered_data:
        _id = idx_counter
        ground_truth = data["solution"]

        

        # 获取 file_path 并分割为 fpath_tuple
        file_path = data["module"]
        fpath_tuple = tuple(file_path.split('.'))

        # 创建一个字典，将数据添加到 prompt 字段，并包含其他元数据
        output_dict = {
            "prompt": data["target_function_prompt"],
            "metadata": {
                "task_id": f"python-string-utils/id{idx_counter}",  # 使用递增的 id
                "ground_truth": ground_truth,
                "fpath_tuple": fpath_tuple,  # 使用分割后的路径元组                
                "function_name": data["entry_point"],
                "_id": _id
            }
        }

        # 将字典写入 JSONL 文件，每个字典占一行
        jsonl_file.write(json.dumps(output_dict) + "\n")

        # 递增计数器
        idx_counter += 1