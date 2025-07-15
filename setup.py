import psycopg
import asyncio

async def setup_tables():
    conn = await psycopg.AsyncConnection.connect("dbname=draw_master user=admin")
    try:
        cursor = conn.cursor()
       
        await conn.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto;")

        await conn.execute("GRANT SELECT ON ALL TABLES IN SCHEMA public TO player")

        # Version
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS Version (
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
                token TEXT UNIQUE
                );
        """)
       
        # Lobby
        await cursor.execute("""
            CREATE TABLE IF NOT EXISTS Lobby (
                ulid TEXT PRIMARY KEY NOT NULL UNIQUE DEFAULT gen_random_uuid(),
                ugid TEXT,
                uvid TEXT NOT NULL,
                status TEXT NOT NULL,
                type TEXT NOT NULL,
                size int NOT NULL
                );
        """)

        # Lobby Members
        await cursor.execute("""
            CREATE TABLE IF NOT EXISTS Lobby_member (
                ulmid TEXT PRIMARY KEY NOT NULL UNIQUE DEFAULT gen_random_uuid(),
                ulid TEXT NOT NULL,
                uuid TEXT NOT NULL,
                slot_number int NOT NULL
                );
        """)
       
        # Game
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS Game (
                ugid TEXT PRIMARY KEY NOT NULL UNIQUE DEFAULT gen_random_uuid(),
                ulid TEXT NOT NULL,
                seed TEXT NOT NULL,
                start_time TIMESTAMP NOT NULL,
                end_time TIMESTAMP
                );
        """)

        # Initial_game_order
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS Initial_game_order (
                uigoid TEXT PRIMARY KEY NOT NULL UNIQUE DEFAULT gen_random_uuid(),
                ugid TEXT NOT NULL,
                uuid TEXT NOT NULL,
                position int NOT NULL
            );
        """)

        # Game Leaderboard
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS Game_leaderboard (
                uglid TEXT PRIMARY KEY NOT NULL UNIQUE DEFAULT gen_random_uuid(),
                ugid TEXT NOT NULL,
                uuid TEXT NOT NULL,
                podium_position TEXT NOT NULL
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
            FOREIGN KEY (uvid) REFERENCES Version(uvid)
        """)

        # Lobby FK
        await conn.execute("""
            ALTER TABLE Lobby
            ADD CONSTRAINT fk_lobby_game
            FOREIGN KEY (ugid) REFERENCES Game(ugid);
        """)

        await conn.execute("""
            ALTER TABLE Lobby
            ADD CONSTRAINT fk_lobby_version
            FOREIGN KEY (uvid) REFERENCES Version(uvid);
        """)

        # Lobby_members FK
        await conn.execute("""
            ALTER TABLE Lobby_member
            ADD CONSTRAINT fk_lobbymember_lobby
            FOREIGN KEY (ulid) REFERENCES Lobby(ulid)
        """)

        await conn.execute("""
            ALTER TABLE Lobby_member
            ADD CONSTRAINT fk_lobbymemeber_player
            FOREIGN KEY (uuid) REFERENCES Player(uuid)
        """)

        # Game FK
        await conn.execute("""
            ALTER TABLE Game
            ADD CONSTRAINT fk_game_lobby
            FOREIGN KEY (ulid) REFERENCES Lobby(ulid)
        """)

        # Game_inital_position FK
        await conn.execute("""
            ALTER TABLE Initial_game_order
            ADD CONSTRAINT fk_gameinitialposition_game
            FOREIGN KEY (ugid) REFERENCES Game(ugid)
        """)

        await conn.execute("""
            ALTER TABLE Initial_game_order
            ADD CONSTRAINT fk_gameinitialpositions_player
            FOREIGN KEY (uuid) REFERENCES Player(uuid)
        """)

        # Game_leaderboard FK
        await conn.execute("""
            ALTER TABLE Game_leaderboard
            ADD CONSTRAINT fk_gameleaderboard_game
            FOREIGN KEY (ugid) REFERENCES Game(ugid)
        """)

        await conn.execute("""
            ALTER TABLE Game_leaderboard
            ADD CONSTRAINT fk_gameleaderboard_player
            FOREIGN KEY (uuid) REFERENCES Player(uuid)
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

