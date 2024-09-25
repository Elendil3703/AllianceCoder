from callLLM.callLLM import generate
import json
from chatgpt import call_openai_api

def second_prompt(content, possible_body):
    system_prompt="You are a Python engineer. Your job is to analyze Python code and the possible body explanation provided. Respond to user instructions by extracting and explaining specific information from the provided code and explanation."
    before_text= """
        Here is an example of your analysis:
        Code:
        ```
        def convert_to_fahrenheit(celsius_temperatures):
        ```
        Body Explanation:
        - The function will start by checking if the input is a list of numerical values representing temperatures in Celsius.
        - It might raise a `TypeError` if the input is not a list or if the elements are not numbers.
        - It will create an empty list to store the converted temperatures.
        - The function will iterate over each temperature in the input list:
        - For each temperature, it will convert it to Fahrenheit using the formula \( F = \frac{9}{5} \times C + 32 \).
        - It will append each converted temperature to the new list.
        - Finally, the function will return the list of converted temperatures.

        Functions likely to be called:
        `isinstance`: This function is used to check if the input is of a specific type, such as a list or a number.
        `TypeError`: This is used to raise an exception when the input is not of the expected type.
        `append`: This function is used to add an item to the list of converted temperatures.
    """
    after_text = "\nGive the code and the possible function functionality provided above, think about what other functions may be called in the code. List the functions that are likely to be called in the body and their functionalities strictly in the following format: 1.`Function name`: This function is used to ...\n2. `Function name`: This function is used to ...\n"
    prompt =  before_text+content + possible_body + after_text
    return prompt,system_prompt

if __name__ == "__main__":
    # 读取 possible_body.jsonl 并将内容存储在字典中
    possible_bodies = {}
    with open("ask_dependencies/possible_body.jsonl", 'r', encoding='utf-8') as file1:
        for line in file1:
            record = json.loads(line)
            _id = record["_id"]
            possible_bodies[_id] = record["possible_body"]

    # 打开 output 文件准备写入
    with open("ask_dependencies/dependencies.jsonl", 'w', encoding='utf-8') as output_file:
        # 逐行读取 input.jsonl
        with open("input/input.jsonl", "r", encoding='utf-8') as file2:
            for line in file2:
                record = json.loads(line)
                _id = record["metadata"]["_id"]
                content = record["prompt"]

                # 检查 _id 是否在 possible_bodies 中
                if _id in possible_bodies:
                    possible_body = possible_bodies[_id]
                    the_second_prompt,before_text = second_prompt(content, possible_body)
                    
                    # 调用生成函数
                    dependencies = call_openai_api(the_second_prompt, before_text)
                    dependencies=dependencies+'\n'
                    
                    # 构造输出记录
                    output_record = {
                        "_id": _id,
                        "dependencies": dependencies
                    }

                    # 写入 JSONL 文件
                    output_file.write(json.dumps(output_record) + "\n")