import asyncio
import time


async def thread1(message):
    await asyncio.sleep(1)
    print(message)

async def thread2(message):
    await asyncio.sleep(5)
    print(message)

async def thread3(message):
    await asyncio.sleep(10)
    print(message)

async def main():
    print(f"started at {time.strftime('%X')}")

    await asyncio.gather( 
        thread1("Hello from thread 1"),
        thread2("Hello from thread 2"),
        thread3("Hello from thread 3"),
    )

    print(f"finished at {time.strftime('%X')}")

asyncio.run(main())
