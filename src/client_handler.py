from src.messaging import handle_message
from src.lobby import host_lobby
import threading
import asyncio

def handle_client(connection):
    message = connection.recv(1024).decode("utf-8")
    # Both request and respose
    is_host = asyncio.run(handle_message(connection, message))

    # Create lobby thread here (host creates this thread...)
    if is_host:
        lobby_thread = threading.Thread(target=host_lobby, args=(connection,)) 
        lobby_thread.start()

    else:
        connection.close()

