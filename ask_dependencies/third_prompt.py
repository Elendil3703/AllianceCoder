from callLLM.callLLM import generate
import json
from chatgpt import call_openai_api
if __name__ == "__main__":
    # 读取 dependencies.jsonl 并将内容存储在字典中
    dependencies_records = {}
    with open("ask_dependencies/dependencies.jsonl", 'r', encoding='utf-8') as f:
        for line in f:
            record = json.loads(line)
            _id = record["_id"]
            dependencies_records[_id] = record["dependencies"]

    # 读取 possible_body.jsonl 并将内容存储在字典中
    possible_bodies = {}
    with open("ask_dependencies/possible_body.jsonl", 'r', encoding='utf-8') as file1:
        for line in file1:
            record = json.loads(line)
            _id = record["_id"]
            possible_bodies[_id] = record["possible_body"]

    # 读取 target_function.jsonl 并生成新的 dependencies.jsonl
    with open("ask_dependencies/dependencies.jsonl", 'w', encoding='utf-8') as output_file:
        with open("input/input.jsonl", "r", encoding='utf-8') as file2:
            for line in file2:
                record = json.loads(line)
                _id = record["metadata"]["_id"]
                target_function = record["prompt"]

                # 检查 _id 是否在 possible_bodies 和 dependencies_records 中
                if _id in possible_bodies and _id in dependencies_records:
                    possible_body = possible_bodies[_id]
                    dependencies = dependencies_records[_id]

                    # 构建新的 prompt
                    sys_prompt = (
                        f"You are a Python engineer. Your job is to speculate other possible functions "
                        f"that the target function may call based on the given function and its possible body and existing dependencies.\n")
                    prompt=(
                        f"Target Function: {target_function}\n"
                        f"Possible body of the function: {possible_body}\n"
                        f"Existing Dependencies: {dependencies}\n"
                        f"Please speculate other possible functions that the target function may need to call based on the given function "
                        f"and its possible body and existing dependencies. Please list all the functions in the following format:\n"
                        f"1. `Function name`: This function is used to ..."
                    )

                    # 调用生成函数
                    all_dependencies =call_openai_api(prompt,sys_prompt)

                    # 构造输出记录
                    output_record = {
                        "_id": _id,
                        "all_dependencies": all_dependencies
                    }

                    # 写入 JSONL 文件
                    output_file.write(json.dumps(output_record) + "\n")