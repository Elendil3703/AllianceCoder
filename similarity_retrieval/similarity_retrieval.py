import torch
from unixcoder import UniXcoder
import numpy as np
from tqdm import tqdm
import re
import json

# Initialize UniXcoder model
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = UniXcoder("microsoft/unixcoder-base")
model.to(device)

def get_embedding(text):
    # Use UniXcoder to get text embeddings
    tokens_ids = model.tokenize([text], max_length=512, mode="<encoder-only>")
    source_ids = torch.tensor(tokens_ids).to(device)
    tokens_embeddings, text_embedding = model(source_ids)
    embedding = torch.nn.functional.normalize(text_embedding, p=2, dim=1)
    return embedding.detach().cpu().numpy().flatten()  # Flatten to 1D array

def cosine_similarity(vec1, vec2):
    # Cosine similarity between two normalized vectors
    return np.dot(vec1, vec2)

def read_input_jsonl(file_path):
    _id_to_function_name = {}
    with open(file_path, 'r', encoding='utf-8') as jsonl_file:
        for line in jsonl_file:
            record = json.loads(line)
            _id = record['metadata']['_id']
            function_name = record['metadata']['function_name']
            _id_to_function_name[_id] = function_name
    return _id_to_function_name

def similarity_retrieval():
    # Regular expression to find function content
    regex_dash = r"(?:\*\*)?`[^`]+`(?:\*\*)?:\s(.*?)(?=\n\d+\.|$)"  # Matches function description after function name

    predict_functionality = []  # To store found function content
    ids = []  # To store corresponding _id

    # Read input/input.jsonl to get mapping from _id to function_name
    _id_to_function_name = read_input_jsonl('input/input.jsonl')

    # Open file and read line by line
    with open("ask_dependencies/dependencies.jsonl", 'r') as dependency:
        for line in dependency:
            record = json.loads(line)
            _id = record["_id"]
            matches_dash = re.findall(regex_dash, record["all_dependencies"], re.DOTALL)  # Find all matches
            if matches_dash:
                for match in matches_dash:  # Iterate over all matches
                    predict_functionality.append(match.strip())
                    ids.append(_id)  # Add _id to ids list
            else:
                # If no match is found, append empty content for the _id
                print(f"No match found for _id: {_id}")  # Print the _id for which no match is found
                predict_functionality.append("")  # Empty content
                ids.append(_id)

    # Load function summaries
    function_summaries = []
    with open("repo_funcs_summary/function_summaries.json", 'r', encoding='utf-8') as jsonfile:
        data = json.load(jsonfile)
        for entry in data:
            function_summaries.append(
                {
                    "function_name": entry['function_name'],
                    "summary": entry['summary']
                }
            )

    summaries = [entry['summary'] for entry in function_summaries]

    # Load function details
    function_details = []
    with open("repo_funcs_summary/function_details.json", 'r', encoding='utf-8') as jsonfile:
        data = json.load(jsonfile)
        for entry in data:
            function_details.append(
                {
                    "name": entry["name"],
                    "docstring": entry["docstring"] if entry["docstring"] is not None else "No docstring provided",
                    "args": entry["args"],
                    "defaults": entry["defaults"],
                    "code": entry["code"],
                    "class": entry["class"],
                    "file": entry["file"]
                }
            )

    # Pre-compute embeddings for all summaries
    summary_embeddings = []
    for summary in tqdm(summaries, desc="Calculating summary embeddings"):
        summary_embeddings.append(get_embedding(summary))

    output_data = []

    # Iterate over each dependency
    for idx, query in enumerate(tqdm(predict_functionality, desc="Processing queries", total=len(predict_functionality))):
        _id = ids[idx]
        query_embedding = get_embedding(query) if query else None  # Handle empty query case

        if query_embedding is not None:
            # Compute similarities between query and all function summaries
            similarities = [
                cosine_similarity(query_embedding, summary_embedding)
                for summary_embedding in summary_embeddings
            ]

            # Convert similarities to a NumPy array
            similarities = np.array(similarities)

            # Get indices sorted by decreasing similarity
            sorted_indices = np.argsort(similarities)[::-1]

            # Get the function name to skip for this _id
            function_name_to_skip = _id_to_function_name.get(_id, None)

            best_match = None
            matching_function_detail = None

            # Iterate over sorted indices to find the best match that is not the same function
            for idx_in_sorted in sorted_indices:
                best_match_candidate = function_summaries[idx_in_sorted]
                candidate_function_name = best_match_candidate['function_name']

                if candidate_function_name != function_name_to_skip:
                    # Found a function with a different name
                    best_match = best_match_candidate

                    # Find matching function detail
                    matching_function_detail = next(
                        (item for item in function_details if item["name"] == candidate_function_name),
                        None
                    )
                    break  # Exit the loop as we have found our best match

            if best_match and matching_function_detail:
                entry = {
                    "_id": _id,
                    "Query": query,
                    "Function Name": matching_function_detail['name'],
                    "Docstring": matching_function_detail['docstring'],
                    "Arguments": ', '.join(matching_function_detail['args']),
                    "Defaults": matching_function_detail['defaults'],
                    "Code": matching_function_detail['code'],
                    "Class": matching_function_detail['class'],
                    "File": matching_function_detail['file']
                }
                output_data.append(entry)
            else:
                # Could not find a suitable match
                output_data.append({
                    "_id": _id,
                    "Query": query,
                    "Function Name": "",
                    "Docstring": "",
                    "Arguments": "",
                    "Defaults": [],
                    "Code": ""
                })
        else:
            # Handle case where the query is empty
            output_data.append({
                "_id": _id,
                "Query": "",
                "Function Name": "",
                "Docstring": "",
                "Arguments": "",
                "Defaults": [],
                "Code": ""
            })

    # Write the results to a JSON file
    with open("similarity_retrieval/retrieved_functions.json", 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=4)

if __name__ == "__main__":
    similarity_retrieval()