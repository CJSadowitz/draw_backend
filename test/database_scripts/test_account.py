import unittest
import json
import os
import sys
import psycopg

base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.append(base_dir)

from src.database_scripts.account import check_version, create_account, login, guest_login, logout

class test_account_request_response(unittest.IsolatedAsyncioTestCase):
    async def test_check_version(self):
        version = "fake_version"
        packet = { "path": "account/version", "version": version }

        await create_testing_version(version)

        # Check when version is present in db
        result = await check_version(json.dumps(packet))
        self.assertEqual(result, '{"success": 200}')

        await remove_testing_version(version)

        # Check when version is either < 0 or not present in db
        result = await check_version(json.dumps(packet))
        # Hard to test which version exactly is return because it changes based on state of db
        self.assertNotEqual(result, '{"success":200}')

    async def test_create_account(self):
        version = "create_account_testing"
        await create_testing_version_create_account(version)

        # This test packet will not be possible for a user to ever replicate -> password is hashed
        packet = {"username": "create_account_test", "password": "create_account_test", "version": version}

        # Test successful account creation:
        result = await create_account(json.dumps(packet))
        self.assertEqual(result, {"success":200})

        # Test account creation with identical username
        result = await create_account(json.dumps(packet))
        self.assertEqual(result, {"error":403})

        # Delete test account
        conn = await psycopg.AsyncConnection.connect("dbname=draw_master user=admin")
        try:
            cursor = conn.cursor()
            await cursor.execute("DELETE FROM Player WHERE uvid=%s", (version,))
        finally:
            await conn.commit()
            await conn.close()

        await remove_testing_version(version)

    async def test_login(self):
        version = "login_testing"
        await create_testing_version_create_account(version)

        packet = {"username": "login_test", "password": "login_test", "version": version}
        await create_account(json.dumps(packet))

        packet = {"username": "login_test", "password": "login_test"}
        # Guard against error
        conn = await psycopg.AsyncConnection.connect("dbname=draw_master user=admin")
        try:
            cursor = conn.cursor()
            await cursor.execute("UPDATE Player SET status=%s WHERE uvid=%s", ("offline", version))
        finally:
            await conn.commit()
            await conn.close()
 
        result = await login(json.dumps(packet))

        # Successful login
        self.assertNotEqual(result, {"error":404})
        self.assertNotEqual(result, {"error":403})

        token = result["token"]
        db_token = None

        conn = await psycopg.AsyncConnection.connect("dbname=draw_master user=admin")
        try:
            cursor = conn.cursor()
            await cursor.execute("SELECT token FROM Player WHERE uvid=%s",(version,))
            row = await cursor.fetchone()
            db_token = row[0]
        finally:
            await conn.close()

        self.assertEqual(token, db_token)

        # Delete test account
        conn = await psycopg.AsyncConnection.connect("dbname=draw_master user=admin")
        try:
            cursor = conn.cursor()
            await cursor.execute("DELETE FROM Player WHERE uvid=%s", (version,))
        finally:
            await conn.commit()
            await conn.close()

        await remove_testing_version(version)

        # Test login to nonexistant account
        result = await login(json.dumps(packet))
        self.assertEqual(result, {"error": 404})


    async def test_guest_login(self):
        version = "guest"
        packet = { "version":  version }

        # Guard for errors
        conn = await psycopg.AsyncConnection.connect("dbname=draw_master user=admin")
        try:
            cursor = conn.cursor()
            await cursor.execute("DELETE FROM Player WHERE uvid=%s",(version,))

        finally:
            await conn.commit()
            await conn.close()

        await create_testing_version(version)

        token = await guest_login(json.dumps(packet))

        result = None
        conn = await psycopg.AsyncConnection.connect("dbname=draw_master user=admin")
        try:
            cursor = conn.cursor()
            await cursor.execute("SELECT token FROM Player WHERE uvid=%s", (version,))
            result = await cursor.fetchone()

        finally:
            await conn.close()

        # A row with this guest exists
        self.assertNotEqual(result, None)

        self.assertEqual(token["token"], result[0])

        conn = await psycopg.AsyncConnection.connect("dbname=draw_master user=admin")
        try:
            cursor = conn.cursor()
            await cursor.execute("DELETE FROM Player WHERE uvid=%s",(version,))

        finally:
            await conn.commit()
            await conn.close()

        await remove_testing_version(version)

    async def test_logout(self):
        # Setup
        version = "logout"

        # Guard for errors
        conn = await psycopg.AsyncConnection.connect("dbname=draw_master user=admin")
        try:
            cursor = conn.cursor()
            await cursor.execute("DELETE FROM Player WHERE uvid=%s",(version,))

        finally:
            await conn.commit()
            await conn.close()

        await create_testing_version(version)

        create_account_packet = { "username": "log_out_test", "password": "log_out_test", "version": version }
        
        await create_account(json.dumps(create_account_packet))

        login_packet = { "username": "log_out_test", "password": "log_out_test" }

        response = await login(json.dumps(login_packet))
        token = response["token"]

        # Test
        logout_packet = { "token": token }
        result = await logout(json.dumps(logout_packet))

        # Cleanup
        conn = await psycopg.AsyncConnection.connect("dbname=draw_master user=admin")
        try:
            cursor = conn.cursor()
            await cursor.execute("DELETE FROM Player WHERE uvid=%s", (version,))
        finally:
            await conn.commit()
            await conn.close()
        await remove_testing_version(version)

    async def test_guest_logout(self):
        version = "guest_logout"

        # Guard for errors
        conn = await psycopg.AsyncConnection.connect("dbname=draw_master user=admin")
        try:
            cursor = conn.cursor()
            await cursor.execute("DELETE FROM Player WHERE uvid=%s",(version,))

        finally:
            await conn.commit()
            await conn.close()

        await create_testing_version(version)

        packet = { "version": version }
        response = await guest_login(json.dumps(packet))
        token = response["token"]

        packet = { "token": token }
        result = await logout(json.dumps(packet))

        self.assertEqual(result, { "success": 200 })
       
        conn = await psycopg.AsyncConnection.connect("dbname=draw_master user=admin")
        try:
            cursor = conn.cursor()
            await cursor.execute("DELETE FROM Player WHERE uvid=%s",(version,))

        finally:
            await conn.commit()
            await conn.close()

        await remove_testing_version(version)

async def create_testing_version(version):
    conn = await psycopg.AsyncConnection.connect("dbname=draw_master user=admin")
    try:
        cursor = conn.cursor()
        try:
            # If unit test fails, this ensures that it can run again to test fixes"
            await cursor.execute("DELETE FROM version WHERE uvid=%s", (version,))
            await conn.commit()

        except Exception as e:
            await conn.rollback()

        await cursor.execute("""
            INSERT INTO Version (uvid, status) VALUES (%s, %s)""",
            (version, 0)
        )

    finally:
        await conn.commit()
        await conn.close()

async def remove_testing_version(version):
        # Remove fake version from db
        conn = await psycopg.AsyncConnection.connect("dbname=draw_master user=admin")
        try:
            cursor = conn.cursor()
            await cursor.execute("DELETE FROM version WHERE uvid=%s", (version,))
        finally:
            await conn.commit()
            await conn.close()

async def create_testing_version_create_account(version):
        conn = await psycopg.AsyncConnection.connect("dbname=draw_master user=admin")
        try:
            # A version needs to be avaliable for this to work
            cursor = conn.cursor()
            try:
                # If check fails, this ensures that it can run again to test fixes"
                await cursor.execute("DELETE FROM Player WHERE uvid=%s", (version,))
                await cursor.execute("DELETE FROM version WHERE uvid=%s", (version,))
                await conn.commit()

            except Exception as e:
                await conn.rollback()

            await cursor.execute("""
                INSERT INTO Version (uvid, status) VALUES (%s, %s)""",
                (version, 0)
            )

        finally:
            await conn.commit()
            await conn.close()

if __name__ == "__main__":
    unittest.main()

