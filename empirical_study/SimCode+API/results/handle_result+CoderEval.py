import json
from collections import defaultdict

def main():
    # 初始化一个字典，用于根据 _id 收集 choices
    results_by_id = defaultdict(list)

    # 读取 results/result.jsonl 文件
    with open("results/result.jsonl", "r", encoding="utf-8") as input_file:
        for line in input_file:
            record = json.loads(line)
            _id = record["metadata"]["_id"]
            choices = record["choices"]
            # 将 choices 添加到对应 _id 的列表中
            results_by_id[_id].append(choices)
    #print(results_by_id["62e60e05d76274f8a4026cfd"])
    # 准备输出数据
    all_results = []
    for _id, choices in results_by_id.items():
        result_record = {
            "_id": _id,
            "generate_results":choices[0]  # 去重，确保没有重复代码
        }
        all_results.append(result_record)

    # 将结果写入 RepoCoder_result.jsonl
    with open("RepoCoder_result.jsonl", "w", encoding="utf-8") as output_file:
        for result in all_results:
            output_file.write(json.dumps(result, ensure_ascii=False) + "\n")

    print("Results successfully written to RepoCoder_result.jsonl.")

if __name__ == "__main__":
    main()
