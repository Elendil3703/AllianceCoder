import requests

def call_openai_api(prompt, system_content="You are a helpful assistant."):
    model = "your_model"
    api_key ="your_api_key"
    
    if not api_key:
        raise ValueError("OpenAI API key is not provided.")

    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    data = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_content},
            {"role": "user", "content": prompt}
        ]
    }

    response = requests.post(url, headers=headers, json=data)

    if response.status_code == 200:
        result = response.json()
        if 'choices' in result and len(result['choices']) > 0:
            return result['choices'][0]['message']['content']
        else:
            raise Exception("No valid response from the API")
    else:
        raise Exception(f"Error {response.status_code}: {response.text}")

