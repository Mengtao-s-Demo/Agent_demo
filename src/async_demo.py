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