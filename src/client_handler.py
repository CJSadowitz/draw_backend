from src.messaging import handle_message
from src.lobby import host_lobby, loading
import threading
import asyncio

def handle_client(connection):
    message = connection.recv(1024).decode("utf-8")
    # Both request and respose
    next_state = asyncio.run(handle_message(connection, message))

    # Create lobby thread here (host creates this thread...)
    match (next_state):
        case ("create_lobby"):
            lobby_thread = threading.Thread(target=host_lobby, args=(connection,))
            lobby_thread.start()
            break
        case ("join_lobby"):
            loading_thread = threading.Thread(target=loading, args=(connection,))
            loading_thread.start()
            break
        case ("end"):
            connection.close()
            
