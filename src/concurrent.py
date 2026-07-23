import asyncio
from .tools import search_notes,fetch_page,draft_reply

async def run_all_tools(query: str, url: str, content: str) -> dict:

    async def timeout_draft():
        try:
            async with asyncio.timeout(3):
                return await draft_reply(content)
        except Exception as e:
            return f"捕获异常：{repr(e)}"

    async def execute_fetch_page():
        try:
            await fetch_page(url)
        except Exception as e:
            return f"捕获异常：{repr(e)}"

    results = await asyncio.gather(
        search_notes(query),
        execute_fetch_page(),
        timeout_draft()
    )

    return {
        "search_notes": results[0],
        "fetch_page": results[1],
        "draft_reply": results[2]
    }

    
