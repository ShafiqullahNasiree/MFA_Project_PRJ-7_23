from flask import Flask, request, jsonify, send_file
import secrets
import time
import requests
import os
import sqlite3
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash

# Initialize Flask application
app = Flask(__name__)

# CORS Configuration - Allow all origins for demo simplicity
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

# Get the base directory (backend folder)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.join(os.path.dirname(BASE_DIR), 'frontend')
PROJECT_ROOT = os.path.dirname(BASE_DIR)
DATABASE_PATH = os.path.join(PROJECT_ROOT, 'mfa.db')

# Demo credentials (hardcoded for academic reproducibility)
TELEGRAM_TOKEN = "8599518592:AAHHY0WU2ZtK3i2W9bemkKDVZc1x3fUAIv8"
TELEGRAM_CHAT_ID = "1415538518"

MAX_OTP_ATTEMPTS = 3  # Max wrong attempts before OTP invalidated

OTP_EXPIRATION_TIME = 60  # OTP valid for 60 seconds


# ===========================================
# DATABASE FUNCTIONS
# ===========================================

def get_db_connection():
    """
    Creates and returns a connection to the SQLite database.
    Uses row_factory to return rows as dictionaries for easier access.
    """
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row  # Return rows as dictionaries
    return conn


def init_db():
    """Initialize database tables on first run."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Create users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            telegram_chat_id TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    ''')
    
    # Create otps table with foreign key to users
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS otps (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            otp_code TEXT NOT NULL,
            created_at TEXT NOT NULL,
            expires_at TEXT NOT NULL,
            client_ip TEXT NOT NULL,
            used INTEGER NOT NULL DEFAULT 0,
            attempts INTEGER NOT NULL DEFAULT 0,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    
    conn.commit()
    conn.close()
    print("[+] Database initialized successfully")


def seed_demo_user():
    """Create demo user (student/password123) if not exists."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Check if demo user already exists
    cursor.execute('SELECT id FROM users WHERE username = ?', ('student',))
    existing_user = cursor.fetchone()
    
    if not existing_user:
        # Hash the password
        password_hash = generate_password_hash('password123')
        created_at = datetime.utcnow().isoformat()
        
        # Insert demo user
        cursor.execute('''
            INSERT INTO users (username, password_hash, telegram_chat_id, created_at)
            VALUES (?, ?, ?, ?)
        ''', ('student', password_hash, TELEGRAM_CHAT_ID, created_at))
        
        conn.commit()
        print("[+] Demo user 'student' created successfully")
    else:
        print("[i] Demo user 'student' already exists")
    
    conn.close()


# ===========================================
# HELPER FUNCTIONS
# ===========================================

def generate_otp():
    """Generate cryptographically secure 6-digit OTP."""
    return str(secrets.randbelow(900000) + 100000)


def send_telegram_message(message):
    """Send OTP via Telegram (out-of-band channel)."""
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message
    }
    
    try:
        response = requests.post(url, json=payload, timeout=5)
        return response.status_code == 200
    except Exception as e:
        print(f"Error sending Telegram message: {e}")
        return False


# ===========================================
# ROUTES
# ===========================================

@app.route('/')
def index():
    """Serve login page."""
    login_path = os.path.join(FRONTEND_DIR, 'login.html')
    return send_file(login_path)


@app.route('/otp_page')
def otp_page():
    """Serve OTP verification page."""
    otp_path = os.path.join(FRONTEND_DIR, 'otp.html')
    return send_file(otp_path)


@app.route('/login', methods=['POST'])
def login():
    """Handle login and generate OTP (sent via Telegram)."""
    try:
        data = request.get_json()
        username = data.get('username', '').strip()
        password = data.get('password', '')
        
        # Connect to database
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Verify username exists
        cursor.execute('SELECT id, password_hash, telegram_chat_id FROM users WHERE username = ?', (username,))
        user = cursor.fetchone()
        
        if not user:
            conn.close()
            return jsonify({
                "success": False,
                "message": "Invalid username or password"
            }), 401
        
        # Verify password hash
        if not check_password_hash(user['password_hash'], password):
            conn.close()
            return jsonify({
                "success": False,
                "message": "Invalid username or password"
            }), 401
        
        # Generate OTP
        otp = generate_otp()
        
        # Get client IP for binding
        client_ip = request.remote_addr
        
        # OTP expires after 60 seconds
        created_at = datetime.utcnow()
        expires_at = created_at + timedelta(seconds=OTP_EXPIRATION_TIME)
        
        # Invalidate any existing OTPs for this user
        cursor.execute('UPDATE otps SET used = 1 WHERE user_id = ? AND used = 0', (user['id'],))
        
        # Store OTP in database
        cursor.execute('''
            INSERT INTO otps (user_id, otp_code, created_at, expires_at, client_ip, used, attempts)
            VALUES (?, ?, ?, ?, ?, 0, 0)
        ''', (user['id'], otp, created_at.isoformat(), expires_at.isoformat(), client_ip))
        
        conn.commit()
        
        # Send OTP via Telegram
        telegram_message = f"Your MFA OTP is: {otp}\n\nValid for 60 seconds.\nDo not share this code with anyone."
        telegram_sent = send_telegram_message(telegram_message)
        
        if not telegram_sent:
            # Clean up OTP from database if Telegram fails
            cursor.execute('DELETE FROM otps WHERE user_id = ? AND otp_code = ?', (user['id'], otp))
            conn.commit()
            conn.close()
            return jsonify({
                "success": False,
                "message": "Failed to send OTP. Please try again."
            }), 500
        
        conn.close()
        
        return jsonify({
            "success": True,
            "message": "OTP sent to your Telegram. Please check your messages."
        }), 200
        
    except Exception as e:
        print(f"Login error: {e}")
        return jsonify({
            "success": False,
            "message": "An error occurred. Please try again."
        }), 500


@app.route('/verify_otp', methods=['POST', 'OPTIONS'])
def verify_otp():
    """
    Verify OTP with 5 security checks:
    1. OTP exists
    2. Not already used (replay prevention)
    3. Not expired (60 second limit)
    4. IP matches login IP
    5. Code is correct (max 3 attempts)
    """
    # Handle CORS preflight
    if request.method == 'OPTIONS':
        return jsonify({}), 200
    
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                "success": False,
                "message": "Invalid request. No data received."
            }), 400
        
        username = data.get('username', '').strip()
        otp_entered = data.get('otp', '').strip()
        
        # Connect to database
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get user by username
        cursor.execute('SELECT id FROM users WHERE username = ?', (username,))
        user = cursor.fetchone()
        
        if not user:
            conn.close()
            return jsonify({
                "success": False,
                "message": "No OTP found. Please login again.",
                "force_relogin": True
            }), 401
        
        # Check 1: OTP exists
        cursor.execute('''
            SELECT id, otp_code, created_at, expires_at, client_ip, used, attempts
            FROM otps
            WHERE user_id = ?
            ORDER BY created_at DESC
            LIMIT 1
        ''', (user['id'],))
        
        otp_data = cursor.fetchone()
        
        if not otp_data:
            conn.close()
            return jsonify({
                "success": False,
                "message": "No OTP found. Please login again.",
                "force_relogin": True
            }), 401
        
        # Check 2: OTP not already used (replay prevention)
        if otp_data['used'] == 1:
            conn.close()
            return jsonify({
                "success": False,
                "message": "OTP has already been used. Please login again."
            }), 401
        
        # Check 3: OTP not expired (60 second limit)
        expires_at = datetime.fromisoformat(otp_data['expires_at'])
        current_time = datetime.utcnow()
        
        if current_time > expires_at:
            # Mark as used and delete expired OTP
            cursor.execute('UPDATE otps SET used = 1 WHERE id = ?', (otp_data['id'],))
            conn.commit()
            conn.close()
            return jsonify({
                "success": False,
                "message": "OTP has expired. Please login again."
            }), 401
        
        # Check 4: IP address matches (prevents hijacking)
        client_ip = request.remote_addr
        stored_ip = otp_data['client_ip']
        
        # Allow localhost variations to match
        localhost_ips = ['127.0.0.1', '::1', 'localhost']
        if not (stored_ip in localhost_ips and client_ip in localhost_ips):
            if stored_ip != client_ip:
                conn.close()
                return jsonify({
                    "success": False,
                    "message": "IP address mismatch. Security violation detected."
                }), 403
        
        # Check 5: OTP code is correct (constant-time comparison)
        otp_entered_clean = ''.join(filter(str.isdigit, otp_entered))
        
        if not secrets.compare_digest(otp_data['otp_code'], otp_entered_clean):
            # Increment attempt counter
            new_attempts = otp_data['attempts'] + 1
            
            # Max attempts exceeded - invalidate OTP
            if new_attempts >= MAX_OTP_ATTEMPTS:
                cursor.execute('UPDATE otps SET used = 1, attempts = ? WHERE id = ?', 
                             (new_attempts, otp_data['id']))
                conn.commit()
                conn.close()
                return jsonify({
                    "success": False,
                    "message": "Too many wrong attempts. Please login again.",
                    "force_relogin": True
                }), 401
            
            # Still have attempts remaining
            cursor.execute('UPDATE otps SET attempts = ? WHERE id = ?', (new_attempts, otp_data['id']))
            conn.commit()
            conn.close()
            
            remaining = MAX_OTP_ATTEMPTS - new_attempts
            return jsonify({
                "success": False,
                "message": f"Invalid OTP. {remaining} attempt(s) remaining.",
                "force_relogin": False
            }), 401
        
        # All security checks passed!
        cursor.execute('UPDATE otps SET used = 1 WHERE id = ?', (otp_data['id'],))
        conn.commit()
        conn.close()
        
        return jsonify({
            "success": True,
            "message": "Authentication successful! Access granted."
        }), 200
        
    except Exception as e:
        print(f"OTP verification error: {e}")
        return jsonify({
            "success": False,
            "message": "An error occurred. Please try again."
        }), 500


if __name__ == '__main__':
    # Initialize database and seed demo user on startup
    print("[*] Initializing MFA system...")
    init_db()
    seed_demo_user()
    print("[+] System ready!")
    print("[i] Database location:", DATABASE_PATH)
    print()
    
    # Run Flask server with debug mode off (production-ready setting)
    # In production, use a proper WSGI server like Gunicorn
    debug_mode = False
    app.run(host='0.0.0.0', port=5000, debug=debug_mode)

