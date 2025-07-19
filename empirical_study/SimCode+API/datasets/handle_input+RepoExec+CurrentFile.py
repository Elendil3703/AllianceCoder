import json
from datasets import load_dataset
# 读取 JSON 文件内容
import os
ds = load_dataset("Fsoft-AIC/RepoExec", split='full_context')
filtered_data = [item for item in ds if item['project'] == 'test-apps/apimd']
base_dir="repositories/function_level"
# 打开文件，以便连续写入多行 JSON 数据
with open('datasets/input.jsonl', 'w', encoding='utf-8') as jsonl_file:
    # 初始化计数器
    idx_counter = 0

    # 遍历每个 record
    for data in filtered_data:
        _id = idx_counter
        ground_truth = data["solution"]
        file_path = data["module"]
        # 按你原先的方式拼接 fpath_tuple：最后一段加 .py
        fpath_tuple = tuple(file_path.split('.'))
        fpath_tuple = fpath_tuple[:-1] + (f"{fpath_tuple[-1]}.py",)

        # 构造本地真实文件路径（示例：在 base_dir 下拼接）
        # 例如: fpath_tuple = ("scrapy", "spider.py")，那就变成 base_dir/scrapy/spider.py
        local_file_path = os.path.join(base_dir, *fpath_tuple)
        
        # 搜索 target_function_prompt 在文件中的出现位置
        snippet = data["target_function_prompt"]
        
        # 默认为0; 若找不到就维持0; 找到则更新
        lineno = 0
        
        if os.path.isfile(local_file_path):
            try:
                with open(local_file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 在文件完整文本里查找 prompt
                idx = content.find(snippet)
                if idx != -1:
                    # 计算 prompt 的起始行：统计 idx 之前有多少个换行符
                    snippet_start_line = content[:idx].count('\n')
                    # prompt本身可能有多行，这里统计它包含多少行
                    snippet_lines = snippet.count('\n') + 1

                    # 假设：你要的是“prompt片段最后一行的下一行的再下一行”
                    # 即 snippet_start_line + snippet_lines 后面再 +1
                    # (如果只想要“prompt最后一行的下一行”就只加 snippet_start_line + snippet_lines)
                    lineno = snippet_start_line + snippet_lines + 1
            except Exception as e:
                print(f"无法读取或搜索文件: {local_file_path}, 错误: {e}")
        else:
            print(f"文件不存在: {local_file_path}，将 lineno 设为0")

        # 获取 file_path 并分割为 fpath_tuple
        
        fpath_tuple = tuple(file_path.split('.'))
        fpath_tuple = fpath_tuple[:-1] + (f"{fpath_tuple[-1]}.py",)
        # 创建一个字典，将数据添加到 prompt 字段，并包含其他元数据
        output_dict = {
            "prompt": data["prompt"],
            "metadata": {
                "task_id": f"{fpath_tuple[0]}/id{idx_counter}",  # 使用递增的 id
                "ground_truth": ground_truth,
                "fpath_tuple": fpath_tuple,  # 使用分割后的路径元组                
                "function_name": data["entry_point"],
                "lineno": lineno,   
                "context_start_lineno": 0,
                "_id": _id
            }
        }

        # 将字典写入 JSONL 文件，每个字典占一行
        jsonl_file.write(json.dumps(output_dict) + "\n")

        # 递增计数器
        idx_counter += 1