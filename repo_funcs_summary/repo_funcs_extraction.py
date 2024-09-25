import ast
import os
import json  # 导入json模块

class FunctionInfoExtractor(ast.NodeVisitor):
    def __init__(self, source_code):
        self.functions = []
        self.source_code = source_code.splitlines()  # Split source code into lines

    def visit_FunctionDef(self, node):
        function_info = {
            "name": node.name,
            "docstring": ast.get_docstring(node),
            "args": [arg.arg for arg in node.args.args],
            "defaults": [ast.unparse(d) for d in node.args.defaults],
            #"start_line": node.lineno,
            #"end_line": node.end_lineno,
            "code": self.extract_source_code(node)
        }
        self.functions.append(function_info)

    def extract_source_code(self, node):
        # Extract the lines of code for the function, from start_line to end_line
        return "\n".join(self.source_code[node.lineno - 1: node.end_lineno])

def find_functions_in_file(file_path):
    with open(file_path, "r") as source:
        source_code = source.read()
        tree = ast.parse(source_code, filename=file_path)
        extractor = FunctionInfoExtractor(source_code)
        extractor.visit(tree)
        return extractor.functions

def find_functions_in_directory(directory):
    functions = []
    for subdir, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(subdir, file)
                functions.extend(find_functions_in_file(file_path))
    return functions

# 使用函数
repo_path = 'input/python-string-utils'
all_functions = find_functions_in_directory(repo_path)

# 将结果写入JSON文件
output_file = 'repo_funcs_summary/function_details.json'
with open(output_file, 'w') as f:
    json.dump(all_functions, f, indent=4)  # 格式化输出

print(f"Function details saved to {output_file}")