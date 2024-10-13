import aiohttp
import asyncio
import time

class AsyncNetworkUtils:
    """异步网络请求处理类，支持重试机制"""

    @staticmethod
    async def post_request(url, headers, data, retries=3, timeout=10):
        """发送异步 POST 请求，并自动重试"""
        for attempt in range(retries):
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.post(url, headers=headers, json=data, timeout=timeout) as response:
                        response.raise_for_status()  # 如果状态码不是200，抛出异常
                        return await response.json()
            except aiohttp.ClientError as e:
                if attempt < retries - 1:
                    await asyncio.sleep(2 ** attempt)  # 指数退避，重试机制
                    continue
                else:
                    raise e  # 如果重试次数用完，抛出异常

# 测试异步网络请求
async def test_async_request():
    url = "http://localhost/v1/chat-messages"
    headers = {"Authorization": "Bearer your_api_key", "Content-Type": "application/json"}
    data = {"query": "Hello", "response_mode": "blocking", "user": "abc-123"}

    try:
        response = await AsyncNetworkUtils.post_request(url, headers, data)
        print(response)  # 打印响应
    except Exception as e:
        print(f"请求失败：{e}")

# 运行异步测试
if __name__ == "__main__":
    asyncio.run(test_async_request())
