import psycopg
import asyncio

async def verify_token(token):
    conn = await psycopg.AsyncConnection.connect("dbname=draw_master user=player")
    try:
        cursor = conn.cursor()

        await conn.execute("SELECT uuid FROM player WHERE token=%s", (token,))
        row = await conn.fetchone()
        if row != []:
            return row[0]
        return

    finally:

if __name__ == "__main__":
    pass

