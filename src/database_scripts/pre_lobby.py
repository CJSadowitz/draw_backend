import psycopg
import asyncio
import json

import src.global_connections

# Received:
#{
#   "path": "pre_lobby/create_new_lobby",
#   "size": 2-8,
#   "token": "hash",
#   "type": "public/private",
#   "uvid": "hash"
#}

# Return:
#{
#   "success": 200,
#   "lobby": { "ulid": ulid, "type": type, "version": version, "size": size, "username", username}
#}

async def create_new_lobby(connection, packet):
    packet = json.loads(packet)
    size = packet["size"]
    lobby_type = packet["type"]
    token = packet["token"]
    # Create new lobby row
    conn = await psycopg.AsyncConnection.connect("dbname=draw_master user=admin") 
    try:
        cursor = conn.cursor()
        # Get user's version
        await cursor.execute("SELECT uuid, uvid, username FROM Player WHERE token=%s", (token,))
        row = await cursor.fetchone()
        uuid = row[0]
        version = row[1]
        username = row[2]

        # Create new lobby instance
        await cursor.execute("""
            INSERT INTO Lobby (uvid, status, type, size) VALUES (%s, %s, %s, %s) RETURNING ulid
            """,
            (version, 'joinable', lobby_type, size)
        )

        row = await cursor.fetchone()
        ulid = row[0]

        # Add the host to lobby_memebers as slot 0 (host)
        await cursor.execute("""
            INSERT INTO Lobby_member (ulid, uuid, slot_number) VALUES (%s, %s, %s)
            """, (ulid, uuid, 0)
        )

        add_connection(connection, uuid, ulid, "hosting")

        await cursor.execute("SELECT * FROM Lobby WHERE ulid=%s", (ulid,))
        row = await cursor.fetchone()

        return {
            "success": 200,
            "lobby": get_lobby_attributes(row)
        }

    finally:
        await conn.commit()
        await conn.close()

# Received:
#{
#   "path": "pre_lobby/join_lobby",
#   "ulid": "hash",
#   "token": "hash",
#}

# Return:
#{
#   "success": 200,
#}
# Or:
#{
#   "error": 403,
#}

async def join_lobby(connection, packet):
    packet = json.loads(packet)
    token = packet["token"]
    ulid = packet["ulid"]
    conn = await psycopg.AsyncConnection.connect("dbname=draw_master user=admin") 
    try:
        cursor = conn.cursor()

        await cursor.execute("SELECT uuid FROM Player WHERE token=%s", (token,))
        row = await cursor.fetchone()
        uuid = row[0]

        await cursor.execute("""
            SELECT slot_number FROM Lobby_member WHERE ulid=%s ORDER BY slot_number DESC""",
            (ulid,)
        )

        active_positions = await cursor.fetchall()
        active_positions = [pos[0] for pos in active_positions]

        await cursor.execute("SELECT size FROM Lobby WHERE ulid=%s", (ulid,))
        row = await cursor.fetchone()
        size = row[0]
        
        pos = None
        try:
            full_set = set(range(1, size + 1))
            pos = min(full_set - set(active_positions))
        except Exception as e:
            # Lobby is full
            return { "error": 403 }

        await cursor.execute("INSERT INTO Lobby_member (ulid, uuid, slot_number) VALUES (%s, %s, %s)", (ulid, uuid, pos))
        
        add_connection(connection, uuid, ulid, "waiting")

        return { "success": 200, "uuid": uuid }

    finally:
        await conn.commit()
        await conn.close()

# Request:
#{
#   "path": "pre_lobby/list_lobbies",
#   "token": "hash"
#}
# Return:
#{
#   "success": 200,
#   "lobbies": [
#       "username_0": { lobby_stat: "val", ... }
#       ...
#       "username_n": { lobby_stat: "val", ... }
#   ]
#}

async def list_lobbies(packet):
    packet = json.loads(packet)
    conn = await psycopg.AsyncConnection.connect("dbname=draw_master user=admin")
    try:
        cursor = conn.cursor()

        # Get all public lobbies
        await cursor.execute("SELECT * FROM Lobby WHERE type=%s", ("public",))
        rows = await cursor.fetchall()

        lobbies = []
        for row in rows:
            # Get host
            ulid = row[0]
            await cursor.execute("""
                SELECT uuid FROM Lobby_member WHERE ulid=%s""", 
                (ulid,)
            )
            lobby_member_row = await cursor.fetchone()
            if lobby_member_row != None:
                host_username = lobby_member_row[0]
                lobbies.append({ str(host_username): get_lobby_attributes(row) })
            else:
                host_username = "empty"
                lobbies.append({ str(host_username): get_lobby_attributes(row) })

        return { "success": 200, "lobbies": lobbies }
    finally:
        await conn.close()


def add_connection(conn, uuid, ulid, status):
    if conn and uuid and ulid:
        src.global_connections.connections[uuid] = {"ulid": ulid, "connection": conn, "status": status}

def get_lobby_attributes(row):
    # [ulid, ugid, uvid, status, type, size]
    return { "ulid": row[0], "uvid": row[2], "status": row[3], "type": row[4], "size": row[5] }

