import asyncio
from pydantic import Field
from typing import Annotated

class ToolExceptionError(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


async def search_notes(query:Annotated[str,Field(description="检索参数")]) -> dict:
    """异步测试检索内容"""
    await asyncio.sleep(0.2)
    return {
        "file_name":"test_file.txt",
        "content": "这是一段测试内容"
    }

result = asyncio.run(search_notes("aa"))

async def fetch_page(url: Annotated[str,Field(description="网页地址")]) -> dict:
    """异步测试拉取网络数据"""
    await asyncio.sleep(1.2)

    if not url:
        raise ValueError("url格式错误")

    if "error" in url:
        raise ToolExceptionError(f"当前url错误： {url}")

    if "timeout" in url:
        raise asyncio.TimeoutError()

    return {
        "title": "text",
        "content": "demo content"
    }

async def draft_reply(content: str) -> str:
    """根据内容反馈结果"""
    try:
        await asyncio.sleep(2)
        return content
    except asyncio.CancelledError :
        return "已取消"