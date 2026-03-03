import requests

API_URL = "https://api.browser-use.com/api/v2/tasks"
API_KEY = "bu_EKfovz-lzSXjU4DoIXGLQrUiG_CgoV1I7CgpFchuq7Q"

headers = {
    "X-Browser-Use-API-Key": API_KEY,
    "Content-Type": "application/json"
}

data = {
    "task": "Go to https://www.bilibili.com and tell me the page title"
}

print("Sending request to browser-use API...")
response = requests.post(API_URL, headers=headers, json=data)

print(f"Status: {response.status_code}")
print(f"Response:\n{response.json()}")
