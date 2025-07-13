# DRAW - JULY 2025

IMPORTANT:

> ALL states layer 1 and greater can timeout to **MS-MAIN-MENU** if server can't be reached after continuously trying for ~3 minutes
> ALL states layers 1-4 can press a home button to return to **MS-MAIN-MENU**, requiring a log-out from **MS-PLAY-ONLINE**
> ALL states layer 4 and greater must send token to server to prove identity
> ALL states layers 5-7 have a back button to go back to **MS-PLAY-ONLINE** (**MS-IN-GAME** uses a "leave game" button instead)

## LAYER 0: OFFLINE

### MS-MAIN-MENU
user presses "play online"
- goes to MS-SELECT-SERVER

## LAYER 1: CONNECT TO SERVER

### MS-SELECT-SERVER (L1)

user can edit default server URL (e.g. "www.draw.com") at their own risk
user presses "connect" to submit a *connection request*

- *connection success*	-> **MS-SELECT-AUTH**
- *client unsupported version failure*	-> **MS-MAIN-MENU** with a GUI warning
- *NO RESPONSE* -> **MS-SELECT-SERVER** with a GUI warning

SERVER HANDSHAKE PACKETS

*Connection request*
- SEND: client version #
- RECEIVE: Connection success
- RECEIVE: *Client unsupported version failure*
		
## LAYERS 2: USER AUTH

### MS-SELECT-AUTH (L2)

user can press three buttons
- "log in" -> goes to **MS-LOGIN**
- End Point -> url/account/login
```SQL
SELECT username, password FROM player WHERE username='input' AND password='input';
```
To verify user info
- "new account" -> goes to **MS-NEW-ACCOUNT**
- End Point -> url/account/create_account
```SQL
INSERT INTO player username, password VALUES(input, input);
```
- "play anonymously" -> goes to **MS-ANON-ACCOUNT**
- End Point url/account/guest_account
```SQL
INSERT INTO player username, password VALUES(guestx, hash);
```

#### IMPORTANT: ALL layer 3 states can receive these packets: 

*client auth success* -> **MS-PLAY-ONLINE**
*client unsupported version failure* -> **MS-MAIN-MENU** with a GUI warning

## Layer 3: LOGIN

### MS-LOGIN (L3)

user presses "log in" to submit a *client auth request* with *login* parameter

*client auth invalid credentials* -> **MS-LOGIN** with a GUI warning
*client duplicate login failure* -> **MS-MAIN-MENU** with a GUI warning

### MS-NEW-ACCOUNT (L3)

user presses "create new account" to submit a *client auth request* with *signup* parameter

*client auth invalid credentials* -> **MS-NEW-ACCOUNT** with a GUI warning

### MS-ANON-ACCOUNT (L3)

user presses "I'm sure" to submit a *client auth request* with *anon* parameter (no UN/PW)


#### USER AUTH PACKETS

NOTE: These packet will need to change to include a single additional parameter for use in sockets

*Client auth request*
```JSON
{
    "version": 0,
    "username": text,
    "password": hash
}
```

*Client auth success* response
```JSON
{
    "token": hash
}
```

*Client unsupported version failure* response
```JSON
{
    "supported_version": 0
}
```

*Client auth invalid credentials* response
```JSON
{
    "error": 401
}
```

*Client duplicate login failure* response
```JSON
{
    "error": 403,
    "status": "already logged in"
}
```
*Client logout request* (technically a layer 4 packet since it needs token) [Techincally not required with sockets]
```JSON
{
    "token": 0
}

```

*Client logout success*

- specifies the backend successfully logged out the user

*Client logout failure* Solved with sockets -> constant connection immediately tell when it is disconnected
- No packets required front end handling 

## LAYERS 4-6: JOINABLE LOBBIES

### MS-PLAY-ONLINE (L4)

user can press three buttons

- "find public lobbies"	-> **MS-PUBLIC-LOBBIES**
- "join lobby with a code"	-> **MS-JOIN-LOBBY-ID**
- "new lobby" -> **MS-NEW-LOBBY**
		
OR user can press the home button to submit a *client logout request*

*client logout success*	-> **MS-MAIN-MENU**
*client logout failure*	-> **MS-MAIN-MENU** with a GUI warning

### MS-NEW-LOBBY (L5)

user presses "create lobby" to submit a *lobby creation request*,

*lobby join success* -> **MS-IN-LOBBY**
*lobby creation failure* -> **MS-PLAY-ONLINE**

### MS-JOIN-LOBBY-ID (L5)

user presses "join lobby" to submit a *lobby join request*,

*lobby join success* -> **MS-IN-LOBBY**
*lobby join ... failure* -> **MS-PLAY-ONLINE** with respective GUI warning

### MS-PUBLIC-LOBBIES (L5)

client repeatedly sends a *lobby public list request* to update their GUI

*lobby public list success*	-> **MS-PUBLIC-LOBBIES** with updated GUI
*lobby public list failure*	-> **MS-PUBLIC-LOBBIES** but shows a small warning somewhere
	
THEN user presses "join lobby" (when viewing one) to submit a *lobby join request* (via the lobby ID),
	
*lobby join success* -> **MS-IN-LOBBY**
*lobby join ... failure"* -> **MS-PUBLIC-LOBBIES** with respective GUI warning


#### LOBBY CREATION PACKETS

*Lobby creation request*
```JSON
{
    "size": 2,
    "type": public
}
```

*Lobby creation failure* response
- specifies a lobby creation failure (and no more; if client is out-of-date, they wouldn't be able to log in)


#### LOBBY JOIN PACKETS

*Lobby join request*
- End Point url/lobby/join
```JSON
{
    "ULID": 0
}
```

*Lobby join success* response
```SQL
UPDATE Lobby SET PUID=input WHERE ULID=input;
```

```JSON
{
    "ULID": 0,
    "Size": 8,
    "Players": [player_1, ..., player_8]
}

```

*Lobby join version failure* response
```JSON
{
    "error": 403,
    "Version": 0
}
```

*Lobby join in-session failure* response
```JSON
{
    "error": 403,
    "Message": "game in session"
}
```

*Lobby join DNE failure* response
```JSON
{
    "error": 404
}
```

#### LOBBY SYNC PACKETS

*Lobby sync success* response -> send this upon update of lobby
```JSON
{
    "size": 6,
    "players": [player_1, ..., player_6]
}
```

#### LOBBY LEAVE PACKETS

*Lobby leave request*
- the user wants to leave their current lobby
- End Point url/lobby/leave
GET REQUEST -> No explicit packet

*Lobby leave success* response
- specifies the user has successfully left their lobby
```JSON
{
    "success": 200
}
```

#### LOBBY PUBLIC LIST PACKETS

*Lobby public list request*
- the client wants the current list of active public lobbies
GET REQUEST:

```SQL
SELECT ulid, version, status, size, Players.Username, FROM Lobbies INNER JOIN Players ON Lobbies.UUID=Players.UUID;
```

*Lobby public list success* response
```JSON
{
    "ULID": hash,
    "Version": "0",
    "Status": "waiting",
    "Size": 2,
    "Players": ["player_1", "player_2"]
}
```

### MS-IN-LOBBY (L6) THREADED LOBBIES HERE DOWN

host client sends *start game request* and server approves or denies (2-max players are allowed),
```JSON
{
    "token": hash,
    "message": "start_game"
}
```
server responds with a *start game success*
```JSON
{
    "success": 200
}
```

*start game success* -> **MS-IN-GAME**

## LAYERS 7-8: ACTIVE LOBBIES

### MS-IN-GAME (L7)

game logic
server accumulates game move history in db for stats
users can send a *lobby leave request* at any time, including the host

### MS-GAME-OVER (L8)

user is shown game stats accumulated in-game, and can press two buttons

- "play again" -> **MS-IN-LOBBY**
- "leave lobby" -> **MS-PLAY-ONLINE**
	
