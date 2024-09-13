# the_brave_six (an among us clone with a twist)
## Application Suitability
1. Why is this application relevant?
- Among us is one of the most popular games for some time now with its easy to understand dynamic mechanics that appear very appealing for many people and in this project I'll try to recreate this hopefully simple game system. 
2. Why does this game can use a microservice architecture?
- the microservice architecture offers a more loosely coupled design which can help develop and test every part of the project faster because of it's more independant structure.
- easier for scaling the game to manage the larger number of players in the game in the future using docker containers for example.
- In a microservice architecture, the failure of one service (like the login for example) doesn't necesarly crash the whole game.
## Service Boundaries
![image](https://github.com/user-attachments/assets/a3e1a487-fe4c-448a-a12a-8a145696a9a4)
- service1: the firts microservice will be responsible of handeling all of the player's data(his login info, friends and stats) as well as user managment protocols.
- Service2: the secound service will handle the active game session amd all it's elements(movements, task progress, players status, chat and votes).
## Technology Stack and Communication Patterns
- User management(serverside):
  - python(RestFull API with flask)
  - mongoDB
- Game logic:
  - C#
- Game session managment(serverside):
  - python(Restfull API with flask)
  - postgreSQL
  - Redis for chache
  - Web sockets
- API Gateway: Restfull API and gRPC for Service descovery
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
### 2. Game Session Service
- methode: POST
- Endpoint: /game/create
- Request:
```json
{
    "user_id": "abc123",
    "game_settings": {
        "max_players": 10,
        "map": "space_station"
    }
}
```
- Responses:
**201 Game Created**
```json
{
    "message": "Game created",
    "game_id": "game567",
    "lobby_code": "XYZ123"
}
```
**400 Bad Request**
```
{
    "error": "Invalid game settings"
}
```
- Methode: POST 
- Endpoint: /game/join
- Request:
```json
{
    "user_id": "def456",
    "lobby_code": "XYZ123"
}
```
- Responses:
**200 OK**
```json
{
    "message": "Joined lobby",
    "game_id": "game567",
    "current_players": 5,
    "max_players": 10
}
```
**404 Not Found - Lobby code invalid**
```
{
    "error": "Lobby not found"
}
```
### 3. Matchmaking Service
- Methode: GET
- Endpoint: /matchmaking/find
- Request:
```json
{
    "user_id": "abc123"
}
```
- Responses:
**200 OK**
```json
{
    "message": "Searching for game",
    "estimated_wait_time": "20s"
}
```
**500 Internal Server Error**
```
{
    "error": "Failed to initiate matchmaking"
}
```
- Methode: GET 
- Endpoint: /matchmaking/status
- Responses:
**200 OK**
```json
{
    "status": "Found match",
    "game_id": "game567",
    "lobby_code": "XYZ123"
}
```
**404 Not Found - No matches found**
```
{
    "error": "No match found yet"
}
```
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
### 5. Chat Service
- methode:POST
- Endpoint /chat/send
- Request:
```json
{
    "user_id": "abc123",
    "game_id": "game567",
    "message": "Hello everyone!"
}
```
- Response:
```json
{
    "status": "Message sent"
}
```
