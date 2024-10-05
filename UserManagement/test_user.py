import unittest
import json
from UserManagement.app import app, db, User  # Adjust import based on your app structure

class UserManagementTestCase(unittest.TestCase):

    def setUp(self):
        self.app = app
        self.client = self.app.test_client()
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app.config['JWT_SECRET_KEY'] = 'your_secret_key'

        with self.app.app_context():
            db.create_all()

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def test_register_user(self):
        response = self.client.post('/register', json={
            'username': 'testuser',
            'password': 'testpassword'
        })
        self.assertEqual(response.status_code, 201)
        self.assertIn(b'User registered successfully', response.data)

    def test_register_existing_user(self):
        self.client.post('/register', json={
            'username': 'testuser',
            'password': 'testpassword'
        })  # Register the user first

        response = self.client.post('/register', json={
            'username': 'testuser',
            'password': 'newpassword'
        })
        self.assertEqual(response.status_code, 409)
        self.assertIn(b'User already exists', response.data)

    def test_login_user(self):
        self.client.post('/register', json={
            'username': 'testuser',
            'password': 'testpassword'
        })  # Register the user first

        response = self.client.post('/login', json={
            'username': 'testuser',
            'password': 'testpassword'
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'access_token', response.data)

    def test_login_invalid_credentials(self):
        response = self.client.post('/login', json={
            'username': 'testuser',
            'password': 'wrongpassword'
        })
        self.assertEqual(response.status_code, 401)
        self.assertIn(b'Invalid credentials', response.data)

    def test_get_user(self):
        self.client.post('/register', json={
            'username': 'testuser',
            'password': 'testpassword'
        })  # Register the user first

        # Login to get the access token
        login_response = self.client.post('/login', json={
            'username': 'testuser',
            'password': 'testpassword'
        })
        access_token = json.loads(login_response.data)['access_token']

        # Use the access token to get user information
        response = self.client.get('/user', headers={
            'Authorization': f'Bearer {access_token}'
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'testuser', response.data)

    def test_get_user_without_token(self):
        """Test getting user information without a token."""
        response = self.client.get('/user')
        self.assertEqual(response.status_code, 401)  # Unauthorized

if __name__ == '__main__':
    unittest.main()
