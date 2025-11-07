# -*- coding:utf-8 -*-
import os
import openai
import asyncio
import traceback
from openai.lib.azure import AzureOpenAI
from utils.logger import mylog
from openai import AsyncOpenAI

client = AsyncOpenAI(
    api_key="sk-ZFEd6Am3xCHJZB5BAd2bAa7c2fB749Eb86Ba807dC3D3D192",
    base_url='http://36.139.157.119:13000/v1'
)
class myChatGPT2:
    def __init__(self, **kwargs):
        self.base_url = "https://127.0.0.1:13000/v1"
        self.api_key = 'sk-ZFEd6Am3xCHJZB5BAd2bAa7c2fB749Eb86Ba807dC3D3D192'
        # self.model = "Qwen1.5-14B-Chat"
        self.model = "gpt-4o-eus2"
        self.temperature = kwargs.pop("temperature", 0.7)
        self.stream = kwargs.pop("stream", True)  # 设置为 True 以启用流式输出
        self.max_tokens = kwargs.pop("max_tokens", 800)
        self.top_p = kwargs.pop("top_p", 0.95)
        self.frequency_penalty = kwargs.pop("frequency_penalty", 0)
        self.presence_penalty = kwargs.pop("presence_penalty", 0)
        self.stop = kwargs.pop("stop", None)
        openai.api_key = self.api_key
        openai.api_base = self.base_url
        return

    def setmessage(self, message=[], **kwargs):
        if message != []:
            self.message = message
        else:
            self.message = [
                {"role": "system", "content": kwargs['system'] if 'system' in kwargs else ''},
                {"role": "user", "content": kwargs['user'] if 'user' in kwargs else ''},
            ]
        return

    async def chat2(self, message=[], **kwargs):
        self.setmessage(message=message, **kwargs)
        response = await openai.ChatCompletion.acreate(
            model=self.model,
            messages=self.message,
            temperature=self.temperature,
            stream=self.stream,
            max_tokens=self.max_tokens,
            top_p=self.top_p,
            frequency_penalty=self.frequency_penalty,
            presence_penalty=self.presence_penalty,
            stop=self.stop
        )
        try:
            async for chunk in response:
                if chunk['choices']:
                    yield chunk['choices'][0]['delta'].get('content', '')
        except Exception as e:
            mylog.error(f"Encountered error while generating summary: {str(e)}")
            return

    async def chat3(self, message=[], **kwargs):
        self.setmessage(message=message, **kwargs)
        response = await client.chat.completions.create(
            model=self.model,
            messages=self.message,
            temperature=self.temperature,
            stream=self.stream,
            max_tokens=self.max_tokens,
            top_p=self.top_p,
            frequency_penalty=self.frequency_penalty,
            presence_penalty=self.presence_penalty,
            stop=self.stop
        )
        try:
            async for chunk in response:
                if len(chunk.choices) > 0:
                    yield chunk.choices[0].delta.content or ""
        except Exception as e:
            print("出错啦")
            mylog.error(f"Encountered error while generating summary: {str(e)}")
            return

if __name__ == '__main__':
    async def main():
        gpt = myChatGPT2()
        result = gpt.chat3(user="《狂人日记》是鲁迅创作的一篇短篇小说，发表于1918年，是中国现代文学史上的一部重要作品，常被视为现代中国文学的开端。这部作品以日记的形式，记录了一个患有迫害妄想症的“狂人”——一个封建社会的受害者的心理活动及其对社会现实的控诉。主要内容概述如下： 引言：故事由一个叙述者的引言开始，叙述者从朋友那里得知某人因病休养，留下了一本日记。这个朋友将日记借给了叙述者，并允许他发表。 日记内容：- 初始疑虑：狂人在日记的最开始，描述了他的疑虑，认为周围的人都变得奇怪，总是用异样的眼神看他，并且他觉得这些人都在密谋着什么。 - 迫害妄想：狂人的惊恐逐渐加剧，他坚信邻居、医生，甚至自己的家人都在密谋“吃人”，他感到社会到处充满了这种可怕的阴谋。 - 历史反思：狂人翻阅古书，认为“吃人”并不是这个时代的新现象，而是自古以来的。书中的“仁义道德”在他看来只是一个掩盖真相的幌子，实际上是一个吃人的社会的记录和延续。- 自我怀疑和绝望：狂人开始怀疑自己是否也曾无意中“吃人”，他感到极度的内疚和恐慌，于是希望能够从这种可怕的现实中解脱出来。他渴望着有天能见到一片光明，希望未来能有“没有吃人的孩子”。 结局：狂人在极度的绝望中呼吁救救孩子，他希望下一代可以摆脱这个吃人的社会，并企盼未来的社会能够真正实现“人”的价值。《狂人日记》通过狂人的视角，猛烈抨击了封建礼教和传统文化的吃人本质，体现了鲁迅对封建制度的深刻批判和对社会变革的急切期盼。这篇小说的讽刺意味深远，对中国现代文学和文化产生了深远的影响。根据这篇文章生成文章大纲和相应模板")
        print(result)
        async for chunk in result:
            print(chunk, end='', flush=True)
    asyncio.run(main())