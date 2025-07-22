import psycopg
import asyncio
import src.global_connections
import time

def host_lobby(connection, ulid):
    asyncio.run(host_lobby_async(connection, ulid))

async def host_lobby_async(conn, ulid):
    active_connections = await get_connections(ulid, [])
    print ("ULID:", ulid)
    in_lobby = True
    while in_lobby:
        print (active_connections)
        time.sleep(1)
        active_connections = await get_connections(ulid, active_connections)
        for connection in active_connections:
            connection.send("WELCOME GAMERS".encode("utf-8"))
        # Lobby Logic
        # Game Logic
        # Consider logging out or leaving lobby

async def get_connections(ulid, current_connections):
    conn_objects = []
    rows = await get_current_lobby_members(ulid)
    for row in rows:
        uuid = row[0]
        if uuid in src.global_connections.connections.keys():
            conn_object = src.global_connections.connections[uuid]["connection"]
            if conn_object in current_connections:
                continue
            else:
                conn_objects.append(conn_object)
                src.global_connections.connections[uuid]["status"] = "in_lobby"

    return current_connections + conn_objects 

async def get_current_lobby_members(ulid):
    conn = await psycopg.AsyncConnection.connect("dbname=draw_master user=admin")
    rows = None
    try:
        cursor = conn.cursor()
        await cursor.execute("SELECT uuid FROM Lobby_member WHERE ulid=%s", (ulid,))
        rows = await cursor.fetchall()

    finally:
        await conn.close()

    return rows

# Busy wait -> replace with async later
def loading(connection, uuid):
    print ("Joiner is loading")
    # Consider removing the object from global_connections.connections to free memory
    in_lobby = False
    while not in_lobby:
        in_lobby = check_player_status(uuid)

# Busy wait -> replace with async later
def check_player_status(uuid):
    if uuid in src.global_connections.connections.keys():
        status = src.global_connections.connections[uuid]["status"]
        if status == "waiting":
            return False
        else:
            return True

