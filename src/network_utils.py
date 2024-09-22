import requests
import time

class NetworkUtils:
    """网络请求处理类，包含重试机制和错误处理"""

    @staticmethod
    def post_request(url, headers, data, retries=3, timeout=10):
        """发送 POST 请求，并自动重试"""
        for attempt in range(retries):
            try:
                response = requests.post(url, headers=headers, json=data, timeout=timeout)
                response.raise_for_status()  # 如果状态码不是200，抛出异常
                return response
            except requests.exceptions.RequestException as e:
                if attempt < retries - 1:
                    time.sleep(2 ** attempt)  # 指数退避，重试机制
                    continue
                else:
                    raise e  # 如果重试次数用完，抛出异常

# 测试网络请求
if __name__ == "__main__":
    url = "http://localhost/v1/chat-messages"
    headers = {"Authorization": "Bearer your_api_key", "Content-Type": "application/json"}
    data = {"query": "Hello", "response_mode": "blocking", "user": "abc-123"}

    try:
        response = NetworkUtils.post_request(url, headers, data)
        print(response.json())  # 打印响应
    except Exception as e:
        print(f"请求失败：{e}")
