## 定义 `ToolRegistry`：管理可用的工具，每个工具需包含名称、描述、参数 schema
# （用 Pydantic BaseModel 或 dict）、实际执行函数。
# 工具示例：`get_time`（返回当前时间文本）、`add_numbers`（校验 a 和 b 为整数并返回和），
# 故意设计一个可能失败的工具 `trouble_tool` （参数小于 0 时抛异常）。

from pydantic import BaseModel,Field
from typing import Callable,Type
import json
from datetime import datetime
import uuid
import random

class ToolRegistry:
    def __init__(self,tools: list[Tool] = []):
        self.tools = tools
        self.full_tools = [
            self.__handle_tool__(t)
            for t in tools
        ] 

    def __handle_tool__(self,tool:Tool) -> str:
        """处理工具"""
        tool_schema = {
            "type": "function",
            "function": {
                "name": tool.func.__name__,
                "description":tool.func.__doc__,
                "properties": tool.args_schema.model_json_schema()
            }
        }
        return json.dumps(tool_schema,ensure_ascii=False)


    def registry_tool(self,tool: Tool):
        self.full_tools.append(
            self.__handle_tool__(tool)
        )

    def execute_tool(self,tool_name: str,**kwargs):
        """根据工具名称执行工具"""
        print(f"开始执行工具：{tool_name}")
        tool = next(
            (t for t in self.tools if t.func.__name__ == tool_name),
            None
        )
        if not tool:
            raise ValueError(f"未找到工具：{tool_name}")
        return tool.invoke_tool(**kwargs)

class Tool:
    def __init__(self,func: Callable, args_schema: Type[BaseModel]):
        self.func = func
        self.args_schema = args_schema

    def invoke_tool(self,**kwargs):

        # dict -> BaseModel
        # 此步骤为了校验参数是否正确
        params = self.args_schema(**kwargs)

        try:
            return self.func(**params.model_dump())
        except Exception as e:
            print(f"执行tool{self.func.__name__}失败，错误原因：{e}")
            return f"执行tool {self.func.__name__}失败，错误原因：{e}"


class CityParam(BaseModel):
    city: str = Field(description="城市名称")

def get_city(city: str):
    """获取城市名称"""
    return f" city is: {city} "

class EmailsParam(BaseModel):
    emails: list[str] = Field(description="收件人列表")
    title: str = Field(description="收件人邮件标题")

def do_send_email(emails:list[str],title:str):
    """发送邮件列表"""
    return ",\n".join(
        [e for e in emails]
    )

class GetTImeParam(BaseModel):
    pass

def get_time():
    """返回当前时间"""
    return datetime.now()

class AddNumbersParam(BaseModel):
    a: int = Field(description="整数a")
    b: int = Field(description="整数b")

def add_numbers(a:int,b:int) -> int:
    """获取两个整数之和"""
    return a+b

class TroubleToolParam(BaseModel):
    n: float = Field(description="一个数字")

def trouble_tool(n:float):
    """返回大于0的输入参数"""
    if n < 0 :
        raise ValueError(f"参数不能小于0")
    return n

tools = [
    Tool(get_city,CityParam),
    Tool(do_send_email,EmailsParam),
    Tool(get_time,GetTImeParam),
    Tool(add_numbers,AddNumbersParam),
    Tool(trouble_tool,TroubleToolParam)
]

## 注册工具
tool_registry = ToolRegistry(tools)

# 实现 `mock_model()` 函数：
# 接收当前对话上下文（列表），模拟模型决策。
# 使用简单规则：
# 如果上下文中不含工具结果，返回调用 `get_time` 的指令；
# 如果已有工具结果，则返回最终回答；
# 随机引入一次对未知工具 `non_exist_tool` 的调用；
# 随机引入一次对 `add_numbers` 的参数错误（传入字符串）。

def mock_model(messages: list[dict]):
    if not messages or len(messages) == 0:
        return {
            "role":"assistant",
            "content":"需要调用get_time，获取当前时间",
            "tool_calls":[
                {"id": f"call:{uuid.uuid4()}","type":"function","arguments":'{}',"name":"get_time"}
            ]
        }
    tool_result = next(
        (t for t in messages if "tool_call_id" in t),
        None
    )
    if tool_result:
        return {
            "role":"assistant",
            "content": f"根据调用工具的结果，最终答案是：{tool_result['content']}"
        }
    else :
        # 随机引入一次工具调用
        choice = random.choice([1,2,3])
        if choice == 1:
            return {
                "role":"assistant",
                "content":"一次工具调用",
                "tool_calls":[
                    {"id":f"call:{uuid.uuid4()}","type":"function","arguments":'{}',"name":"non_exist_tool"}
                ]
            }
        elif choice == 2:
        # 错误的参数
            return {
                "role":"assistant",
                "content":"一次工具调用",
                "tool_calls":[
                    {"id":f"call:{uuid.uuid4()}","type":"function","arguments":'{"a":"1","b":"2"}',"name":"add_numbers"}
                ]
            }
        else:
            return {
                "role":"assistant",
                "content":"需要调用get_time，获取当前时间",
                "tool_calls":[
                    {"id": f"call:{uuid.uuid4()}","type":"function","arguments":'{}',"name":"get_time"}
                ]
            }

def run_agent_loop():
    history = [
        {"role":"user","content":"现在几点？"}
    ]
    max_count = 5
    now_count = 0
    while now_count <= 5:
        print("开始循环")
        response = mock_model(history)

        print(f"========={now_count}=======")
        print(response)

        ## 判断是否有工具调用
        tool_calls = response.get("tool_calls")
        if tool_calls is not None:
            for t in tool_calls:
                print(f"调用工具：{t["name"]}，工具参数：{t["arguments"]}")
                try:
                    tool_result = tool_registry.execute_tool(t["name"],json.loads(t["arguments"]))
                    print(f"调用工具：{t["name"]},工具结果：{tool_result}")
                    history.append(
                        {"role":"tool","tool_call_id":t["id"],"content":tool_result}
                    )
                except ValueError as e:
                    history.append(
                        {"role":"tool","tool_call_id":t["id"],"content":f"调用工具报错：{e}"}
                    )
                

        else:
            print(f"最终答案：{response}")
            return response

        
        now_count += 1

    # 超过最大次数，直接最终回答
    # history.append(
    #     {"role":"assistant","content":"已经达到最大步骤：5，强制停止循环，根据以上信息，请作出最终回答"}
    # )
    # final_response = mock_model(history)
    final_response = "当前已经到达最大步骤，结束循环"
    print(f"============final response===============")
    print(final_response)
    return final_response

if __name__ == "__main__":
    run_agent_loop()
                
