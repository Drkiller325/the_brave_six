from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager, create_access_token, get_jwt_identity, jwt_required
from flask_sqlalchemy import SQLAlchemy

DATABASE_URI = 'sqlite:///users.db'
JWT_SECRET = 'your_secret_key'

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URI
app.config['JWT_SECRET_KEY'] = JWT_SECRET

db = SQLAlchemy(app)
jwt = JWTManager(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

@app.route('/')
def index():
    return 'Hello World!'


def get_request_data():
    return request.get_json()


def user_exists(username):
    return User.query.filter_by(username=username).first()


@app.route('/register', methods=['POST'])
def register_user():
    data = get_request_data()
    username = data['username']
    if user_exists(username):
        return jsonify({'message': 'User already exists'}), 409
    new_user = User(username=username, password=data['password'])
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'message': 'User registered successfully'}), 201


@app.route('/login', methods=['POST'])
def login_user():
    data = get_request_data()
    user = user_exists(data['username'])
    if user and user.password == data['password']:
        access_token = create_access_token(identity=user.username)
        db.session.refresh(user)
        db.session.commit()
        return jsonify(access_token=access_token), 200
    return jsonify({'message': 'Invalid credentials'}), 401

@app.route('/user', methods=['GET'])
@jwt_required()
def get_user():
    access_token = request.headers.get('Authorization')
    access_token = access_token.replace('Bearer ', '')
    if access_token:
        user = get_jwt_identity()
        if user:
            return jsonify({'username': user}), 200
    return jsonify({'message': "no user detected"}), 400

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5000, debug=True)
