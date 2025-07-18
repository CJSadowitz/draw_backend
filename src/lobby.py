import psycopg
import asyncio
import src.global_connections

def host_lobby(connection, ulid):
    asyncio.run(host_lobby_async(connection, ulid))

async def host_lobby_async(conn, ulid):
    active_connections = await get_connections(ulid, [])
    in_lobby = True
    while in_lobby:
        # Lobby Logic
        # Game Logic
        # Consider logging out or leaving lobby
        break
        pass

async def get_connections(ulid, current_connections):
    conn_objects = []
    rows = await get_current_lobby_members(ulid)
    for row in rows:
        uuid = row[0]
        if uuid in g_connection.keys():
            conn_object = g_connection[uuid]["connection"]
            if conn_object in current_connections:
                continue
            else:
                conn_objects.append(conn_object)
                g_connection[uuid]["status"] = "in_lobby"

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
def loading(connection):
    # Consider removing the object from global_connections.connections to free memory
    in_lobby = False
    while not in_lobby:
        in_lobby = check_player_status(uuid)

def check_player_status(uuid):
    if key in global_connections.connections.key:
        status = src.global_connections.connections[uuid]["status"]
        if status == "waiting":
            return False
        else:
            return True

