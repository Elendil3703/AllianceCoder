import json
from collections import defaultdict
from tqdm import tqdm

# 读取 JSON 数据
with open("similarity_retrieval/retrieved_functions.json", 'r', encoding='utf-8') as jsonfile:
    retrieved_functions = json.load(jsonfile)

# 用于存储每个 _id 对应的函数信息
id_to_functions = defaultdict(list)

# 遍历每个 JSON 对象
for entry in tqdm(retrieved_functions, desc="Processing Entries"):
    _id = entry['_id']
    query = entry['Query']
    details = f'"_id": "{_id}", '  # 将 _id 添加到 details 中

    # 遍历条目中的键和值，除了 "Query" 和 "_id"
    for key, value in entry.items():
        if key != "Query" and key != "_id":  # 排除 "Query" 和 "_id" 本身，因为 _id 已经手动添加了
            if isinstance(value, list):  # 如果值是列表，将其转换为字符串
                value = ', '.join(value)
            details += f'"{key}": "{value}", '
    
    details = details.strip(', ')  # 移除最后一个逗号
    
    id_to_functions[_id].append(details)

# 确保每个 _id 至少有一个空的 function_list
for _id in retrieved_functions:
    if _id['_id'] not in id_to_functions:
        id_to_functions[_id['_id']] = []  # 如果没有任何匹配项，初始化为空列表

# 写入到 JSONL 文件中
with open("function_list_buildup/function_list.jsonl", 'w', encoding='utf-8') as f:
    for _id, function_list in id_to_functions.items():
        # 创建一个包含 _id 和它所有函数列表的 JSON 对象
        json_obj = {
            "_id": _id,
            "function_list": function_list
        }
        # 将每个 JSON 对象写入文件
        f.write(json.dumps(json_obj, ensure_ascii=False) + '\n')