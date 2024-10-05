# app/app.py
from flask import Flask, jsonify, request
from flask_socketio import SocketIO, emit
from flask import send_from_directory
from pymongo import MongoClient  # Import MongoDB client


app = Flask(__name__)
socketio = SocketIO(app)

# Connect to MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['game_sessions_db']  # Database
sessions_collection = db['sessions']  # Collection


# Route to serve the HTML client
@app.route('/')
def index():
    return send_from_directory('', 'client.html')


# Create a new game session and save it to MongoDB
@app.route('/create_session', methods=['POST'])
def create_session():
    session_id = request.json.get('session_id')

    # Check if the session already exists in the database
    if sessions_collection.find_one({"session_id": session_id}):
        return jsonify({"error": "Session already exists"}), 400

    # Insert new session into the database
    new_session = {"session_id": session_id, "players": []}
    sessions_collection.insert_one(new_session)

    return jsonify({"message": "Session created", "session_id": session_id}), 201


# Socket event to join a game session
@socketio.on('join_session')
def join_session(data):
    session_id = data['session_id']
    player_id = data['player_id']

    # Check if the session exists in the database
    session = sessions_collection.find_one({"session_id": session_id})

    if session:
        # Add player to the session
        sessions_collection.update_one(
            {"session_id": session_id},
            {"$push": {"players": player_id}}
        )
        updated_session = sessions_collection.find_one({"session_id": session_id})
        emit('session_update', updated_session, broadcast=True)
    else:
        emit('error', {'error': 'Session not found'})


# Socket event to leave a game session
@socketio.on('leave_session')
def leave_session(data):
    session_id = data['session_id']
    player_id = data['player_id']

    # Check if the session exists in the database
    session = sessions_collection.find_one({"session_id": session_id})

    if session and player_id in session['players']:
        # Remove player from the session
        sessions_collection.update_one(
            {"session_id": session_id},
            {"$pull": {"players": player_id}}
        )
        updated_session = sessions_collection.find_one({"session_id": session_id})
        emit('session_update', updated_session, broadcast=True)
    else:
        emit('error', {'error': 'Session not found or player not in session'})


# Socket event to retrieve all active sessions
@socketio.on('get_sessions')
def get_sessions():
    sessions = list(sessions_collection.find({}, {"_id": 0}))  # Get all sessions, hide MongoDB _id field
    emit('active_sessions', sessions)


if __name__ == '__main__':
    socketio.run(app, debug=True, allow_unsafe_werkzeug=True, host='0.0.0.0')
