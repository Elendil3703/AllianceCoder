import json
import logging
import os
from tqdm import tqdm  
from chatgpt import call_openai_api

# Read function information
with open('repo_funcs_summary/function_details.json', 'r') as file:
    functions = json.load(file)

results = []

# Try to continue from the last saved position
if os.path.exists('repo_funcs_summary/function_summaries.json'):
    with open('repo_funcs_summary/function_summaries.json', 'r') as out_file:
        try:
            existing_data = json.load(out_file)
            results.extend(existing_data)
            start_index = len(existing_data)
        except json.JSONDecodeError:
            logging.warning("Failed to decode JSON, starting from scratch.")
            results = []
            start_index = 0
else:
    start_index = 0

# Use tqdm for progress tracking
for i in tqdm(range(start_index, len(functions))):
    function = functions[i]
    name = function['name']
    docstring = function.get('docstring', 'No docstring provided')
    args = ', '.join(function['args'])
    defaults = ', '.join([str(d) for d in function['defaults']])
    code = function['code'].replace('\n', '\\n')  # Adjust newlines for single-line string

    # Build prompt
    summary = call_openai_api(
        f"Here is the description of the function:\nFunction Name: {name}\nDocstring: {docstring}\nArguments: {args}\nDefaults: {defaults}\nCode: {code}\nFor this function, please provide a brief summary of its functionality. Your answer should start with: \"This function is used to...\".",
        "You are a Python engineer. Your job is to analyze the provided Python function and summarize its functionality."
    )
    print(summary)
    
    # Save the result
    results.append({
        "function_name": name,
        "summary": summary
    })

# Write to file once after processing all functions
with open('repo_funcs_summary/function_summaries.json', 'w') as out_file:
    json.dump(results, out_file, indent=4)
    
print("Summaries have been saved to function_summaries.json")
