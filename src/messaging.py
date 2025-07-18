import psycopg
import asyncio
from src.database_scripts.account import create_account, guest_login, login, check_version, logout
from src.database_scripts.pre_lobby import list_lobbies, create_new_lobby, join_lobby
import socket
import json

# Returns next state
async def handle_message(conn, packet):
    path = json.loads(packet)["path"]
    message = None

    print ("message:", packet)

    if "account" in path:
        message = await account_message(packet, path)
    elif "pre_lobby" in path:
        message = await pre_lobby_message(conn, packet, path)
        ulid = None
        if "ulid" in message:
            ulid = message["ulid"]

        if "lobby" in message:
            ulid = message["lobby"]["ulid"]

        if path == "pre_lobby/join_lobby" and "success" in message.keys():
            conn.send(json.dumps(message).encode("utf-8"))
            return "join_lobby", ulid
        if path == "pre_lobby/create_new_lobby" and "success" in message.keys():
            conn.send(json.dumps(message).encode("utf-8"))
            return "create_lobby", ulid
    else:
        message = { "error": 404, "path_not_found": path }

    conn.send(json.dumps(message).encode("utf-8"))
    return "end", None

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

async def pre_lobby_message(conn, packet, path):
    sub_path = path.split('/')[1]
    match (sub_path):
        case ("create_new_lobby"):
            return await create_new_lobby(conn, packet)
        case ("join_lobby"):
            return await join_lobby(conn, packet)
        case ("list_lobbies"):
            return await list_lobbies(packet)
        case _:
            return { "error": 404, "path_not_found": path }

