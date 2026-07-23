import asyncio

timeout = 10

async def download(name:str,download_time:int = 5):
    global timeout
    print(f"开始下载：{name}")

    if name == 'text_error':
        raise FileExistsError(f"文件不存在: {name}")

    try:
        async with asyncio.timeout(timeout):
            await asyncio.sleep(download_time) # await阻塞当前协程，交给asyncio.sleep这个协程
            print(f"下载成功： {name}")
    except TimeoutError as e:
        print(f"执行任务超时，下载：{name}失败")
        return f"下载 : {name}, 失败！"


async def main():

    await asyncio.gather(
    download("A"), ## 正常下载
    download("B", 11), ## 超时
    download("text_error") ## 抛出异常
    )

asyncio.run(main()) # 生成一个事件循环