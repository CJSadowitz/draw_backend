import unittest
import json
import os
import sys
import psycopg

base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.append(base_dir)

from src.database_scripts.account import check_version

class test_account_request_response(unittest.IsolatedAsyncioTestCase):
    async def test_check_version(self):
        packet = { "path": "account/version", "version": "fake_version" }

        # Create fake version for testing
        conn = await psycopg.AsyncConnection.connect("dbname=draw_master user=admin")
        try:
            cursor = conn.cursor()

            try:
                # If check fails, this ensures that it can run again to test fixes"
                await cursor.execute("DELETE FROM version WHERE uvid=%s", ("fake_version",))
                await conn.commit()

            except Exception as e:
                pass

            await cursor.execute("""
                INSERT INTO Version (uvid, status) VALUES (%s, %s)""",
                ("fake_version", 0)
            )

        finally:
            await conn.commit()
            await conn.close()

        result = await check_version(json.dumps(packet))

        self.assertEqual(result, '{"success": 200}')

        # Remove fake version from db
        conn = await psycopg.AsyncConnection.connect("dbname=draw_master user=admin")
        try:
            cursor = conn.cursor()
            await cursor.execute("DELETE FROM version WHERE uvid=%s", ("fake_version",))
        finally:
            await conn.commit()
            await conn.close()

        result = await check_version(json.dumps(packet))

        # Hard to test which version exactly is return because it changes based on state of db
        self.assertNotEqual(result, '{"success":200}')

    def test_login(self):
        pass

    def test_create_account(self):
        pass

    def test_guest_login(self):
        pass

    def test_logout(self):
        pass

if __name__ == "__main__":
    unittest.main()

