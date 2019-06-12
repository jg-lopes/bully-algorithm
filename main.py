import asyncio
import time
import sys, select
import os

os.system("clear")

programIDList = []

# Bool in order to check if connected to the network
isConnected = False

# If process is not active, it DOES NOT returns messages
active = True

# We use the process' PID as a unique identifier in multiple occastions on the program.
# This means that all of the identifier, port, and value of election is equal to the ID.
uniqueID = os.getpid()

# Starts with an unknown leader 
# Discovers it in connection protocol
# If is the initial node on the network (when it connects to -1), declares itself as leader
leaderID = -1





################ READ USER INPUT ################

def get_data():
    # Reads user input from stdin
    if select.select([sys.stdin], [], [], 0) == ([sys.stdin], [], []):
        return sys.stdin.readline().strip()

async def userInterfaceThread():
    # Responsible for calling for reading the user input and directing it to the current function
    while True:
        await asyncio.sleep(0.1)

        userInput = get_data()

        if userInput == 'leader':
            verifyLeader()
        if userInput == 'fail':
            emulateFailure()
        if userInput == 'recover':
            await recoverProcess()





################ USER INPUT FUNCTION ################

def verifyLeader():
    # Returns if the leader is alive
    print("ouvi leader")
    return None

def emulateFailure():
    global active

    # Emulates a failure in the process
    active = False

    print("O processo parou de funcionar")
    return None

async def recoverProcess():
    global active

    # Makes the process recover from the failure
    active = True
    print("Iniciada uma eleição devido à recuperação de um processo")
    await election()

    print("O processo se recuperou da falha")
    return None

def generateMetrics():
    # Prints to the console some useful information
    return None





################ CONNECTION HANDLERS ################

# Connects the process to the network

async def connectNetwork():
    global isConnected, programIDList, leaderID

    while (isConnected == False):
        connect_port = int(input("Insira o ID de um processo existente para se conectar (-1 para se conectar a ninguém): "))
        try:
            if (connect_port != -1):
                returnedMessage = await exchangeMessages(f"6|{uniqueID}", connect_port)
                
                # Recebe uma mensagem do tipo 7|LIDERID|PROCESSO1|PROCESSO2|PROCESSO3....
                messageElements = [int(n) for n in returnedMessage.split("|")]
                leaderID = messageElements[1]
                programIDList.extend(messageElements[2:])
                isConnected = True
            else:
                leaderID = uniqueID
                isConnected = True
        except ConnectionError:
            print("Erro de conexão, tente novamente")


    # Communicates to all process that it is connecting to the network
    for program in programIDList:
        if program != uniqueID:
            await exchangeMessages(f"8|{uniqueID}", program)

    

# Functions to handle the listening of messages

async def serverFunc(reader, writer):
    global active, leaderID, programIDList

    # Creates a function in order to handle to handle messages from ther processes
    data = await reader.read(100)
    message = data.decode()

    # Splits the string into ints
    messageElements = [int(n) for n in message.split("|")]
    
    # Only answers messages when active
    if (active):
        
        # Answering ELEICAO
        if (messageElements[0] == 1):

            electionCallerID = messageElements[1]
            
            if electionCallerID < uniqueID:
                message = "2"

                writer.write(message.encode())
                await writer.drain()

                print(f"Començando eleição por receber um OK")
                await election()

        # Answering OK unecessary

        # Answering LEADER
        elif (messageElements[0] == 3):
            leaderID = messageElements[1]

        # Answering VIVO
        elif (messageElements[0] == 4):
            # Returns a VIVO_OK
            message = "5"

            writer.write(message.encode())
            await writer.drain()

        # Answering VIVO_OK unecessary

        # Answering CONNECT 
        elif (messageElements[0] == 6):
            global programIDList
    
            # Second element of the return message is the leader ID
            message = "7|" + str(leaderID) + "|"

            # Other elements are all the existing IDs in the network (including the leader)
            for element in programIDList:
                message = message + str(element) + "|"
            message = message[:-1]

            writer.write(message.encode())
            await writer.drain()

        # Answering CONNECTION_REQUEST already handled by connectNetwork function

        # Answering CONNECT
        elif (messageElements[0] == 8):
            programIDList.append(messageElements[1])

        else:
            writer.write(data)
            await writer.drain()

    writer.close()

async def messageHandlerThread(server):
    # Instructs the execution of the server 
    return await server.serve_forever()

# Sending messages

async def exchangeMessages(message, port):
    # Handles sending a message to another process (defined by it's uniqueID, which is equal to the port it resides)
    # Recieves a response (if available)
    reader, writer = await asyncio.open_connection(
        '127.0.0.1', port)

    #print(f'Send: {message!r}')
    writer.write(message.encode())

    data = await reader.read(100)
    #print(f'Received: {data.decode()!r}')

    #print('\n\n')
    writer.close()

    return data.decode()





################ RESPONSIBLE FOR RECEIVING MESSAGES ################

async def detectLeaderThread():
    global leaderID, programIDList

    

    while True:
        # Asks if leader is alive -> VIVO

        # Checks if the process already recognizes a leader
        await asyncio.sleep(5)
        
        print(leaderID)
        if (leaderID != -1) and active:
            result = await exchangeMessages("4", leaderID)
            
            if (result == ""):
                print(f"Començando eleição por ver lider em falha")
                await election()





################ ELECTION PROTOCOL ################

async def election():
    global programIDList, uniqueID, leaderID

    possibleLeader = True

    for program in programIDList:
        if program != uniqueID:  
            # Sends ELEICAO to all processes in the network
            #print(f"Enviando ELEICAO para {program}")
            returnMessage = await exchangeMessages(f"1|{uniqueID}", program)

            # If receives an OK, knows there is a bigger ID than itself, and thus cannot become the leader
            if returnMessage == "2":
                possibleLeader = False            
    
    # Has sent to all processes and found no process with a bigger ID
    if possibleLeader == True:
        leaderID = uniqueID
        for program in programIDList:
            if program != uniqueID:
                # Envia que é o líder a todos os processos

                #print(f"Enviando LIDER para {program}")
                leaderID = uniqueID
                await exchangeMessages(f"3|{uniqueID}", program)
                


        
        



################ MAIN FUNCTION ################

async def main():
    global programIDList, uniqueID

    ################# MESSAGE TABLE
    ########## 1. ELEIÇÃO
    ########## 2. OK
    ########## 3. LIDER
    ########## 4. VIVO
    ########## 5. VIVO_OK
    ########## 6. CONNECTION_REQUEST (request for program list, in order to discover the network)
    ########## 7. PROGRAM_LIST (returns informations necessary for connection, current leader followed by all processes (incluind leader))
    ########## 8. CONNECT (enters the network, comunicating to all processes' it's ID)

    # Inserts the current program unique ID in the program ID list
    programIDList.append(uniqueID)
   
    # Uses the user input in order to locate a existing process in the network in order to connect to the whole network
    await connectNetwork()
 
    # Starts a server (in order to receive TCP messages) on the port of the PID (always unique)
    server = await asyncio.start_server(serverFunc, '127.0.0.1', uniqueID)

    print(f'Conectado na rede! Seu ID é {uniqueID}')
    
    await asyncio.gather(
        userInterfaceThread(),
        messageHandlerThread(server),
        detectLeaderThread()
    )

# Executes the main in asynchronous fashion (allows the creation of the threads)
asyncio.run(main())
