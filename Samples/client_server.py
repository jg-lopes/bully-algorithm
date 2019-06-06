import asyncio
import os

connect_port = input("Insira o PID do processo servidor: ")

async def client_wrapper(message, port):
    while True:
        await asyncio.sleep(2)
        await tcp_echo_client(message, port)

async def tcp_echo_client(message, port):
    reader, writer = await asyncio.open_connection(
        '127.0.0.1', port)

    print(f'Send: {message!r}')
    writer.write(message.encode())

    data = await reader.read(100)
    print(f'Received: {data.decode()!r}')

    print('Close the connection')
    writer.close()

async def handle_echo(reader, writer):
    data = await reader.read(100)
    message = data.decode()
    addr = writer.get_extra_info('peername')

    print(f"Received {message!r} from {addr!r}")

    print(f"Send: {message!r}")
    writer.write(data)
    await writer.drain()

    print("Close the connection")
    writer.close()

async def main():
    server = await asyncio.start_server(handle_echo, '127.0.0.1', os.getpid())

    addr = server.sockets[0].getsockname()
    print(f'Serving on {addr}')
    

    await asyncio.gather(
        await client_wrapper("Message", connect_port),
        await server.serve_forever()
    )

    

   

    

    

asyncio.run(main())
