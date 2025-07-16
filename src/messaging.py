import psycopg
import asyncio
from src.database_scripts.account import create_account, guest_login, login, check_version, logout
from src.database_scripts.pre_lobby import list_lobbies, create_new_lobby, join_lobby
import socket
import json

# Gross...

# Returns a boolean for lobby state
async def handle_message(conn, packet):
    # parse the packet
    path = json.loads(packet)["path"]
    message = None

    if "account" in path:
        message = await account_message(packet, path)
    elif "pre_lobby" in path:
        message = await pre_lobby_message(packet, path)
        for key in message:
            if key == "success":
                conn.send(json.dumps(message).encode("utf-8"))
                return True
    else:
        message = { "error": 404, "path_not_found": path }

    conn.send(json.dumps(message).encode("utf-8"))
    return False

async def account_message(packet, path):
    sub_path = path.split('/')[1]
    match (sub_path):
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
            return { "error": 404, "path_not_found": path }

async def pre_lobby_message(packet, path):
    sub_path = path.split('/')[0]
    match (sub_path):
        case ("create_new_lobby"):
            return await create_lobby(packet)
        case ("join_lobby"):
            return await join_lobby(packet)
        case ("list_lobbies"):
            return await list_lobbies(packet)
        case _:
            return { "error": 404, "path_not_found": path }

if __name__ == "__main__":
    pass

