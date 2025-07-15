import psycopg
import asyncio
from security import verify_token

# Received:
#{
#   "path": "pre_lobby/create_new_lobby",
#   "size": 2-8,
#   "token": "hash",
#   "status": "public/private",
#   "uvid": "hash"
#}

# Return:
#{
#   "success": 200,
#   "ulid": [status, version, size, player_count]
#}

async def create_new_lobby(packet):
    pass

# Received:
#{
#   "path": "pre_lobby/join_lobby",
#   "ulid": "hash",
#   "token": "hash",
#}

# Return:
#{
#   "success": 200,
#   "ulid": [status, version, size, player_count]
#}

async def join_lobby(packet):
    pass

# Request:
#{
#   "path": "pre_lobby/list_lobbies",
#}

# Return:
#{
#   "success": 200,
#   "lobbies": {
#       "ulid_0": [status, version, size, player_count],
#       ...
#       "ulid_n": [status, version, size, player_count]
#   }
#}
async def list_lobbies(packet):
    pass

