import asyncio
import time
import sys, select
import os

programIDList = []





################ READ USER INPUT ################

def get_data():
    # Reads user input from stdin
    if select.select([sys.stdin], [], [], 0) == ([sys.stdin], [], []):
        return sys.stdin.readline().strip()

async def userInterfaceThread():
    # Responsible for calling for reading the user input and directing it to the current function
    while True:
        await asyncio.sleep(0.1)
        if get_data() == 'leader':
            verifyLeader()





################ USER INPUT FUNCTION ################

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





################ CONNECTION HANDLERS ################

# Functions to handle the listening of messages

async def serverFunc(reader, writer):
    # Creates a function in order to handle to handle messages from ther processes
    data = await reader.read(100)
    message = data.decode()

    # Splits the string into ints
    messageElements = [int(n) for n in message.split("|")]
    
    if (messageElements[0] == 6):
        message = await CONNECT_return(writer)
        programIDList.append(messageElements[1])
    else:
        writer.write(data)
        await writer.drain()

    writer.close()

async def messageHandlerThread(server):
    # Instructs the execution of the server 
    return await server.serve_forever()

# Sending messages

async def sendMessage(message, port):
    # Handles sending a message to another process (defined by it's uniqueID, which is equal to the port it resides)
    reader, writer = await asyncio.open_connection(
        '127.0.0.1', port)

    print(f'Send: {message!r}')
    writer.write(message.encode())

    data = await reader.read(100)
    print(f'Received: {data.decode()!r}')

    print('Close the connection')
    writer.close()

    return data.decode()




################ MESSAGE RESPONSE ACTIONS ##################

async def ELEICAOreturn():
    return

async def OK_Return():
    return

async def LIDER_Return():
    return

async def VIVO_return():
    return

async def VIVO_OK_return():
    return

async def CONNECT_return(writer):
    global programIDList
    
    message = ""
    for element in programIDList:
        message = message + str(element) + "|"
    message = message[:-1]

    writer.write(message.encode())
    await writer.drain()
    
    return message

################ RESPONSIBLE FOR RECEIVING MESSAGES ################

async def detectLeaderThread():

    print(programIDList)
    while True:
        await asyncio.sleep(3)
        #print("Detect Leader")





################ MAIN FUNCTION ################

async def main():
    global programIDList

    ################# MESSAGE TABLE
    ########## 1. ELEIÇÃO
    ########## 2. OK
    ########## 3. LIDER
    ########## 4. VIVO
    ########## 5. VIVO_OK
    ########## 6. CONNECT (requisição para entrar na rede)


    # We use the process' PID as a unique identifier in multiple occastions on the program.
    # This means that all of the identifier, port, and value of election is equal to the ID.

    uniqueID = os.getpid()
    programIDList.append(uniqueID)
    isConnected = False
    

    while (isConnected == False):
        connect_port = int(input("Insira o ID de um processo existente para se conectar (-1 para se conectar a ninguém): "))
        try:
            if (connect_port != -1):
                message = await sendMessage(f"6|{uniqueID}", connect_port)
                messageList = [int(n) for n in message.split("|")]
                programIDList.extend(messageList)
                isConnected = True
            else:
                isConnected = True
        except ConnectionError:
            print("Erro de conexão, tente novamente")
    
    if (connect_port != -1):
        programIDList.append(connect_port)

    # Starts a server (in order to receive TCP messages) on the port of the PID (always unique)
    server = await asyncio.start_server(serverFunc, '127.0.0.1', uniqueID)
    
    print(f'Seu ID é {uniqueID}')
    
    await asyncio.gather(
        userInterfaceThread(),
        #sendMessage("Message", connect_port),
        messageHandlerThread(server),
        detectLeaderThread()
    )

asyncio.run(main())
