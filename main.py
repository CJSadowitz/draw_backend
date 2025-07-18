import socket
import threading
from src.client_handler import handle_client

#{
#   "uuid_1": { "connection": socket_connection_object,
#             "status":     "in_lobby/waiting",
#             "lobby":      "ulid"
#           },
#   "uuid_2": { "connection": socket_connection_object,
#             "status":     "waiting",
#             "lobby":      None
#           }
#}

g_connections = dict()

def main():
    address = ("", 8008)
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    server.bind(address)
    server.listen(10)
    while True:
        connection, address = server.accept()

        request_response = threading.Thread(target=handle_client, args=(connection,))
        request_response.start() 

if __name__ == "__main__":
    main()

