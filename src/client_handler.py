from src.messaging import handle_message

def handle_client(conn):
    message = conn.recv(1024).decode("utf-8")
    is_lobby = handle_message(conn, message)
    if is_lobby:
        in_lobby = True
        while in_lobby:
            pass
    return

