import psycopg
import asyncio
import json

# Recieved:
#{
#   "version": hash
#}

# Returned:
#{
#   "success": 200
#}
# Or:
#{
#   "version": hash
#}

async def check_version(packet):
    packet = json.loads(packet)
    version = packet["version"]
    conn = await psycopg.AsyncConnection.connect("dbname=draw_master user=colin")

    try:
        cursor = conn.cursor()
        await cursor.execute("SELECT version FROM Versions WHERE status>=0")
        data = await cursor.fetchall()
        for item in data:
            if version == item[0]:
                return json.dumps({ "success": 200 })
        await cursor.execute("SELECT version FROM Versions WHERE status=1")
        data = await cursor.fetchone()
        return json.dumps({ "version": data[0] })

    finally:
        await conn.close()

# Received:
#{
#   "username": username,
#   "password": hash
#}

# Returned:
#{
#   "token": hash
#}

async def login(packet):
    packet = json.loads(packet)
    username = packet["username"]
    password = packet["password"]
    conn = await psycopg.AsyncConnection.connect("dbname=draw_master user=player")
    try:
        cursor = conn.cursor()
        await cursor.execute("SELECT uuid FROM Players WHERE username = %s AND password = %s", (username, password))
        data = cursor.fetchall()

    finally:
        await conn.close()
        

def create_account(packet):
    pass

if __name__ == "__main__":
    packet = {}
    packet["version"] = "f"
    json_packet = json.dumps(packet)
    print (asyncio.run(check_version(json_packet)))

   
