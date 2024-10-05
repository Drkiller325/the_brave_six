# the_brave_six (an among us clone with a twist)
## Application Suitability
1. Why is this application relevant?
- Among us is one of the most popular games for some time now with its easy to understand dynamic mechanics that appear very appealing for many people and in this project I'll try to recreate this hopefully simple game system. 
2. Why does this game can use a microservice architecture?
- the microservice architecture offers a more loosely coupled design which can help develop and test every part of the project faster because of it's more independant structure.
- easier for scaling the game to manage the larger number of players in the game in the future using docker containers for example.
- In a microservice architecture, the failure of one service (like the login for example) doesn't necesarly crash the whole game.
## Service Boundaries
![image](https://github.com/user-attachments/assets/4ac87c99-6d19-43de-b81e-fd4cc2b4c128)

- service1: the firts microservice will be responsible of handeling all of the player's data(his login info, friends and stats) as well as user managment protocols.
- Service2: the secound service will handle the active game session amd all it's elements(movements, task progress, players status, chat and votes).
## Technology Stack and Communication Patterns
- User management(serverside):
  - python(RestFull API with flask)
  - mongoDB
- Client application:
  - C#
- Game session managment(serverside):
  - python(Restfull API with flask)
  - postgreSQL
  - Redis for chache
  - Web sockets
- API Gateway: raw C#
## Game Rules and end conditions
- the game will start like the ususal among us game with 6 heros and one disguised hero(the bad guy) and they will be trapped in a place until they discover the imposter but there's a catch! everyone will be able to kill anyone but the game will end if the hero kills the imposter or they finish the tasks and the imposter has to convince the other heros to kill eachother basically.
- end condition: imposter dead or tasks completed
## Data Management
here are some examples on how would some of the requests and thier responses look like in the different microservices in the game:
### 1. Authentication Service
- methode: POST
- Endpoint: /auth/register
- Request:
```json
  {
      "username": "player123",
      "password": "password"
  }
```
- Responses:
**201**
```json
  {
      "message": "User registered successfully",
      "user_id": "abc123",
      "token": "JWT-token-here"
  }
```
**400 Bad Request - Username taken**
```
{
    "error": "Username already exists"
}
```
- methode: POST
- Endpoint: /auth/login
-Request:
```json
{
    "username": "player123",
    "password": "securepassword"
}
```
- Responses:
**200**
```json
{
    "message": "Login successful",
    "token": "JWT-token-here"
}
```
**401 Unauthorized**
```
{
    "error": "Invalid credentials"
}
```
---

### 2. Game Session Service
- On Lobby Creation
- Response On success
```
 ws.send(JSON.stringify({
        type: 'lobby-created',
        lobbyId: lobbyId,
        message: `Lobby ${lobbyId} created successfully.`,
      }));
```
- On Gamestart
```
 if (parsedMessage.type === 'start-game') {
      broadcast(JSON.stringify({
        type: 'game-start',
        status: 1010, // Custom status code for game start
        message: `Game session started by ${playerId}`
      }));
```
---

### 3. Matchmaking Service
- through Websocket
- On User connection:
```
broadcast(JSON.stringify({
    type: 'player-join',
    playerId: playerId,
    message: `${playerId} joined the game.`
  }));
```
- On joining
- Request
```
wss.on('connection', function connection(ws) {
  //User unique ID
  const playerId = `player-${Math.floor(Math.random() * 1000)}`;
  players[playerId] = { id: playerId, connection: ws, status: 'connected' };
```
- On Success
```
broadcastToLobby(lobbyId, JSON.stringify({
          type: 'player-joined',
          playerId: playerId,
          message: `${playerId} joined the lobby.`,
        }));
```
- to track all user position and Tasks
```
broadcast(JSON.stringify({
        type: 'game-update',
        playerId: parsedMessage.playerId,
        position: parsedMessage.position
      }));
    }
```
- On leave
- Request
```
ws.on('close', function close(code, reason) {
    console.log(`${playerId} disconnected. Status code: ${code}, Reason: ${reason}`);
```
- On Success
```
broadcast(JSON.stringify({
      type: 'player-leave',
      playerId: playerId,
      message: `${playerId} left the game.`
    }));
```
---

### 4. Player Stats Service
- methode: GET
- Endpoint: /player/stats/{user_id}
- Response:
```json
{
    "user_id": "abc123",
    "games_played": 100,
    "games_won": 50,
    "tasks_completed": 200
}
```
---

### 5. Chat Service
- chat service will be using websockets
- On message
```
broadcastToLobby(lobbyId, JSON.stringify({
          type: 'lobby-chat',
          playerId: playerId,
          message: parsedMessage.message
        }));
```

## Deployment and Scaling
- We can scale the game in the future horizontly using Docker containers.
