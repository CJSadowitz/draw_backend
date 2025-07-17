import os
import os
import sys
import unittest
import psycopg
import json

base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.append(base_dir)

from src.database_scripts.pre_lobby import create_new_lobby, join_lobby, list_lobbies

class test_pre_lobby_request_response(unittest.IsolatedAsyncioTestCase):
    async def test_create_new_lobby(self):
        version = "pre_lobby_create_new_lobby"
        await setup(version)

        token = None
        conn = await psycopg.AsyncConnection.connect("dbname=draw_master user=admin")
        try:
            cursor = conn.cursor()
            await cursor.execute("SELECT token FROM player WHERE uvid=%s", (version,))
            row = await cursor.fetchone()
            token = row[0]
        finally:
            await conn.close()

        packet = { "size": 8, "token": token, "type": "public", "uvid": version }

        username = None
        conn = await psycopg.AsyncConnection.connect("dbname=draw_master user=admin")
        try:
            cursor = conn.cursor()
            await cursor.execute("SELECT username FROM player WHERE token=%s", (token,))
            row = await cursor.fetchone()
            username = row[0]
        finally:
            await conn.close()

        result = await create_new_lobby(json.dumps(packet))

        ulid = None
        conn = await psycopg.AsyncConnection.connect("dbname=draw_master user=admin")
        try:
            cursor = conn.cursor()
            await cursor.execute("SELECT ulid FROM Lobby WHERE uvid=%s", (version,))
            row = await cursor.fetchone()
            ulid = row[0]

        finally:
            await conn.close()

        self.assertEqual(result, { "success": 200,
                                  username: { "ulid": ulid,
                                              "type": "public",
                                              "uvid": version,
                                              "size": 8,
                                              "status": "joinable"
                                             }
                                  }
        )

        conn = await psycopg.AsyncConnection.connect("dbname=draw_master user=admin")
        try:
            cursor = conn.cursor()
            await cursor.execute("SELECT ulid FROM lobby WHERE uvid=%s", (version,))
            result = await cursor.fetchone()
            self.assertNotEqual(result, None)

            await cursor.execute("SELECT ulmid FROM lobby_member")
            result = await cursor.fetchone()
            self.assertNotEqual(result, None)

            await cursor.execute("DELETE FROM lobby_member WHERE uuid=(SELECT uuid FROM player WHERE uvid=%s)", (version,)) 
            await cursor.execute("DELETE FROM lobby WHERE uvid=%s", (version,))
        finally:
            await conn.commit()
            await conn.close()

        await cleanup(version)

    async def test_join_lobby(self):
        version = "test_join_lobby"
        await setup(version)
        conn = await psycopg.AsyncConnection.connect("dbname=draw_master user=admin")
        try:
            cursor = conn.cursor()
            await cursor.execute("DELETE FROM lobby_member WHERE uuid=(SELECT uuid FROM player WHERE uvid=%s)", (version,))
            await cursor.execute("DELETE FROM lobby WHERE uvid=%s", (version,))
            await cursor.execute("INSERT INTO lobby (uvid, status, type, size) VALUES (%s, %s, %s, %s)",
                                 (version, "joinable", "public", 2))
        finally:
            await conn.commit()
            await conn.close()

        token, ulid = None, None
        conn = await psycopg.AsyncConnection.connect("dbname=draw_master user=admin")
        try:
            cursor = conn.cursor()
            await cursor.execute("SELECT token FROM player WHERE uvid=%s", (version,))
            row = await cursor.fetchone()
            token = row[0]
            await cursor.execute("SELECT ulid FROM lobby WHERE uvid=%s", (version,))
            row = await cursor.fetchone()
            ulid = row[0]

        finally:
            await conn.close()
 
        # Test
        packet = { "ulid": ulid, "token": token }

        result = await join_lobby(json.dumps(packet))
        self.assertEqual(result, { "success": 200 })

        conn = await psycopg.AsyncConnection.connect("dbname=draw_master user=admin")
        try:
            cursor = conn.cursor()
            await cursor.execute("SELECT COUNT(*) FROM lobby_member WHERE ulid=%s", (ulid,))
            row = await cursor.fetchone()
            count = row[0]
            self.assertEqual(count, 1)

            # Second member join
            await join_lobby(json.dumps(packet))
            await cursor.execute("SELECT COUNT(*) FROM lobby_member WHERE ulid=%s", (ulid,))
            row = await cursor.fetchone()
            count = row[0]
            self.assertEqual(count, 2)

            # Lobby full test
            result = await join_lobby(json.dumps(packet))
            self.assertEqual(result, { "error": 403 })

        finally:
            await conn.close()

        conn = await psycopg.AsyncConnection.connect("dbname=draw_master user=admin")
        try:
            cursor = conn.cursor()
            await cursor.execute("DELETE FROM lobby_member WHERE uuid IN (SELECT uuid FROM Player WHERE uvid=%s)", (version,))
            await cursor.execute("DELETE FROM lobby WHERE uvid=%s", (version,))

        finally:
            await conn.commit()
            await conn.close()
 
        await cleanup(version)

    async def test_list_lobbies(self):
        version = "test_list_lobbies"
        await setup(version)

        # No lobbies test

        token = None
        conn = await psycopg.AsyncConnection.connect("dbname=draw_master user=admin")
        try:
            cursor = conn.cursor()
            await cursor.execute("SELECT token FROM player WHERE uvid=%s", (version,))
            row = await cursor.fetchone()
            token = row[0]
        finally:
            await conn.close()

        packet = { "token": token }
        result = await list_lobbies(json.dumps(packet))

        self.assertEqual(result, { "success": 200, "lobbies": [] })

        conn = await psycopg.AsyncConnection.connect("dbname=draw_master user=admin")
        try:
            cursor = conn.cursor()
            await cursor.execute("INSERT INTO lobby (uvid, status, type, size) VALUES (%s, %s, %s, %s)",
                                 (version, "joinable", "public", 2))
            await cursor.execute("INSERT INTO lobby (uvid, status, type, size) VALUES (%s, %s, %s, %s)",
                                 (version, "joinable", "public", 2))
        finally:
            await conn.commit()
            await conn.close()
 
        # Test with two lobbies
        result = await list_lobbies(json.dumps(packet))

        self.assertEqual(len(result["lobbies"]), 2)

        conn = await psycopg.AsyncConnection.connect("dbname=draw_master user=admin")
        try:
            cursor = conn.cursor()
            await cursor.execute("DELETE FROM lobby_member WHERE uuid IN (SELECT uuid FROM Player WHERE uvid=%s)", (version,))
            await cursor.execute("DELETE FROM lobby WHERE uvid=%s", (version,))

        finally:
            await conn.commit()
            await conn.close()
        
        await cleanup(version)

async def setup(version):
    await cleanup(version)

    conn = await psycopg.AsyncConnection.connect("dbname=draw_master user=admin")
    try:
        cursor = conn.cursor()
        await cursor.execute("SELECT gen_random_uuid()")
        row = await cursor.fetchone()
        token = row[0]

        await cursor.execute("INSERT INTO version (uvid, status) VALUES (%s, %s)", (version, 0))
        await cursor.execute("INSERT INTO player (uvid, username, password, status, token) VALUES (%s, %s, %s, %s, %s)",
                       (version, "pre_lobby_test", "pre_lobby_test", "online", token))
    finally:
        await conn.commit()
        await conn.close()

async def cleanup(version):
    conn = await psycopg.AsyncConnection.connect("dbname=draw_master user=admin")
    try:
        cursor = conn.cursor()
        await cursor.execute("DELETE FROM lobby_member WHERE uuid IN (SELECT uuid FROM Player WHERE uvid=%s)", (version,))
        await cursor.execute("DELETE FROM lobby WHERE uvid=%s", (version,))
        await cursor.execute("DELETE FROM player WHERE uvid=%s", (version,))
        await cursor.execute("DELETE FROM version WHERE uvid=%s", (version,))
    finally:
        await conn.commit()
        await conn.close()

if __name__ == "__main__":
    unittest.main()

