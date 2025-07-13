import psycopg
import asyncio

async def setup_tables():
    conn = await psycopg.AsyncConnection.connect("dbname=draw_master user=admin")
    try:
        cursor = conn.cursor()
       
        await conn.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto;")

        # Versions
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS Versions (
                uvid TEXT PRIMARY KEY NOT NULL UNIQUE DEFAULT gen_random_uuid(),
                type TEXT NOT NULL
                );
        """)
        
        # Player
        await cursor.execute("""
            CREATE TABLE IF NOT EXISTS Player (
                uuid TEXT PRIMARY KEY NOT NULL UNIQUE DEFAULT gen_random_uuid(),
                uvid TEXT NOT NULL,
                username TEXT NOT NULL,
                password TEXT NOT NULL,
                status TEXT NOT NULL,
                token TEXT
                );
        """)
       
        # Lobbies
        await cursor.execute("""
            CREATE TABLE IF NOT EXISTS Lobbies (
                ulid TEXT PRIMARY KEY NOT NULL UNIQUE DEFAULT gen_random_uuid(),
                ugid TEXT,
                uvid TEXT NOT NULL,
                status TEXT NOT NULL,
                type TEXT NOT NULL,
                size int NOT NULL,
                uuid1 TEXT,
                uuid2 TEXT,
                uuid3 TEXT,
                uuid4 TEXT,
                uuid5 TEXT,
                uuid6 TEXT,
                uuid7 TEXT,
                uuid8 TEXT
                );
        """)
       
        # Game
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS Game (
                ugid TEXT PRIMARY KEY NOT NULL UNIQUE DEFAULT gen_random_uuid(),
                ulid TEXT NOT NULL,
                turn int NOT NULL,
                direction TEXT NOT NULL,
                seed TEXT NOT NULL,
                start_time TIMESTAMP WITH TIME ZONE NOT NULL,
                end_time TIMESTAMP WITH TIME ZONE
                );
        """)
       
        # Moves
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS Moves (
                umid TEXT PRIMARY KEY NOT NULL UNIQUE DEFAULT gen_random_uuid(),
                ugid TEXT NOT NULL,
                uuid TEXT NOT NULL,
                turn_number int NOT NULL,
                move TEXT NOT NULL
            );
        """)

    finally:
        await conn.commit()
        await conn.close()

async def add_foreign_keys():
    conn = await psycopg.AsyncConnection.connect("dbname=draw_master user=admin")
    try:
        cursor = conn.cursor()

        # Player FK
        await conn.execute("""
            ALTER TABLE Player
            ADD CONSTRAINT fk_player_versions
            FOREIGN KEY (uvid) REFERENCES Versions(uvid)
        """)

        # Lobbies FK
        await conn.execute("""
            ALTER TABLE Lobbies
            ADD CONSTRAINT fk_lobby_game
            FOREIGN KEY (ugid) REFERENCES Game(ugid);
        """)

        await conn.execute("""
            ALTER TABLE Lobbies
            ADD CONSTRAINT fk_lobby_version
            FOREIGN KEY (uvid) REFERENCES Versions(uvid);
        """)

        await conn.execute("""
            ALTER TABLE Lobbies
            ADD CONSTRAINT fk_lobby_player1
            FOREIGN KEY (uuid1) REFERENCES Player(uuid);
        """)

        await conn.execute("""
            ALTER TABLE Lobbies
            ADD CONSTRAINT fk_lobby_player2
            FOREIGN KEY (uuid2) REFERENCES Player(uuid);
        """)

        await conn.execute("""
            ALTER TABLE Lobbies
            ADD CONSTRAINT fk_lobby_player3
            FOREIGN KEY (uuid3) REFERENCES Player(uuid);
        """)

        await conn.execute("""
            ALTER TABLE Lobbies
            ADD CONSTRAINT fk_lobby_player4
            FOREIGN KEY (uuid4) REFERENCES Player(uuid);
        """)

        await conn.execute("""
            ALTER TABLE Lobbies
            ADD CONSTRAINT fk_lobby_player5
            FOREIGN KEY (uuid5) REFERENCES Player(uuid);
        """)

        await conn.execute("""
            ALTER TABLE Lobbies
            ADD CONSTRAINT fk_lobby_player6
            FOREIGN KEY (uuid6) REFERENCES Player(uuid);
        """)

        await conn.execute("""
            ALTER TABLE Lobbies
            ADD CONSTRAINT fk_lobby_player7
            FOREIGN KEY (uuid7) REFERENCES Player(uuid);
        """)

        await conn.execute("""
            ALTER TABLE Lobbies
            ADD CONSTRAINT fk_lobby_player8
            FOREIGN KEY (uuid8) REFERENCES Player(uuid);
        """)

        # Game FK
        await conn.execute("""
            ALTER TABLE Game
            ADD CONSTRAINT fk_game_lobby
            FOREIGN KEY (ulid) REFERENCES Lobbies(ulid)
        """)

        # Move FK
        await conn.execute("""
            ALTER TABLE Moves
            ADD CONSTRAINT fk_moves_game
            FOREIGN KEY (ugid) REFERENCES Game(ugid)
        """)

        await conn.execute("""
            ALTER TABLE Moves
            ADD CONSTRAINT fk_moves_player
            FOREIGN KEY (uuid) REFERENCES Player(uuid)
        """)

    finally:
        await conn.commit()
        await conn.close()

if __name__ == "__main__":
    asyncio.run(setup_tables())
    asyncio.run(add_foreign_keys())

