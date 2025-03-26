
filename1 = 'repo_funcs_summary/repo_funcs_extraction.py'
with open(filename1, 'r') as file:
    script_content1 = file.read()

exec(script_content1)

filename1 = 'repo_funcs_summary/repo_funcs_summary.py'
with open(filename1, 'r') as file:
    script_content1 = file.read()

exec(script_content1)

filename1 = 'ask_dependencies/generate_implementation_steps.py'
with open(filename1, 'r') as file:
    script_content1 = file.read()
exec(script_content1)
print("generate_implementation_steps.py execution completed")

filename2 = 'ask_dependencies/generate_api_description.py'
with open(filename2, 'r') as file:
    script_content2 = file.read()
exec(script_content2)
print("generate_api_description.py execution completed")

filename2 = 'ask_dependencies/generate_extended_api_description.py'
with open(filename2, 'r') as file:
    script_content2 = file.read()
exec(script_content2)
print("generate_extended_api_description.py execution completed")

filename2 = 'similarity_retrieval/similarity_retrieval.py'
with open(filename2, 'r') as file:
    script_content2 = file.read()
exec(script_content2)
print("similarity_retrieval.py execution completed")

filename1 = 'function_list_buildup/function_list_buildup.py'
with open(filename1, 'r') as file:
    script_content1 = file.read()
exec(script_content1)
print("function_list_buildup.py execution completed")

filename1 = 'final_completion.py'
with open(filename1, 'r') as file:
    script_content1 = file.read()
exec(script_content1)
print("final_completion.py execution completed")

