import json
import re

def main():
    # 读取 CoderEval4Python.json 文件
    with open("CoderEval4Python.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    
    records = data["RECORDS"]  # 假设文件中顶层有一个键为 "RECORDS" 的列表

    # 打开（或新建） input.jsonl 文件用于写入
    with open("datasets/input.jsonl", "w", encoding="utf-8") as fout:
        # 从 0 开始的序号计数，用于拼装 task_id
        task_counter = 0

        for record in records:
            # 筛选 project 为 "neo4j/neo4j-python-driver" 的记录
            if record.get("project") != "skorokithakis/shortuuid":
                continue

            # 1. 提取并处理 code
            code_str = record["code"]

            # 查找 """ 的位置
            triple_quotes_positions = [m.start() for m in re.finditer(r'"""', code_str)]
            if len(triple_quotes_positions) >= 2:
                start_index = 0
                end_index = triple_quotes_positions[1]
                target_function_prompt = code_str[start_index:end_index]
            else:
                # 如果找不到或只出现一次，则直接使用原始 code
                target_function_prompt = code_str
            
            # 拼上结尾的 """
            target_function_prompt += '"""'
            # 2. 组织 metadata 字段
            file_path = record["file_path"]  # 例："neo4j/_codec/hydration/v1/temporal.py"
            fpath_tuple = file_path.split("/")

            metadata = {
                "ground_truth": code_str,
                "fpath_tuple": fpath_tuple,
                "function_name": record["name"],
                "lineno": int(record["lineno"]),
                "context_start_lineno": 0,
                "_id": record["_id"],
                "task_id": f"{fpath_tuple[0]}/id{task_counter}"
            }

            # 增加 task_counter
            task_counter += 1

            # 组织最终输出记录
            out_record = {
                "prompt": target_function_prompt,
                "metadata": metadata
            }

            # 将结果按行写入 input.jsonl
            fout.write(json.dumps(out_record, ensure_ascii=False) + "\n")

if __name__ == "__main__":
    main()
