from src.messaging import handle_message
from src.lobby import host_lobby
import threading

def handle_client(connection):
    message = connection.recv(1024).decode("utf-8")
    # Both request and respose
    is_host = handle_message(connection, message)

    # Create lobby thread here (this is the host thread...)
    if is_host:
        lobby_thread = threading.thread(target=host_lobby, args=(connection,)) 
        lobby_thread.start()

    else:
        connection.close()

