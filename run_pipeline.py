filename1 = 'repo_funcs_summary/repo_funcs_extraction.py'
with open(filename1, 'r') as file:
    script_content1 = file.read()

exec(script_content1)

filename1 = 'repo_funcs_summary/repo_funcs_summary.py'
with open(filename1, 'r') as file:
    script_content1 = file.read()

exec(script_content1)

filename1 = 'input/handle_input.py'
with open(filename1, 'r') as file:
    script_content1 = file.read()
exec(script_content1)
print("handle_input.py execution completed")

filename1 = 'ask_dependencies/first_prompt.py'
with open(filename1, 'r') as file:
    script_content1 = file.read()
exec(script_content1)
print("first_prompt.py execution completed")

filename2 = 'ask_dependencies/second_prompt.py'
with open(filename2, 'r') as file:
    script_content2 = file.read()
exec(script_content2)
print("second_prompt.py execution completed")

filename2 = 'ask_dependencies/third_prompt.py'
with open(filename2, 'r') as file:
    script_content2 = file.read()
exec(script_content2)
print("third_prompt.py execution completed")

filename2 = 'similarity_retrieval/similarity_retrieval.py'
with open(filename2, 'r') as file:
    script_content2 = file.read()
exec(script_content2)
print("similarity_retrieval.py execution completed")

filename1 = 'LLM_doublecheck/LLM_doublecheck.py'
with open(filename1, 'r') as file:
    script_content1 = file.read()
exec(script_content1)
print("LLM_doublecheck.py execution completed")

filename1 = 'final_completion.py'
with open(filename1, 'r') as file:
    script_content1 = file.read()
exec(script_content1)
print("final_completion.py execution completed")