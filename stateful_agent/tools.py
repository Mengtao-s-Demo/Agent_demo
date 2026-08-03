from pydantic import BaseModel,Field
from datetime import datetime
from typing import Callable
from .models import AgentState,UserMessage,SystemMessage,Metadata,AgentError,ToolCallRecord,ToolMessage,AssistantMessage
from uuid import uuid4
from dataclasses import dataclass
from src.llm.client import do_chat

class TimeParam(BaseModel):
    pass

def get_current_time():
    """获取当前时间日期"""
    return datetime.now()

class WeatherParam(BaseModel):
    city: str = Field(description="城市名称")

def get_current_weather(city:str):
    """获取当前城市天气"""
    return f"{city} 狂风暴雨，正在下冰雹"

class Tool:
    def __init__(self,real_func:Callable,params:type[BaseModel]) -> None:
        self.name = real_func.__name__
        self.real_func = real_func
        self.params = params

    def generate_tool_schema(self):
        return {
            "type":'function',
            "function": {
                "name": self.name,
                "description":self.real_func.__doc__,
                "parameters": self.params.model_json_schema()
            }
        }

class ToolNotExitsError(Exception):
    pass

class ToolRegistry:
    def __init__(self,tools:list[Tool]) -> None:
        self.tools = tools

    def execute_tool(self,tool_name:str,params:str):
        exist_tool = next(
            (t for t in self.tools if t.name == tool_name),
            None
        )

        if exist_tool == None:
            raise ToolNotExitsError(f"tool name: {tool_name} 不存在")

        validate_params = exist_tool.params.model_validate_json(params)
        params_dict = validate_params.model_dump()
        tool_result = exist_tool.real_func(**params_dict)
        return str(tool_result)

@dataclass
class Agent:
    state:AgentState|None = None
    max_steps: int = 8

    def run(self,input:str,state_json:str|None = None):
        tool_registry = ToolRegistry([
            Tool(get_current_weather,WeatherParam),
            Tool(get_current_time,TimeParam)
        ])
        tool_schemas = [
            t.generate_tool_schema() for t in tool_registry.tools
        ]
        messages = [
            SystemMessage(role="system",content="你是一个Ai助手！"),
            UserMessage(role="user",content=input)
        ]

        # 初始化state
        if state_json == None:
            self.state = AgentState(
                session_id=str(uuid4()),
                user_id='tom',
                messages=messages,
                tool_calls=None,
                errors=None,
                artifacts=None,
                current_step='initializing',
                created_at=int(datetime.now().timestamp()),
                updated_at=int(datetime.now().timestamp()),
                version=1,
                metadata=Metadata(
                    trace_id=str(uuid4()),user_id="tom",max_tool_retried_time=3
                )
            )
        else:
            self.state = AgentState.load_json_state(state_json)

        current_step_count = 0

        while self.state.current_step != "completed" and self.state.current_step !="failed" and current_step_count < self.max_steps:
            print('================')
            print(self.state)
            self.state.current_step = "generating_response"
            current_step_count += 1

            try:
                response = do_chat(self.state.messages,tools=tool_schemas)
                print(f"response is : {response}")

                message = response.choices[0].message

                self.state.messages.append(AssistantMessage.convert_openai_message(message))

                tool_calls = message.tool_calls

                if tool_calls != None and len(tool_calls) > 0:
                    # 调用工具
                    self.state.current_step = "calling_tool"
                    self.state.tool_calls = []
                    for tool_call in tool_calls:
                        tool_call_result = ToolCallRecord(
                            id=tool_call.id,
                            arguments=tool_call.function.arguments,
                            name=tool_call.function.name,
                            status="pending",
                            error=None,
                            content=None,
                            tried_times=0
                        )
                        self.state.tool_calls.append(tool_call_result)
                        ## 执行任务
                        while True:
                            try:
                                tool_result = tool_registry.execute_tool(tool_call.function.name,
                                                        tool_call.function.arguments)
                                self.state.messages.append(
                                    ToolMessage(
                                        tool_call_id=tool_call.id,
                                        content=tool_result,
                                        role='tool'
                                    )
                                )
                                # 更新state
                                tool_call_result.content = tool_result
                                tool_call_result.status = "succeeded"
                                if tool_call_result.error != None:
                                    tool_call_result.error = None
                                break
                            except ToolNotExitsError as te:
                                ## 工具不存在，不用再执行了，直接跳出错误
                                tool_call_result.status = "failed"
                                tool_call_result.error = {
                                    "type":"ToolNotExitsError",
                                    "content":"工具不存在！"
                                }
                                ## 更新工具消息
                                self.state.messages.append(ToolMessage(
                                    tool_call_id = tool_call.id,
                                    content="工具不存在",
                                    role="tool"
                                ))
                                break
                            except Exception as e:
                                tool_call_result.tried_times += 1
                                tool_call_result.error = {
                                    "type": str(type(e)),
                                    "content": str(e)
                                }
                                if tool_call_result.tried_times > self.state.metadata.max_tool_retried_time:
                                    # 超过最大次数，升级 为state错误
                                    tool_call_result.status = "failed"
                                    self.state.current_step = "failed"
                                    self.state.errors = AgentError(type=str(type(e)),detail=f"调用工具:{tool_call.function.name},达到最大调用次数！")
                                    break
                    
                else:
                    self.state.current_step = "completed"
                    

            except Exception as e:
                self.state.current_step = "failed"
                self.state.errors = AgentError(
                    type=type(e).__name__,
                    detail=str(e)
                )

        print("[][][]][][][][][]")
        print(self.state)

agent = Agent()

agent.run("现在几点，今天武汉的天气是什么？")