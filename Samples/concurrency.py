import asyncio
import time
import sys, select

def verifyLeader():
    # Returns if the leader is alive
    return None

def emulateFailure():
    # Emulates a failure in the process
    return None

def recoverProcess():
    # Makes the process recover from the failure
    return None

def generateMetrics():
    # Prints to the console some useful information
    return None

def get_data():
    if select.select([sys.stdin], [], [], 0) == ([sys.stdin], [], []):
        return int(sys.stdin.readline())

async def userInterface(message):
    while True:
        await asyncio.sleep(0.1)
        
        if get_data() == 1:
            print("O Astolfo mandou oi")
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
