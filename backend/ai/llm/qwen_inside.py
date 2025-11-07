import os
import json
import requests
import unittest
from unittest.mock import patch
import asyncio
import aiohttp

class InsideQwenChat:
    def __init__(self, api_key, base_url, model):
        self.api_key = api_key
        self.base_url = base_url
        self.model = model

    async def inside_astream_async(self, text):
        """
        Generates a summary based on the prompt and context using streaming (asynchronous).
        """
        headers = {
            "accept": "application/json",
            "authorization": f"Bearer {self.api_key}",
            "content-type": "application/json"
        }

        payload = {
            "model": "deepseek-ai/DeepSeek-V2-Chat",
            "messages": [
                {
                    "role": "user",
                    "content": text
                }
            ],
            "stream": True,
            "max_tokens": 512,
            "temperature": 0.7,
            "top_p": 0.7,
            "top_k": 50,
            "frequency_penalty": 0.5,
            "n": 1
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(self.base_url, headers=headers, json=payload) as response:
                if response.status == 200:
                    async for line in response.content:
                        decoded_line = line.decode('utf-8').replace("data: ", "")
                        try:
                            data = json.loads(decoded_line)
                            if 'choices' in data and len(data['choices']) > 0 and 'delta' in data['choices'][0] and 'content' in data['choices'][0]['delta']:
                                yield data['choices'][0]['delta']['content']
                        except json.JSONDecodeError:
                            pass
                else:
                    print("HTTP请求失败，状态码：" + str(response.status) + "，错误信息：" + await response.text())

    async def inside_ainvoke_async(self, text):
        """
        Generates a summary based on the prompt and context without streaming (asynchronous).
        """
        headers = {
            "accept": "application/json",
            "authorization": f"Bearer {self.api_key}",
            "content-type": "application/json"
        }

        payload = {
            "model": "deepseek-ai/DeepSeek-V2-Chat",
            "messages": [
                {
                    "role": "user",
                    "content": text
                }
            ],
            "stream": False,
            "max_tokens": 512,
            "temperature": 0.7,
            "top_p": 0.7,
            "top_k": 50,
            "frequency_penalty": 0.5,
            "n": 1
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(self.base_url, headers=headers, json=payload) as response:
                if response.status == 200:
                    try:
                        data = await response.json()
                        if 'choices' in data and len(data['choices']) > 0 and 'delta' in data['choices'][0] and 'content' in data['choices'][0]['delta']:
                            return data
                    except json.JSONDecodeError:
                        pass
                else:
                    print("HTTP请求失败，状态码：" + str(response.status) + "，错误信息：" + await response.text())
        return None

class TestQwenInside(unittest.TestCase):
    def setUp(self):
        self.qwen = InsideQwenChat(api_key="sk-nmyyoncsmaagafmvjmbpyaxbeewtwqaiycitmhtomjzlwbsw", base_url="https://api.siliconflow.cn/v1/chat/completions", model="Qwen/Qwen2.5-14B-Instruct")
    
    @patch('requests.post')
    def test_inside_ainvoke_success(self, mock_post):
        # Mock the response from requests
        mock_response = unittest.mock.Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"choices": [{"delta": {"content": "测试内容"}}]}
        mock_post.return_value = mock_response

        result = self.qwen.inside_ainvoke("测试文本")
        self.assertEqual(result, {"choices": [{"delta": {"content": "测试内容"}}]})

    @patch('requests.post')
    def test_inside_ainvoke_failure(self, mock_post):
        # Mock the response from requests
        mock_response = unittest.mock.Mock()
        mock_response.status_code = 400
        mock_response.text = "错误信息"
        mock_post.return_value = mock_response

        result = self.qwen.inside_ainvoke("测试文本")
        self.assertIsNone(result)

if __name__ == "__main__":
    import asyncio

    async def main():
        llm = InsideQwenChat(api_key="sk-nmyyoncsmaagafmvjmbpyaxbeewtwqaiycitmhtomjzlwbsw", base_url="https://api.siliconflow.cn/v1/chat/completions", model="Qwen/Qwen2.5-14B-Instruct")
        result = await llm.inside_ainvoke_async("你好")
        print(result)

    asyncio.run(main())