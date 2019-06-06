import asyncio
import time
import sys, select

def verifyLeader():
    print ('Consegui Rodar essa funcao')

def get_data():
    if select.select([sys.stdin], [], [], 0) == ([sys.stdin], [], []):
        name = sys.stdin.readline()
        name = name.strip()
        return name

async def userInterface(message):
    while True:
        await asyncio.sleep(0.1)
        if get_data() == 'leader':
            verifyLeader()
    return message

async def messageReciever(message):
    while True:
        await asyncio.sleep(3)
        print(message)
    return message

async def detectLeader(message):
    while True:
        await asyncio.sleep(3)
        print(message)
    return message

async def main():
    print(f"started at {time.strftime('%X')}")

    # #ui = userInterface("Hello from thread 1")
    # mr = messageReciever("Hello from thread 2")
    # dl = detectLeader("Hello from thread 3")
    # #await ui
    # await mr
    # await dl


    # await asyncio.wait([
    #     messageReciever("Hello from thread 2"),
    #     detectLeader("Hello from thread 3")]
    # )

    await asyncio.gather(
        userInterface("A"),
        messageReciever("a"),
        detectLeader("b")
    )

   

    print(f"finished at {time.strftime('%X')}")

asyncio.run(main())
