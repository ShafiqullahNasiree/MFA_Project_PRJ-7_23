from flask import Flask, request, jsonify, send_file
import secrets
import time
import requests
import os

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

# ===========================================
# DEMO CONFIGURATION (Academic Project)
# ===========================================
# Note: Credentials are embedded for demo reproducibility.
# In production: use environment variables or a secrets manager.
TELEGRAM_TOKEN = "8599518592:AAHHY0WU2ZtK3i2W9bemkKDVZc1x3fUAIv8"
TELEGRAM_CHAT_ID = "1415538518"

# User credentials database (in production, use hashed passwords)
USERS = {
    "student": "password123"
}

# In-memory storage for OTPs
# Structure: {username: {"otp": "123456", "timestamp": 1234567890, "ip": "127.0.0.1", "used": False, "attempts": 0}}
otp_storage = {}

# Maximum OTP verification attempts before OTP is invalidated
MAX_OTP_ATTEMPTS = 3

# OTP expiration time in seconds
OTP_EXPIRATION_TIME = 60


# ===========================================
# HELPER FUNCTIONS
# ===========================================

def generate_otp():
    """
    Generates a cryptographically secure random 6-digit OTP (One-Time Password).
    Uses secrets module instead of random for security-sensitive applications.
    Returns a string of 6 digits (100000-999999).
    """
    return str(secrets.randbelow(900000) + 100000)


def send_telegram_message(message):
    """
    Sends a message to Telegram using the bot API.
    
    Security Note: This is an out-of-band channel - the OTP is sent
    through a different communication channel (Telegram) than the web
    interface, making it harder for attackers to intercept.
    
    Args:
        message (str): The message to send
        
    Returns:
        bool: True if message sent successfully, False otherwise
    """
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
    """
    Serves the login page.
    """
    login_path = os.path.join(FRONTEND_DIR, 'login.html')
    return send_file(login_path)


@app.route('/otp_page')
def otp_page():
    """
    Serves the OTP verification page.
    """
    otp_path = os.path.join(FRONTEND_DIR, 'otp.html')
    return send_file(otp_path)


@app.route('/login', methods=['POST'])
def login():
    """
    Handles user login and OTP generation.
    
    Security Flow:
    1. Verify username and password
    2. Generate a random 6-digit OTP
    3. Store OTP with timestamp and IP address
    4. Send OTP via Telegram (out-of-band channel)
    
    Returns:
        JSON response with success/error status
    """
    try:
        data = request.get_json()
        username = data.get('username', '').strip()
        password = data.get('password', '')
        
        # Security Check 1: Verify username exists
        if username not in USERS:
            return jsonify({
                "success": False,
                "message": "Invalid username or password"
            }), 401
        
        # Security Check 2: Verify password matches
        if USERS[username] != password:
            return jsonify({
                "success": False,
                "message": "Invalid username or password"
            }), 401
        
        # Generate OTP
        otp = generate_otp()
        
        # Get client IP address for security validation
        client_ip = request.remote_addr
        
        # Store OTP with metadata including attempts counter
        otp_storage[username] = {
            "otp": otp,
            "timestamp": time.time(),
            "ip": client_ip,
            "used": False,
            "attempts": 0  # Track failed verification attempts
        }
        
        # Send OTP via Telegram
        telegram_message = f"Your MFA OTP is: {otp}\n\nValid for 60 seconds.\nDo not share this code with anyone."
        telegram_sent = send_telegram_message(telegram_message)
        
        if not telegram_sent:
            # Clean up OTP storage if Telegram fails
            del otp_storage[username]
            return jsonify({
                "success": False,
                "message": "Failed to send OTP. Please try again."
            }), 500
        
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
    Verifies the OTP entered by the user.
    
    Security Checks (5 total):
    1. OTP exists for the username
    2. OTP has not been used before (prevents replay attacks)
    3. OTP has not expired (time-based security)
    4. IP address matches the login IP (prevents session hijacking)
    5. OTP code is correct
    
    Returns:
        JSON response with success/error status
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
        
        # Security Check 1: Verify OTP exists for this username
        if username not in otp_storage:
            return jsonify({
                "success": False,
                "message": "No OTP found. Please login again.",
                "force_relogin": True
            }), 401
        
        otp_data = otp_storage[username]
        
        # Security Check 2: Verify OTP has not been used
        if otp_data["used"]:
            return jsonify({
                "success": False,
                "message": "OTP has already been used. Please login again."
            }), 401
        
        # Security Check 3: Verify OTP has not expired
        current_time = time.time()
        time_elapsed = current_time - otp_data["timestamp"]
        
        if time_elapsed > OTP_EXPIRATION_TIME:
            del otp_storage[username]
            return jsonify({
                "success": False,
                "message": "OTP has expired. Please login again."
            }), 401
        
        # Security Check 4: Verify IP address matches (skip for localhost)
        client_ip = request.remote_addr
        
        stored_ip = otp_data["ip"]
        # Allow localhost variations to match
        localhost_ips = ['127.0.0.1', '::1', 'localhost']
        if not (stored_ip in localhost_ips and client_ip in localhost_ips):
            if stored_ip != client_ip:
                return jsonify({
                    "success": False,
                    "message": "IP address mismatch. Security violation detected."
                }), 403
        
        # Security Check 5: Verify OTP code is correct
        # Using constant-time comparison to prevent timing attacks
        otp_entered_clean = ''.join(filter(str.isdigit, otp_entered))
        
        if not secrets.compare_digest(otp_data["otp"], otp_entered_clean):
            # Increment attempt counter
            otp_data["attempts"] += 1
            
            # Check if max attempts exceeded - force re-login
            if otp_data["attempts"] >= MAX_OTP_ATTEMPTS:
                del otp_storage[username]
                return jsonify({
                    "success": False,
                    "message": "Too many wrong attempts. Please login again.",
                    "force_relogin": True
                }), 401
            
            # Still have attempts remaining
            remaining = MAX_OTP_ATTEMPTS - otp_data["attempts"]
            return jsonify({
                "success": False,
                "message": f"Invalid OTP. {remaining} attempt(s) remaining.",
                "force_relogin": False
            }), 401
        
        # All security checks passed!
        otp_data["used"] = True
        del otp_storage[username]
        
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
    # Run Flask server with debug mode off (production-ready setting)
    # In production, use a proper WSGI server like Gunicorn
    debug_mode = False
    app.run(host='0.0.0.0', port=5000, debug=debug_mode)

