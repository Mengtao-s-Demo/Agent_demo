from datetime import datetime
from src.llm.client import client,OPENAI_MODEL_NAME
import json


def get_current_time():
    """获取当前时间"""
    return datetime.now()


def get_weather(city:str):
    """获取当前city天气"""
    return f"{city} is sunny"

## 定义tool schema

tools = [
    {
        "type":"function",
        "function": {
            "name":"get_current_time",
            "description":"获取当前时间",
            "parameters": {
                "type":"object",
                "properties":{}
            },
        }
    },
    {
        "type":"function",
        "function": {
             "name":"get_weather",
            "description":"获取当前city的天气",
            "parameters": {
                "type":"object",
                "properties":{
                    "city":{
                        "type":"string",
                        "description":"城市名称"
                    },
                },
                "required":["city"]
            }
        }
    }
]

def do_chat(input:str):
    """进行单词对话调用
    param:
    input : 用户输入
    """
    max_count = 6 # 最大LLM请求次数
    now_count = 0 # 当前LLM请求次数
    global tools

    messages_list = [
        {"role":"system","content":"你是一个智能助手，帮助用户解决问题！"},
        {"role":"user","content":input}
    ]

    while now_count < max_count:
        now_count += 1
        response = client.chat.completions.create(
            model=OPENAI_MODEL_NAME,
            messages=messages_list,
            tools=tools
        )
        print(f"==============={now_count}====================")
        print(response)
        messages_list.append(response.choices[0].message)
        # 判断是否工具调用
        if response.choices[0].message.tool_calls :
            tool_calls = response.choices[0].message.tool_calls
            for item in tool_calls:
                print(f"call_id: {item.id}")
                function = item.function
                print(f"tool_name : {function.name}")
                # 判断是否在工具list中
                real_func = next((t for t in tools if t['function']['name'] == function.name),None)
                if not real_func:
                    messages_list.append(
                        {"role":"assistant","content":f"工具不合法，{function.name}不在可用工具列表中！"}
                    )
                else:
                    # 执行工具
                    params = function.arguments
                    print(f"工具参数为：{params}")
                    try:
                        params = json.loads(params)
                        # 手工选择任务了
                        if function.name == 'get_weather':
                            result = get_weather(*params)
                        elif function.name == 'get_current_time':
                            result = get_current_time(*params)
                        messages_list.append(
                            {"role":"tool","tool_call_id":item.id,"content":str(result)}
                        )
                    except Exception as e:
                        print(f"调用工具{function.name}失败,错误原因为：{e}")
                        messages_list.append(
                            {"role":"assistant","content":f"调用工具{function.name}失败,错误原因为：{e}"}
                        )
        else:
            print(messages_list)
            return response

    # 最终总结
    messages_list.append(
        {"role":"assistant","content":"当前轮数已经达到最大次数了，直接总结回复用户的问题！"}
    )
    print(messages_list)
    response = client.chat.completions.create(
            model=OPENAI_MODEL_NAME,
            messages=messages_list
    )

    return response

        
response = do_chat("现在时间是多少，纽约市的天气如何？")

print(f"==========final=========")
print(response)
    

## 结果
## ChatCompletion(id='e2d4284f-6a07-46b6-ad73-5ded2ab583ca', 
#  choices=[Choice(finish_reason='tool_calls', index=0, logprobs=None,
#  message=ChatCompletionMessage(content='', refusal=None, role='assistant', 
#  annotations=None, audio=None, 
#  function_call=None, 
#  tool_calls=[ChatCompletionMessageFunctionToolCall(id='call_00_36qHARVqy4mkG13E7VuJ9123', 
#  function=Function(arguments='{"city": "纽约"}', name='get_weather'), type='function',
#  index=0)], reasoning_content='用户想知道纽约市的天气。
# 让我调用get_weather工具来获取纽约市的天气信息。'))], 
# created=1784904511, model='deepseek-v4-flash', object='chat.completion', 
# moderation=None, service_tier=None, 
# usage=CompletionUsage(completion_tokens=64, prompt_tokens=315, 
# total_tokens=379, 
# completion_tokens_details=CompletionTokensDetails(accepted_prediction_tokens=None,
# audio_tokens=None, reasoning_tokens=19, rejected_prediction_tokens=None), 
# prompt_tokens_details=PromptTokensDetails(audio_tokens=None, 
# cache_write_tokens=None, cached_tokens=256),
#  prompt_cache_hit_tokens=256, prompt_cache_miss_tokens=59))