import json
import os
import re

file_list = [file for file in os.listdir('predictions/') if ('postProcess' not in file) and file.endswith('.jsonl')]
file_path_list = [os.path.join('predictions', file) for file in file_list]
# file_path_list = ['test.jsonl']

for i in range(len(file_list)):
    file_path = file_path_list[i]
    with open(file_path, encoding='utf-8') as f:
        result_list = f.readlines()
    # if len(result_list) != 1600:
    #     continue
    result_list = [json.loads(result) for result in result_list]
    for i in range(len(result_list)):
        result = result_list[i]
        prompt = result['prompt']
        choice = result['choices'][0]['text']
        choice = choice.replace(prompt, '')
        choice = choice.strip('\n')
        choice = choice.split('\n\n')[0]
        parentheses = 0
        for i in range(len(choice)):
            pass
        
        result_list[i] = json.dumps({
            "prompt": prompt,
            "choices": [{"text": choice}],
            "metadata": {}
        })
        # print(prompt[-80:])
        # print("\n---------------------\n")
        print(choice)
        print("\n---------------------\n")
        # # exit()
        import time
        time.sleep(5)
    
    with open(f'{file_path.replace(".jsonl", "")}_postProcess.jsonl', 'w', encoding='utf-8') as f:
        f.write('\n'.join(result_list))
        