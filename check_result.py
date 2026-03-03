import requests
import time

API_URL = "https://api.browser-use.com/api/v2/tasks"
TASK_ID = "2d70d2ee-6ea5-4cee-ab6d-05318e360c76"
API_KEY = "bu_EKfovz-lzSXjU4DoIXGLQrUiG_CgoV1I7CgpFchuq7Q"

headers = {
    "X-Browser-Use-API-Key": API_KEY
}

# 查询任务状态
print("Checking task status...")
response = requests.get(f"{API_URL}/{TASK_ID}", headers=headers)

print(f"Status: {response.status_code}")
result = response.json()
print(f"\nResult:\n{result}")

# 如果有最终结果，打印出来
if result.get("status") == "success":
    print(f"\n最终结果: {result.get('result')}")
