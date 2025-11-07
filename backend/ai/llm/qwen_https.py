import aiohttp
import asyncio
import json

class QwenChat:
    def __init__(self, api_key, base_url):
        self.api_key = api_key
        self.base_url = base_url

    async def astream_async(self, content):
        """
        Asynchronous function to handle streaming response.
        """
        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "authorization": f"Bearer {self.api_key}"
        }

        payload = {
            "model": "deepseek-ai/DeepSeek-V2-Chat",
            "messages": [
                {
                    "role": "user",
                    "content": content
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

    async def ainvoke_async(self, content):
        """
        Asynchronous function to handle non-streaming response.
        """
        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "authorization": f"Bearer {self.api_key}"
        }

        payload = {
            "model": "deepseek-ai/DeepSeek-V2-Chat",
            "messages": [
                {
                    "role": "user",
                    "content": content
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
                        return data 
                    except json.JSONDecodeError:
                        pass
                else:
                    print("HTTP请求失败，状态码：" + str(response.status) + "，错误信息：" + await response.text())
        return None

if __name__ == "__main__":
    async def main():
        api_key = "sk-nmyyoncsmaagafmvjmbpyaxbeewtwqaiycitmhtomjzlwbsw"
        base_url = "https://api.siliconflow.cn/v1/chat/completions"
        qwen_chat = QwenChat(api_key, base_url)

        # Test non-streaming function
        result = await qwen_chat.ainvoke_async("你好")
        print(result)
        print("*" * 100)

        # Test streaming function
        async for content in qwen_chat.astream_async("你好"):
            print(content)

    asyncio.run(main())
