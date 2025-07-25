import json
import re
from collections import defaultdict

input_path = "input/execrepobench_data.jsonl"
output_path = "input/input.jsonl"

# 用来跟踪每个repo_name中已经处理多少条
repo_counters = defaultdict(int)

with open(input_path, "r", encoding="utf-8") as fin, open(output_path, "w", encoding="utf-8") as fout:
    for line in fin:
        item = json.loads(line)
        repo_name = item["repo_name"]

        # 只处理repo_name为Chronyk的记录
        if repo_name != "algorithms":
            continue

        file_name = item["file_name"]
        prefix_code = item["prefix_code"]
        middle_code = item["middle_code"]
        task_id = item.get("task_id", None)

        # 统计当前条在此repo中的idx
        idx = repo_counters[repo_name]
        repo_counters[repo_name] += 1

        # prompt：从最后一个def开始到prefix_code结尾
        def_matches = list(re.finditer(r'\bdef\b', prefix_code))
        if def_matches:
            last_def_pos = def_matches[-1].start()
            prompt = prefix_code[last_def_pos:]
        else:
            # 如果没有def，就用整个prefix_code
            prompt = prefix_code

        # 拆分 file_name 生成 fpath_tuple
        fpath_tuple = tuple(file_name.strip("/").split("/"))

        # 构造 metadata
        metadata = {
            "task_id": task_id,
            "ground_truth": middle_code,
            "fpath_tuple": fpath_tuple,
            "function_name": "",
            "lineno": 0,
            "context_start_lineno": 0,
            "_id": idx,
        }

        new_item = {
            "prompt": prompt,
            "current_file": prefix_code,
            "metadata": metadata,
        }

        fout.write(json.dumps(new_item, ensure_ascii=False) + "\n")

print(f"转换完成，输出文件：{output_path}")