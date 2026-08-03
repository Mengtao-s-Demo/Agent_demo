from pydantic import BaseModel,model_validator,Field
from typing import Literal,Annotated
from uuid import uuid4
from datetime import datetime

class Message(BaseModel):
    content:str

class SystemMessage(Message):
    role:Literal["system"]="system"

class UserMessage(Message):
    role:Literal["user"] = "user"

class FunctionCall(BaseModel):
    name:str
    arguments:str

class ToolCall(BaseModel):
    id:str
    type: Literal["function"] = 'function'
    function: FunctionCall

class AssistantMessage(Message):
    role : Literal["assistant"] = "assistant"
    tool_calls: list[ToolCall] | None

    @classmethod
    def convert_openai_message(cls,openai_message) -> AssistantMessage:
        """转换openai的message格式"""
        tool_call = openai_message.tool_calls
        if tool_call == None:
            return AssistantMessage(
                role="assistant",content=openai_message.content,tool_calls=None
            )
        else:
            return AssistantMessage(
                role="assistant",content="",
                tool_calls = [
                    ToolCall(id=t.id,type="function",function=FunctionCall(name=t.function.name,arguments=t.function.arguments))
                    for t in tool_call
                ]
            )

class ToolMessage(Message):
    role:Literal["tool"] = "tool"
    tool_call_id:str

class AgentError(BaseModel):
    type: str
    detail: str

class ToolCallRecord(BaseModel):
    id:str
    name:str
    arguments: str
    status: Literal["pending","succeeded","failed"]
    error: dict | None
    content: str | None
    tried_times: int = 0

    @model_validator(mode='after')
    def check_status(self):
        # 如果status='succeeded'的话，content不为空，且error为None
        if self.status == 'succeeded' and self.error != None:
            raise ValueError('当status为succeeded的时候，error不为None！')
        elif self.status == 'pending':
            if self.error != None or self.content != None:
                raise ValueError("当前状态为：pending，error和content不为空！")
        elif self.status == 'failed':
            if self.error == None or self.content != None:
                raise ValueError('当前状态为faile，工具的error为空，或者content不为空！')

        return self

class Artifact(BaseModel):
    id:str
    type: Literal["img","document","other"]
    path: str
    version: int

class Metadata(BaseModel):
    trace_id:str
    user_id:str
    max_tool_retried_time: int = 3

type MessageType = Annotated[
    SystemMessage |
    UserMessage |
    AssistantMessage |
    ToolMessage,
    Field(discriminator="role")
]

class AgentState(BaseModel):
    session_id:str
    user_id:str
    messages: list[MessageType]
    tool_calls: list[ToolCallRecord] | None
    errors: AgentError | None
    artifacts: list[Artifact] | None
    current_step: Literal["initializing",
                          "calling_tool","generating_response",
                          "completed","failed"]
    created_at: int
    updated_at: int
    version: int
    metadata: Metadata

    @classmethod
    def load_json_state(cls,json_state:str) -> AgentState:
        try:
            state = cls.model_validate_json(json_state)
            if state.version != 1:
                raise ValueError("模型版本错误！")
            return state
        except Exception as e:
            raise ValueError("加载模型错误")

    def update_state(self):
        pass

# 创建ToolCallRecord
succeeded_tool_record = ToolCallRecord(
    id="1",
    arguments='{}',
    name="get_time",
    status="succeeded",
    content="12:07",
    error=None
)

failed_tool_record = ToolCallRecord(
    id="2",
    arguments='{}',
    name="get_time",
    status="failed",
    error={type:"ValueError","content":"错误"},
    content=None
)

# 错误的示例
# pending_tool_record_error = ToolCallRecord(
#     id="3",
#     arguments={},
#     name="get_time",
#     status="pending",
#     error=None,
#     content="12:08"
# )

real_agent_state = AgentState(
    session_id=str(uuid4()),
    user_id="tml",
    messages=[
        SystemMessage(role="system",content="你是一个Ai助手"),
        UserMessage(content="你好，请问现在几点？")
    ],
    tool_calls=[succeeded_tool_record,failed_tool_record],
    errors=None,
    artifacts=None,
    current_step="initializing",
    created_at=int(datetime.now().timestamp()),
    updated_at=int(datetime.now().timestamp()),
    version=1,
    metadata= Metadata(
        user_id='tml',
        trace_id=str(uuid4())
    )
)

# real_json = real_agent_state.model_dump_json()
# print(real_json)

# l_agent = AgentState.load_json_state(json_state=real_json)
