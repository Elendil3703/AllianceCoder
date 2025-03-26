import json
from chatgpt import call_openai_api
def generate_implementation_steps(content):
    system_prompt="You are a Python engineer. Your job is to analyze Python code and interpret annotations provided. Respond to user instructions by extracting and explaining specific information from the code."
    prompt = """
    Here are a few examples of possible function body breakdowns:

    Example 1:
    Code: 
    ```python
    def calculate_area(radius):
    ```

    Explanation in bullet points:
    - The function will calculate the area using the formula for the area of a circle: \( A = \pi \times r^2 \).
      - This will involve importing the `math` module to access the value of `pi`.
    - The function will return the calculated area as a floating-point number.

    Example 2:
    Code: 
    ```python
    def find_max_value(numbers):
    ```

    Explanation in bullet points:
    - It will initialize a variable to store the maximum value, starting with the first element of the list.
    - The function will iterate over the list of numbers:
      - For each number, it will compare it with the current maximum value.
      - If a larger value is found, it will update the maximum value.
    - After the loop, the function will return the maximum value found.

    Example 3:
    Code: 
    ```python
    def convert_to_fahrenheit(celsius_temperatures):
    ```

    Explanation in bullet points:
    - It will create an empty list to store the converted temperatures.
    - The function will iterate over each temperature in the input list:
      - For each temperature, it will convert it to Fahrenheit using the formula \( F = \frac{9}{5} \times C + 32 \).
      - It will append each converted temperature to the new list.
    - Finally, the function will return the list of converted temperatures.

    Example 4:
    Code:
    ```python
    def find_user(users, username):
    ```

    Explanation in bullet points:
    - it will retrieve the corresponding user data from the dictionary.
    - The function will return the user data associated with the provided `username`.

    Now, given the code provided below, break down the possible body of the function step by step using bullet points.
    Code:
    """ + content + """

    ### Breakdown in bullet points:
    - ...
    """
    
    
    return system_prompt,prompt


if __name__ == "__main__":
    output_data = []
    with open("input/input.jsonl", "r") as file1:
        for line in file1:
            record=json.loads(line)
            content=record["prompt"]
            _id = record["metadata"]["_id"]
            system_prompt,prompt=generate_implementation_steps(content) 
            possible_body=call_openai_api(prompt,system_prompt)
            
            possible_body=str(possible_body) 
            output_record = {
                "_id": _id,
                "possible_body": possible_body
            }
            output_data.append(output_record) 
    with open("ask_dependencies/possible_body.jsonl", 'w') as file2:
        for record in output_data:
            file2.write(json.dumps(record) + "\n")
    