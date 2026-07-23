import pytest
import asyncio
from src.concurrent import run_all_tools
from src.tools import ToolExceptionError

@pytest.mark.asyncio
async def test_run_all_tools():
    result = await run_all_tools("a","b","c")

    assert len(result.keys()) is 3

@pytest.mark.asyncio
async def test_2_run_all_tools():
    result = await run_all_tools("a","timeout","c")
    
    assert "TimeoutError" in result["fetch_page"]


@pytest.mark.asyncio
async def test_3_run_all_tools():

    result = await run_all_tools("a","is error","c")
    
    assert "ToolExceptionError" in result["fetch_page"]


@pytest.mark.asyncio
async def test_4_run_all_tools():

    task = asyncio.create_task(run_all_tools("a","b","c"))

    task.cancel()

    with pytest.raises(asyncio.TimeoutError):
        await task

