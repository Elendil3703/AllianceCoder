import json

# 定义文件路径
result_file_path = 'results/result.jsonl'
output_file_path = 'RepoCoder_result.json'

# 初始化一个字典用于根据 _id 存储预测结果
predictions_by_id = {}

# 逐行读取 result.jsonl 文件
with open(result_file_path, 'r', encoding='utf-8') as result_file:
    for line in result_file:
        # 解析每一行数据
        result_data = json.loads(line)
        
        # 获取 _id
        _id = result_data['metadata']['_id']
        
        # 假设预测结果在 result_data['choices'][0]['message']['content'] 中
        # 根据您的数据结构，调整下面这行代码
        prediction = result_data.get('result') or result_data.get('prediction') or result_data.get('choices')

        # 将预测结果添加到对应的 _id 列表中
        if _id not in predictions_by_id:
            predictions_by_id[_id] = []
        predictions_by_id[_id].append(prediction)

# 按照 _id 排序
sorted_ids = sorted(predictions_by_id.keys())

# 按照排序后的 _id 提取预测结果列表
sorted_predictions = [predictions_by_id[_id] for _id in sorted_ids]

# 将结果写入 RepoCoder_result.json，格式为 [[pred_11, pred_12, pred_13], [pred_21, pred_22, pred_23], ...]
with open(output_file_path, 'w', encoding='utf-8') as output_file:
    json.dump(sorted_predictions, output_file, ensure_ascii=False, indent=4)

print(f"Results have been written to {output_file_path}")