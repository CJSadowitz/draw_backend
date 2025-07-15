import psycopg
import asyncio
from src.database_scripts import create_account, guest_login, login, check_version, logout
from src.database_scripts import list_lobbies, create_lobby, join_lobby
import socket

# Gross...

# Returns a boolean for lobby state
async def handle_message(conn, packet):
    # parse the packet
    path = packet["path"]
    message = None

    if "account" in path:
        message = await account_message(packet, path)
    elif "pre_lobby" in path:
        message = await pre_lobby_message(packet, path)

    conn.send(json.dumps(message).encode("utf-8"))

async def account_message(packet, path):
    sub_path = path.split('/')[1]
    switch (sub_path):
        case ("login"):
            return await login(packet)
        case ("create_account"):
            return await create_account(packet)
        case ("guest"):
            return await guest_login(packet)
        case ("version"):
            return await check_version(packet)
        case ("logout"):
            return await logout(packet)
        case _:
            return { "error": 404 }

async def pre_lobby_message(packet, path):
    sub_path = path.split('/')[0]
    switch (sub_path):
        case ("create_new_lobby"):
            return await create_lobby(packet)
        case ("join_lobby"):
            return await join_lobby(packet)
        case ("list_lobbies"):
            return await list_lobbies(packet)

if __name__ == "__main__":
    pass

