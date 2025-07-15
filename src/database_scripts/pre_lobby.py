import psycopg
import asyncio

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
#   "lobby": { "uuid": uuid, "type": type, "version": version, "size": size }
#}

async def create_new_lobby(packet):
    size = packet["size"]
    lobby_type = packet["type"]
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
            INSERT INTO Lobby (uvid, status, type, size) VALUES (%s, %s, %s, %s)
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

        await cursor.execute("SELECT * FROM Lobby WHERE ulid=%s", (ulid,))
        row = await cursor.fetchone()

        return {
            "success": 200,
            str(username): get_lobby_attributes(row)
        }

    finally:
        await cursor.commit()
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

async def join_lobby(packet):
    ulid = packet["ulid"]
    conn = await psycopg.AsyncConnection.connect("dbname=draw_master user=admin") 
    try:
        cursor = conn.cursor()
        # Add player to next avaliable slot in the lobby_member
        await cursor.execute("SELECT uuid FROM Player WHERE token=%s", (token,))
        uuid = await cursor.fetchone()[0]

        await cursor.execute("""
            SELECT slot_number FROM Lobby_memeber WHERE ulid=%s ORDER BY slot_number DESC""",
            (ulid,)
        )
        # Find and fill next numerical position
        active_positions = await cursor.fetchall()
        active_positions = [pos[0] for pos in active_positions]

        # Get lobby size
        await cursor.execute("SELECT size FROM Lobby WHERE ulid=%s", (ulid,))
        size = await cursor.fetchone()

        # Compute next value
        full_set = set(range(1, size + 1))
        pos = min(full_set - set(active_positions))

        # Add player to lobby
        await cursor.execute("INSERT INTO Lobby_members ulid=%s, uuid=%s, slot_number=%s", (ulid, uuid, pos))
        return { "success": 200 }

    finally:
        await cursor.commit()
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
    conn = await psycopg.AsyncConnection.connect("dbname=draw_master user=admin")
    try:
        cursor = conn.cursor()

        # Get all public lobbies
        await cursor.execute("SELECT * FROM Lobby WHERE type=%s", ("public",))
        rows = await cursor.fetchall()

        lobbies = []
        for row in rows:
            # Get host
            await cursor.execute("""
                SELECT uuid FROM Lobby_member WHERE ulid=%s AND slot_number=%s""", 
                (ulid, slot_number)
            )
            lobby_memeber_row = await cursor.fetchone()
            host_username = lobby_memeber_row[0]
            lobbies.append({ str(host_username): get_lobby_attributes(row) })

        return { "success": 200, "lobbies": lobbies }
            

def get_lobby_attributes(row):
    # [ulid, ugid, uvid, status, type, size]
    return { "ulid": row[0], "uvid": row[2], "status": row[3], "type": row[4], "size": row[5] }

