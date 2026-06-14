"""
Authentication Module
Handles user registration, login, and JWT token management.
"""

from flask import Blueprint, request, jsonify, current_app
from datetime import datetime, timedelta
from functools import wraps
import bcrypt
import jwt
import logging

logger = logging.getLogger(__name__)

auth_bp = Blueprint('auth', __name__)


# ─── Helpers ────────────────────────────────────────────────────────────────

def hash_password(password: str) -> str:
    """Hash a password using bcrypt"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


def verify_password(password: str, password_hash: str) -> bool:
    """Verify a password against its hash"""
    return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))


def generate_token(user_id: int, username: str) -> str:
    """Generate a JWT token"""
    payload = {
        'user_id': user_id,
        'username': username,
        'exp': datetime.utcnow() + timedelta(hours=24),
        'iat': datetime.utcnow()
    }
    return jwt.encode(payload, current_app.config['SECRET_KEY'], algorithm='HS256')


def token_required(f):
    """Decorator to protect routes with JWT authentication"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        # Get token from Authorization header
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]

        if not token:
            return jsonify({'error': 'Token is missing'}), 401

        try:
            data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
            current_user_id = data['user_id']
            current_username = data['username']
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token has expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Invalid token'}), 401

        return f(current_user_id, current_username, *args, **kwargs)

    return decorated


# ─── Routes ─────────────────────────────────────────────────────────────────

@auth_bp.route('/register', methods=['POST'])
def register():
    """
    POST /api/auth/register
    Body: { "username": "...", "email": "...", "password": "..." }
    """
    data = request.get_json()

    # Validate input
    if not data:
        return jsonify({'error': 'No data provided'}), 400

    username = data.get('username', '').strip()
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')

    if not username or not email or not password:
        return jsonify({'error': 'Username, email, and password are required'}), 400

    if len(username) < 3 or len(username) > 80:
        return jsonify({'error': 'Username must be between 3 and 80 characters'}), 400

    if len(password) < 6:
        return jsonify({'error': 'Password must be at least 6 characters'}), 400

    if '@' not in email:
        return jsonify({'error': 'Invalid email address'}), 400

    db = current_app.db

    # Check if username or email already exists
    existing_user = db.get_user(username)
    if existing_user:
        return jsonify({'error': 'Username already taken'}), 409

    # Create user
    try:
        password_hash = hash_password(password)
        user = db.add_user(username=username, email=email, password_hash=password_hash)
        token = generate_token(user.id, user.username)

        logger.info(f"New user registered: {username}")
        return jsonify({
            'message': 'Registration successful',
            'token': token,
            'user': {'id': user.id, 'username': user.username, 'email': user.email}
        }), 201

    except Exception as e:
        logger.error(f"Registration error: {e}")
        return jsonify({'error': 'Registration failed'}), 500


@auth_bp.route('/login', methods=['POST'])
def login():
    """
    POST /api/auth/login
    Body: { "username": "...", "password": "..." }
    """
    data = request.get_json()

    if not data:
        return jsonify({'error': 'No data provided'}), 400

    username = data.get('username', '').strip()
    password = data.get('password', '')

    if not username or not password:
        return jsonify({'error': 'Username and password are required'}), 400

    db = current_app.db
    user = db.get_user(username)

    if not user or not verify_password(password, user.password_hash):
        return jsonify({'error': 'Invalid username or password'}), 401

    if not user.is_active:
        return jsonify({'error': 'Account is disabled'}), 403

    token = generate_token(user.id, user.username)
    logger.info(f"User logged in: {username}")

    return jsonify({
        'message': 'Login successful',
        'token': token,
        'user': {'id': user.id, 'username': user.username, 'email': user.email}
    }), 200


@auth_bp.route('/me', methods=['GET'])
@token_required
def get_me(current_user_id, current_username):
    """
    GET /api/auth/me
    Returns current authenticated user info.
    """
    db = current_app.db
    user = db.get_user(current_username)

    if not user:
        return jsonify({'error': 'User not found'}), 404

    return jsonify({'user': user.to_dict()}), 200
