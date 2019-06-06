import asyncio
import time


async def userInterface(message):
    await asyncio.sleep(1)
    print(message)

async def messageReciever(message):
    await asyncio.sleep(5)
    print(message)

async def detectLeader(message):
    await asyncio.sleep(10)
    print(message)

async def main():
    print(f"started at {time.strftime('%X')}")

    await asyncio.gather( 
        userInterface("Hello from thread 1"),
        messageReciever("Hello from thread 2"),
        detectLeader("Hello from thread 3"),
    )

    print(f"finished at {time.strftime('%X')}")

asyncio.run(main())
