import requests
def call_openai_api(prompt, system_content="You are a helpful assistant."):
    """
    调用 OpenAI API 生成聊天回复。

    参数:
    - prompt: 用户输入的内容（字符串）
    - model: 使用的模型名称（默认为 "gpt-3.5-turbo"）
    - system_content: 系统消息的内容（默认为 "You are a helpful assistant."）
    - api_key: OpenAI API 密钥，如果未提供，将从环境变量中读取

    返回:
    - 成功时返回生成的消息内容（字符串）
    - 出错时抛出异常并返回错误消息
    """
    model="gpt-4o-mini"
    api_key ="your-api-key"
    if api_key is None:
        raise ValueError("OpenAI API key is not provided.")

    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    data = {
        "model": model,
        "messages": [
            {
                "role": "system",
                "content": system_content
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
    }

    response = requests.post(url, headers=headers, json=data)

    # 检查请求是否成功
    if response.status_code == 200:
        return response.json()['choices'][0]['message']['content']
    else:
        raise Exception(f"Error {response.status_code}: {response.text}")

if __name__ == "__main__":
    try:
        response = call_openai_api("Hello!")
        print("Response from OpenAI:", response)
    except Exception as e:
        print(e)