import time
import requests
import json

# Baseurl = "https://api.claudeshop.top"
# Skey = "sk-ESaMW4UBGX1Y3YfFRjo74TIFaDlmyS5o16zHReiBGgxvYvo4"
# Skey ="sk-JTm49RbiDIuG9rMxXFuOQrmhTvaQjDaAH9c0yFwjebDInbGX"
Baseurl ="http://35.220.164.252:3888/"
Skey = "sk-b7QfNvfuYfn7ZyvGeTz9Ol37dQaUph829zxdGfXzMT2GCDlp"

# Skey = "sk-BzAetTYOwKxji5BnJiW3VBhbDIyVsp5Uo2leR9XYxXEHThjr"


# Skey = "sk-svowCeqZw45Y7t1GJnuiOw5v9Rg9btsqWbPEa9IBSshZj4bm"
# Skey = "sk-fwarlRh82SYNbVQKxglcjXjHfLQ9yT8spFDuRQXbe4dhrvMx"
# Function to make API requests with retries
# Baseurl = "https://boyuerichdata.chatgptten.com"


# https://api.claudeshop.top/v1
# https://dashscope.aliyuncs.com/compatible-mode/v1
# https://boyuerichdata.chatgptten.com/v1/
def api_request(messages,temperature = 1.0, max_retries=60, sleep_time=15):
    # url = Baseurl + "/v1/chat/completions"
    url = Baseurl + "/v1/chat/completions"
    headers = {
        'Accept': 'application/json',
        'Authorization': f'Bearer {Skey}',
        'User-Agent': 'Apifox/1.0.0 (https://apifox.com)',
        'Content-Type': 'application/json'
    }
    payload = json.dumps({
        # "model": "gpt-4o-2024-08-06",
        "model": "gpt-4o-mini",
        "messages": [{"role": "system", "content": "You are a helpful assistant."},
                     {"role": "user", "content": messages}],
        "temperature":temperature
    })
    
    for attempt in range(max_retries):
        print(f"Attempt:{attempt}")
        try:
            response = requests.post(url, headers=headers, data=payload, timeout=(60,60))
            # If the request is successful, return the result
            if response.status_code == 200:
                return response.json()["choices"][0]["message"]["content"].strip()
            else:
                raise Exception(f"API request failed with status {response.status_code}: {response.text}")
        except Exception as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            # Sleep for the specified amount of time before retrying
            if attempt < max_retries - 1:
                print(f"Retrying in {sleep_time} seconds...")
                time.sleep(sleep_time)  # Sleep for 15 seconds before retry
            else:
                raise Exception(f"All {max_retries} attempts failed. Last error: {e}")

# # Function to generate verifier's hypothesis
# def gpt(prompt):
#     hypothesis = api_request(prompt)
#     return hypothesis
