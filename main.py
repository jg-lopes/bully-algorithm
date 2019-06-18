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


sentMessages = [0,0,0,0,0,0,0,0,0]
receivedMessages = [0,0,0,0,0,0,0,0,0]




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
            await verifyLeader()
        if userInput == 'fail':
            emulateFailure()
        if userInput == 'recover':
            await recoverProcess()
        if userInput == 'metrics':
            generateMetrics()





################ USER INPUT FUNCTION ################

async def verifyLeader():
    # Returns if the leader is alive
    if (leaderID != -1) and active:
        result = await exchangeMessages("4", leaderID)
            
        if (result == ""):
            print(f"Començando eleição por ver lider em falha")
            await election()
        else:
            print(f"O líder de ID {leaderID} está vivo!")
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
    print(f"Mensagens enviadas ordenadas por tipo = {sentMessages[1:]}")
    print(f"Mensagens recebidas ordenadas por tipo = {receivedMessages[1:]}")
    return None





################ CONNECTION HANDLERS ################

# Connects the process to the network

async def connectNetwork():
    global isConnected, programIDList, leaderID, sentMessages, receivedMessages

    while (isConnected == False):
        connect_port = int(input("Insira o ID de um processo existente para se conectar (-1 para se conectar a ninguém): "))
        try:
            if (connect_port != -1):
                returnedMessage = await exchangeMessages(f"6|{uniqueID}", connect_port)
                sentMessages[6] += 1
                
                # Recebe uma mensagem do tipo 7|LIDERID|PROCESSO1|PROCESSO2|PROCESSO3....
                messageElements = [int(n) for n in returnedMessage.split("|")]
                receivedMessages[7] += 1

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
            sentMessages[8] += 1

    

# Functions to handle the listening of messages

async def serverFunc(reader, writer):
    global active, leaderID, programIDList, sentMessages, receivedMessages

    # Creates a function in order to handle to handle messages from ther processes
    data = await reader.read(100)
    message = data.decode()

    # Splits the string into ints
    messageElements = [int(n) for n in message.split("|")]
    
    # Only answers messages when active
    if (active):
        
        # Answering ELEICAO
        if (messageElements[0] == 1):
            receivedMessages[1] += 1

            electionCallerID = messageElements[1]
            
            if electionCallerID < uniqueID:
                message = "2"

                writer.write(message.encode())
                await writer.drain()
                sentMessages[2] += 1

                print(f"Començando eleição por receber um OK")
                await election()

        # Answering OK unecessary
        elif (messageElements[0] == 2):
            receivedMessages[2] += 1

        # Answering LEADER
        elif (messageElements[0] == 3):
            receivedMessages[3] += 1
            leaderID = messageElements[1]

        # Answering VIVO
        elif (messageElements[0] == 4):
            receivedMessages[4] += 1

            # Returns a VIVO_OK
            message = "5"

            writer.write(message.encode())
            await writer.drain()
            sentMessages[5] += 1

        # Answering VIVO_OK unecessary
        elif (messageElements == 5):
            receivedMessages[5] += 1

        # Answering CONNECT 
        elif (messageElements[0] == 6):
            global programIDList
            receivedMessages[6] += 1
    
            # Second element of the return message is the leader ID
            message = "7|" + str(leaderID) + "|"

            # Other elements are all the existing IDs in the network (including the leader)
            for element in programIDList:
                message = message + str(element) + "|"
            message = message[:-1]

            writer.write(message.encode())
            await writer.drain()
            sentMessages[7] += 1

        # Answering CONNECTION_REQUEST already handled by connectNetwork function
        elif (messageElements[0] == 7):
            receivedMessages[7] += 1

        # Answering CONNECT
        elif (messageElements[0] == 8):
            receivedMessages[8] += 1
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

    writer.write(message.encode())

    data = await reader.read(100)

    writer.close()

    return data.decode()





################ RESPONSIBLE FOR RECEIVING MESSAGES ################

async def detectLeaderThread():
    global leaderID, programIDList, sentMessages, receivedMessages

    

    while True:
        # Asks if leader is alive -> VIVO

        # Checks if the process already recognizes a leader
        await asyncio.sleep(30)
        
        print(f"Verificando se o líder está vivo")
        if (leaderID != -1) and active:
            result = await exchangeMessages("4", leaderID)
            sentMessages[4] += 1
            
            if (result == ""):
                print(f"Començando eleição por ver lider em falha")
                await election()
            elif (result == "5"):
                # Received a VIVO_OKif (result == ""):
                print(f"O líder de ID {leaderID} está vivo!")
                receivedMessages[4] += 1





################ ELECTION PROTOCOL ################

async def election():
    global programIDList, uniqueID, leaderID, sentMessages, receivedMessages

    possibleLeader = True

    for program in programIDList:
        if program != uniqueID:  
            # Sends ELEICAO to all processes in the network
            returnMessage = await exchangeMessages(f"1|{uniqueID}", program)
            sentMessages[1] += 1

            # If receives an OK, knows there is a bigger ID than itself, and thus cannot become the leader
            if returnMessage == "2":
                receivedMessages[2] += 1
                possibleLeader = False            
    
    # Has sent to all processes and found no process with a bigger ID
    if possibleLeader == True:
        leaderID = uniqueID
        print("Eu sou o novo líder!")
        print("Comunicando todos os outros processos que sou o novo líder")
        for program in programIDList:
            if program != uniqueID:
                # Envia que é o líder a todos os processos
                leaderID = uniqueID
                await exchangeMessages(f"3|{uniqueID}", program)
                sentMessages[3] += 1
                


        
        



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