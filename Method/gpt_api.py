import time
import requests
import json


Baseurl =""
Skey = ""


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
