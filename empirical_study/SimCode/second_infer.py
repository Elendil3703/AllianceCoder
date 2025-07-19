import json
from callLLM.callLLM import generate
with open("prompts/repocoder-one-gram-ws-20-ss-2.jsonl") as f:
    data = json.load(f)
    # extract the prompt from the input data
    prompt = data['prompt']
result=generate(prompt,"codellama/CodeLlama-7b-Instruct-hf", 1000, 20, 0.9,0.26)
result=result.replace(prompt,"")
output_data = {
    "result": result,
    "metadata": data['metadata']
}

# Write the processed data to a JSONL file
with open('results/result.jsonl', 'w') as outfile:
    json.dump(output_data, outfile)
