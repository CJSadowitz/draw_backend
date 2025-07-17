import unittest
import json
import os
import sys
import psycopg

base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.append(base_dir)

from src.database_scripts.account import login
from src.database_scripts.security import verify_token

class test_account_request_response(unittest.IsolatedAsyncioTestCase):
    async def test_verify_token(self):
        # Setup
        version = "test_verify_token"
        # Create Version
        conn = await psycopg.AsyncConnection.connect("dbname=draw_master user=admin")
        try:
            # Guard for errors:
            cursor = conn.cursor()
            await cursor.execute("DELETE FROM Player WHERE uvid=%s", (version,))
            await cursor.execute("DELETE FROM Version WHERE uvid=%s", (version,))

            await cursor.execute("INSERT INTO Version (uvid, status) VALUES (%s, %s)", (version, 0))
            await cursor.execute("""
                INSERT INTO Player (uvid, username, password, status) VALUES (%s, %s, %s, %s)
                """, (version, "verify_token_test", "verify_token_test", "offline")
            )
        finally:
            await conn.commit()
            await conn.close()

        # Login
        packet = { "username": "verify_token_test", "password": "verify_token_test" }
        response = await login(json.dumps(packet))
        token = response["token"]

        # Test
        result = await verify_token(token)
        self.assertEqual(result, { "success": 200 })

        token = "not_a_valid_token"
        result = await verify_token(token)
        self.assertEqual(result, { "error": 400 })

        # Cleanup
        conn = await psycopg.AsyncConnection.connect("dbname=draw_master user=admin")
        try:
            cursor = conn.cursor()
            await cursor.execute("DELETE FROM Player WHERE uvid=%s", (version,))
            await cursor.execute("DELETE FROM Version WHERE uvid=%s", (version,))

        finally:
            await conn.commit()
            await conn.close()

if __name__ == "__main__":
   unittest.main() 

