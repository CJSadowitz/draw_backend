import psycopg
import asyncio

async def verify_token(token):
    conn = await psycopg.AsyncConnection.connect("dbname=draw_master user=admin")
    try:
        cursor = conn.cursor()

        await cursor.execute("SELECT uuid FROM player WHERE token=%s", (token,))
        row = await cursor.fetchone()
        if row != None:
            return { "success": 200 }
        return { "error": 400 }

    finally:
        await conn.close()

