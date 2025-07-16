import psycopg
import asyncio
import json

# Received:
#{
#   "path": "account/version",
#   "version": "hash"
#}

# Returned:
#{
#   "success": 200
#}
# Or:
#{
#   "version": "hash"
#}

async def check_version(packet):
    packet = json.loads(packet)
    version = packet["version"]

    conn = await psycopg.AsyncConnection.connect("dbname=draw_master user=admin")
    try:
        cursor = conn.cursor()
        await cursor.execute("SELECT uvid FROM Version WHERE status>=0")
        row = await cursor.fetchall()
        for item in row:
            if version == item[0]:
                return json.dumps({ "success": 200 })
        try:
            await cursor.execute("SELECT uvid FROM Version WHERE status=1")
            row = await cursor.fetchone()
            return { "version": row[0] }
        
        except Exception as e:
            return { "error": 500 }

    finally:
        await conn.close()

# Received:
#{
#   "path": "account/login",
#   "username": "username",
#   "password": "hash"
#}

# Returned:
#{
#   "token": hash
#}
# Or:
#{
#   "error": 404
#}

async def login(packet):
    packet = json.loads(packet)
    username = packet["username"]
    password = packet["password"]
    conn = await psycopg.AsyncConnection.connect("dbname=draw_master user=admin")
    try:
        cursor = conn.cursor()
        # Verify user's existance
        await cursor.execute("SELECT uuid, token FROM Player WHERE username = %s AND password = %s", (username, password))
        row = await cursor.fetchone()
        if row == None:
            return { "error": 404 }

        # User already has a token; someone else logged in? 
        if row[1] != None:
            return { "error": 403 }

        await cursor.execute("SELECT gen_random_uuid()")
        data = await cursor.fetchone()
        token = data[0]

        await cursor.execute("UPDATE Player SET token=%s, status=%s WHERE uuid=%s", (token, "online", row[0]))
        await conn.commit()

        return { "token": str(token) }

    finally:
        await conn.close()
        
# Received:
#{
#   "path": "account/create_account",
#   "username": text,
#   "password": hash,
#   "version": hash,
#}

# Returned:
#{
#   "success": 200
#}
# Or:
#{
#   "error": 409
#}

async def create_account(packet):
    packet = json.loads(packet)
    username = packet["username"]
    password = packet["password"]
    version  = packet["version"]
    conn = await psycopg.AsyncConnection.connect("dbname=draw_master user=admin")
    try:
        cursor = conn.cursor()
        # Check if username is already taken
        await cursor.execute("SELECT username FROM Player WHERE username=%s", (username,))
        data = await cursor.fetchall()
        if data != []:
            return { "error": 403 }

        # Add user
        try:
            await cursor.execute("""
                INSERT INTO Player (username, password, uvid, status) VALUES (%s, %s, %s, %s)
                """, 
                (username, password, version, "offline")
            )
            return { "success": 200 }

        except psycopg.Error as e:
            print (e)
            return { "error": 500 }

    finally:
        await conn.commit()
        await conn.close()

# Request:
#{
#   "path": "account/guest",
#   "version": "hash"
#}

# Return:
#{
#   "token": "token"
#}

async def guest_login(packet):
    packet = json.loads(packet)
    version = packet["version"]
    conn = await psycopg.AsyncConnection.connect("dbname=draw_master user=admin")
    try:
        cursor = conn.cursor()
        
        # Generate token
        await cursor.execute("SELECT gen_random_uuid()")
        row = await cursor.fetchone()
        token = row[0]

        # Generate password
        await cursor.execute("SELECT gen_random_uuid()")
        row = await cursor.fetchone()
        password = row[0]

        await cursor.execute("""
            INSERT INTO Player (username, password, uvid, status, token) VALUES (%s, %s, %s, %s, %s)
            """, 
            ("", password, version, "online", token)
        )
        return { "token": str(token) }

    finally:
        await conn.commit()
        await conn.close()

# Request:
#{
#   "path": "account/logout",
#   "logout": "token"
#}

# Return:
#{
#   "success": 200
#}

async def logout(packet):
    packet = json.loads(packet)
    token = packet["token"]
    conn = await psycopg.AsyncConnection.connect("dbname=draw_master user=admin")
    try:
        cursor = conn.cursor()
        # Check if token is associated with a guest
        await cursor.execute("SELECT username FROM Player WHERE token=%s", (token,))
        row = await cursor.fetchone()
        if row[0] != "":
            # Set to offline remove token
            await cursor.execute("UPDATE Player SET status=%s WHERE token=%s", ("offline", None))
            return { "success": 200 }

        # Delete guest from database
        await cursor.execute("DELETE FROM Player WHERE token=%s", (token,))
        return { "success": 200 }

    finally:
        await conn.commit()
        await conn.close()

