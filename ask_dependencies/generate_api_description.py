import json
from chatgpt import call_openai_api
def generate_api_description(content, possible_body):
    system_prompt="You are a Python engineer. Your job is to analyze Python code and the possible body explanation provided. Respond to user instructions by extracting and explaining specific information from the provided code and explanation."
    before_text= """
        Here is an example of your analysis:
        Code:
        ```
        def convert_to_fahrenheit(celsius_temperatures):
        ```
        Body Explanation:
        - It will create an empty list to store the converted temperatures.
        - The function will iterate over each temperature in the input list:
        - For each temperature, it will convert it to Fahrenheit using the formula \( F = \frac{9}{5} \times C + 32 \).
        - It will append each converted temperature to the new list.
        - Finally, the function will return the list of converted temperatures.

        Functions likely to be called:
        `append`: This function is used to add an item to the list of converted temperatures.
    """
    after_text = "\nGiven the code and the possible function functionality provided above, think step by step about each part of the possible function's functionality and consider what other functions may be called in the code to support or implement each step. List the functions that are likely to be called in the body and their functionalities strictly in the following format: 1.`Function name`: This function is used to ...\n2. `Function name`: This function is used to ...\n"
    prompt =  before_text+content + possible_body + after_text
    return prompt,system_prompt

if __name__ == "__main__":
    possible_bodies = {}
    with open("ask_dependencies/possible_body.jsonl", 'r', encoding='utf-8') as file1:
        for line in file1:
            record = json.loads(line)
            _id = record["_id"]
            possible_bodies[_id] = record["possible_body"]

    with open("ask_dependencies/dependencies.jsonl", 'w', encoding='utf-8') as output_file:
        with open("input/input.jsonl", "r", encoding='utf-8') as file2:
            for line in file2:
                record = json.loads(line)
                _id = record["metadata"]["_id"]
                content = record["prompt"]

                if _id in possible_bodies:
                    possible_body = possible_bodies[_id]
                    the_second_prompt,before_text = generate_api_description(content, possible_body)
                    
                    dependencies = call_openai_api(the_second_prompt, before_text)
                    dependencies=dependencies+'\n'
                    
                    output_record = {
                        "_id": _id,
                        "dependencies": dependencies
                    }

                    output_file.write(json.dumps(output_record) + "\n")