import asyncio

async def download(name:str,seconds:int):
    print(f"开始下载: {name}")

    await asyncio.sleep(seconds)

    print(f"{name}下载完毕")

    return f"{name}下载完毕"


async def main():
    results = await asyncio.gather(
        download("A",10),
        download("B",5)
    )

    print(results)

asyncio.run(main())

async def main2():
    try:
        async with asyncio.TaskGroup() as tg:
            tg.create_task(download("C",2))
            tg.create_task(download("D",1))
    except* ValueError as group:
        for exc in group.exceptions:
            print(f"捕获：{exc}")

asyncio.run(main2())