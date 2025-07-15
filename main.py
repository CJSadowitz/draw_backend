import socket
import threading
from src.client_handler import handle_client

def main():
    address = ("", 8008)
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    server.bind(address)
    server.listen(10)
    while True:
        connection, address = server.accept()
        client_handler = threading.thread(target=handle_client, args=(connection,))
        client_handler.start() 

if __name__ == "__main__":
    main()

