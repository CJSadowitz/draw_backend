import socket
import threading
from src.client_handler import handle_client

g_connections = dict()

def main():
    address = ("", 8008)
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    server.bind(address)
    server.listen(10)
    while True:
        connection, address = server.accept()

        request_response = threading.thread(target=handle_client, args=(connection,))
        request_response.start() 

if __name__ == "__main__":
    main()

