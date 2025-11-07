# -*- coding:utf-8 -*-
import os
import openai
import asyncio
import traceback

from logger import mylog


class myChatGPT:
    def __init__(self, **kwargs):

        openai.api_type = "azure"
        openai.api_base = "https://gmccai.openai.azure.com/"
        openai.api_version = "2024-02-15-preview"
        openai.api_key = 'fbb1e9cf2c9b41249c2e5dec7eb44f6e'#os.getenv("OPENAI_API_KEY")
        openai.proxy ={
            'no_proxy': None,
            'https': None,
            'http':None
        }

        self.engine = kwargs.pop("engine", 'gpt-4') #'gpt-4-32k' 'gpt-35-turbo-16k'
        self.temperature = kwargs.pop("temperature", 0.7)
        self.stream = kwargs.pop("stream", False) 
        self.max_tokens = kwargs.pop("max_tokens", 800) 
        self.top_p = kwargs.pop("top_p",0.95) 
        self.frequency_penalty = kwargs.pop("frequency_penalty", 0) 
        self.presence_penalty = kwargs.pop("presence_penalty", 0) 
        self.stop = kwargs.pop("stop", None) 
        return 
    
    def setmessage(self, message=[], **kwargs):
        if message !=[]:
            self.message = message
        else:
            self.message = [
                        {"role":"system","content": kwargs['system'] if 'system' in kwargs else ''},
                        {"role":"user","content": kwargs['user'] if 'user' in kwargs else ''},
                        ]
        return 

    def chat2(self, message=[], **kwargs):
        self.setmessage(message=message, **kwargs)  # 确保在调用 chat2 之前设置 message
        response = openai.ChatCompletion.create(
            engine=self.engine,
            messages=self.message,
            temperature=self.temperature,
            stream=self.stream,
            max_tokens=self.max_tokens,
            top_p=self.top_p,
            frequency_penalty=self.frequency_penalty,
            presence_penalty=self.presence_penalty,
            stop=self.stop)
        return response

    def chat(self, message=[], **kwargs):
        error = "Noerror"
        self.setmessage(message=message, **kwargs)
        try:
            response = openai.ChatCompletion.create(
            engine= self.engine,
            messages = self.message,
            temperature=self.temperature,
            stream=self.stream,
            max_tokens=self.max_tokens,
            top_p=self.top_p,
            frequency_penalty=self.frequency_penalty,
            presence_penalty=self.presence_penalty,
            stop = self.stop)
        
        except openai.error.APIError as e:
            # Handle API error here, e.g. retry or log
            mylog.info(f"OpenAI API returned an API Error: {e}")
            #error = "APIError"
            response ={'choices':[{"message":{"content":f"OpenAI API returned an API Error: {e}"}}]}
            #
            traceback.print_exc()
            mylog.info(traceback.format_exc())

        except openai.error.AuthenticationError as e:
            # Handle Authentication error here, e.g. invalid API key
            mylog.info(f"OpenAI API returned an Authentication Error: {e}")
            #error = "AuthenticationError"
            response ={'choices':[{"message":{"content":f"OpenAI API returned an API Error: {e}"}}]}
            #
            traceback.print_exc()
            mylog.info(traceback.format_exc())

        except openai.error.APIConnectionError as e:
            # Handle connection error here
            mylog.info(f"Failed to connect to OpenAI API: {e}")
            #error = "APIConnectionError"
            response ={'choices':[{"message":{"content":f"OpenAI API returned an API Error: {e}"}}]}
            #
            traceback.print_exc()
            mylog.info(traceback.format_exc())

        except openai.error.InvalidRequestError as e:
            # Handle connection error here
            mylog.info(f"Invalid Request Error: {e}")
            #error = "InvalidRequestError"
            response ={'choices':[{"message":{"content":f"OpenAI API returned an API Error: {e}"}}]}
            #
            traceback.print_exc()
            mylog.info(traceback.format_exc())

        except openai.error.RateLimitError as e:
            # Handle rate limit error
            mylog.info(f"OpenAI API request exceeded rate limit: {e}")
            #error = "RateLimitError"
            response ={'choices':[{"message":{"content":f"OpenAI API returned an API Error: {e}"}}]}
            #
            traceback.print_exc()
            mylog.info(traceback.format_exc())

        except openai.error.ServiceUnavailableError as e:
            # Handle Service Unavailable error
            mylog.info(f"Service Unavailable: {e}")
            #error = "ServiceUnavailableError"
            response ={'choices':[{"message":{"content":f"OpenAI API returned an API Error: {e}"}}]}
            #
            traceback.print_exc()
            mylog.info(traceback.format_exc())

        except openai.error.Timeout as e:
            # Handle request timeout
            mylog.info(f"Request timed out: {e}")
            #error = "Timeout"
            response ={'choices':[{"message":{"content":f"OpenAI API returned an API Error: {e}"}}]}
            #
            traceback.print_exc()
            mylog.info(traceback.format_exc())
                 
        except:
            # Handles all other exceptions
            mylog.info("An exception has occured.") 
            #error = "Unknow error"
            response = {'choices':[{"message":{"content":f"An unknow exception has occured."}}]}
            #
            traceback.print_exc()
            mylog.info(traceback.format_exc())             
        return response

    async def async_chat(self, message=[], **kwargs):
        self.setmessage(message=message, **kwargs)
        response = await openai.ChatCompletion.acreate(
        engine= self.engine,
        messages = self.message,
        temperature=self.temperature,
        max_tokens=self.max_tokens,
        top_p=self.top_p,
        frequency_penalty=self.frequency_penalty,
        presence_penalty=self.presence_penalty,
        stop = self.stop)
        #await asyncio.sleep(100)        
        return response

#gpt = myChatGPT(engine="gpt-4-32k")
