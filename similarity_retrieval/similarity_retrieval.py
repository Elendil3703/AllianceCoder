import torch
from unixcoder import UniXcoder
import numpy as np
from tqdm import tqdm
import re
import json

# Initialize UniXcoder model
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = UniXcoder("microsoft/unixcoder-base")
model.to(device)

def get_embedding(text):
    # 使用 UniXcoder 获取文本嵌入
    tokens_ids = model.tokenize([text], max_length=512, mode="<encoder-only>")
    source_ids = torch.tensor(tokens_ids).to(device)
    tokens_embeddings, text_embedding = model(source_ids)
    
    # 返回嵌入并进行归一化，使用 detach() 分离计算图
    return torch.nn.functional.normalize(text_embedding, p=2, dim=1).detach().cpu().numpy()

def cosine_similarity(vec1, vec2):
    # Cosine similarity between two normalized vectors
    vec1 = np.array(vec1)
    vec2 = np.array(vec2)
    return np.dot(vec1, vec2.T)

def similarity_retrieval():
    # 正则表达式用于找到函数内容
    regex_dash = r": (.*?)\." #匹配:和.之间的内容
    predict_functionality = []  # 用于存储找到的函数内容
    ids = []  # 用于存储对应的_id
    
    # 打开文件并逐行读取
    with open("ask_dependencies/dependencies.jsonl", 'r') as dependency:
        for line in dependency:
            record = json.loads(line)
            _id = record["_id"]
            matches_dash = re.findall(regex_dash, record["all_dependencies"])  # 找到所有匹配项
            if matches_dash:
                for match in matches_dash:  # 遍历所有匹配项
                    predict_functionality.append(match.strip())
                    ids.append(_id)  # 将_id添加到ids列表中
    
    # 加载函数摘要
    function_summaries = []
    with open("repo_funcs_summary/function_summaries.json", 'r', encoding='utf-8') as jsonfile:
        data = json.load(jsonfile)
        for entry in data:
            function_summaries.append(
                {
                    "function_name": entry['function_name'],
                    "summary": entry['summary']
                }
            )

    summaries = [entry['summary'] for entry in function_summaries]

    # 加载函数详细信息
    function_details = []
    with open("repo_funcs_summary/function_details.json", 'r', encoding='utf-8') as jsonfile:
        data = json.load(jsonfile)
        for entry in data:
            function_details.append(
                {
                    "name": entry["name"],
                    "docstring": entry["docstring"] if entry["docstring"] is not None else "No docstring provided",
                    "args": entry["args"],
                    "defaults": entry["defaults"],
                    "code": entry["code"]
                }
            )

    # 预先计算所有摘要的嵌入
    summary_embeddings = []
    for summary in tqdm(summaries, desc="Calculating summary embeddings"):
        summary_embeddings.append(get_embedding(summary))  # 计算并存储每个摘要的嵌入

    output_data = []

    # 遍历每一个 dependency
    for idx, query in enumerate(tqdm(predict_functionality, desc="Processing queries", total=len(predict_functionality))):
        query_embedding = get_embedding(query)  # 使用 UniXcoder 获取当前 query 的嵌入

        # 计算当前 query 和所有函数摘要的相似度
        similarities = [
            cosine_similarity(query_embedding, summary_embedding)  # 用预先计算的摘要嵌入
            for summary_embedding in summary_embeddings
        ]

        # 找到相似度最高的函数
        max_index = np.argmax(similarities)
        best_match = function_summaries[max_index]

        # 用 function_name 找到详细信息
        matching_function_detail = next(
            (item for item in function_details if item["name"] == best_match['function_name']),
            None
        )

        if matching_function_detail:
            entry = {
                "_id": ids[idx],
                "Query": query,
                "Function Name": matching_function_detail['name'],
                "Docstring": matching_function_detail['docstring'],
                "Arguments": ', '.join(matching_function_detail['args']),
                "Defaults": matching_function_detail['defaults'],
                "Code": matching_function_detail['code']
            }
            output_data.append(entry)

    # 将结果写入 JSON 文件
    with open("similarity_retrieval/retrieved_functions.json", 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=4)

if __name__ == "__main__":
    similarity_retrieval()