import asyncio
import time
import sys, select
import os

connect_port = input("Insira o PID do processo servidor: ")

################ USER INPUT HANDLERS ################

def verifyLeader():
    # Returns if the leader is alive
    print ('Consegui Rodar essa funcao')
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
        return sys.stdin.readline().strip()
    

async def userInterfaceThread():
    while True:
        await asyncio.sleep(0.1)
        if get_data() == 'leader':
            verifyLeader()

################ CONNECTION HANDLERS ################

## Sending

async def sendMessage(message, port):
    reader, writer = await asyncio.open_connection(
        '127.0.0.1', port)

    print(f'Send: {message!r}')
    writer.write(message.encode())

    data = await reader.read(100)
    print(f'Received: {data.decode()!r}')

    print('Close the connection')
    writer.close()


## Receiving

async def serverFunc(reader, writer):
    data = await reader.read(100)
    message = data.decode()
    addr = writer.get_extra_info('peername')

    print(f"Received {message!r} from {addr!r}")

    print(f"Send: {message!r}")
    writer.write(data)
    await writer.drain()

    print("Close the connection")
    writer.close()

async def messageHandlerThread(server):
    return await server.serve_forever()


################ RESPONSIBLE FOR RECEIVING MESSAGES ################


async def detectLeaderThread():
    while True:
        await asyncio.sleep(3)
        print("Detect Leader")



async def main():

    # Starts a server (in order to receive TCP messages) on the port of the PID (always unique)
    server = await asyncio.start_server(serverFunc, '127.0.0.1', os.getpid())
    
    addr = server.sockets[0].getsockname()
    print(f'Serving on {addr}')
    
    await asyncio.gather(
        userInterfaceThread(),
        sendMessage("Message", connect_port),
        messageHandlerThread(server),
        detectLeaderThread()
    )

asyncio.run(main())
