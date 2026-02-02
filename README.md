# Multi-Factor Authentication (MFA) System

## Overview

This is a complete Multi-Factor Authentication (MFA) system built for a System Security course project (PRJ-7_23). The system implements a two-factor authentication flow where users must provide both a password and a time-limited One-Time Password (OTP) sent via Telegram.

> **Demo Note:** This is a controlled academic demo. Telegram credentials are embedded in the code for reproducibility and ease of testing.

> **Production Note:** In a production environment, credentials must be externalized via environment variables or a secrets manager.

The system demonstrates key security principles including:
- Out-of-band authentication (OTP sent via different channel)
- Time-based OTP expiration (60 seconds)
- IP address validation
- Replay attack prevention
- Rate limiting (max 3 OTP attempts)
- Cryptographically secure OTP generation

### Database Architecture

The system uses **SQLite** as a lightweight, file-based relational database to store user credentials and OTP records. This upgrade from in-memory storage provides:

- **Persistent storage**: Data survives server restarts
- **ACID compliance**: Atomic, consistent, isolated, and durable transactions
- **Password hashing**: Passwords stored as hashes using werkzeug.security (scrypt/pbkdf2)
- **Relational integrity**: Foreign key constraints between users and OTPs

**Database Schema**:

**`users` table**:
- `id` - Primary key (auto-increment)
- `username` - Unique username
- `password_hash` - Hashed password using werkzeug
- `telegram_chat_id` - User's Telegram chat ID for OTP delivery
- `created_at` - Account creation timestamp

**`otps` table**:
- `id` - Primary key (auto-increment)
- `user_id` - Foreign key to users table
- `otp_code` - The 6-digit OTP code
- `created_at` - OTP generation timestamp
- `expires_at` - Expiration timestamp (created_at + 60 seconds)
- `client_ip` - IP address from login request
- `used` - Boolean flag (0 = unused, 1 = used)
- `attempts` - Failed verification attempts counter

The database is automatically created at `mfa.db` in the project root on first run. A demo user (`student/password123`) is seeded automatically with a hashed password.

**How the Database Supports MFA Security**:

1. **User Authentication**: Login queries the `users` table and verifies the password against the stored hash using constant-time comparison
2. **OTP Lifecycle**: Each OTP is inserted into the `otps` table with expiration timestamp and IP binding
3. **Security Checks**: All 5 security checks (existence, reuse, expiration, IP match, correctness) query the database
4. **Attempt Limiting**: Failed attempts increment the `attempts` column; after 3 attempts, OTP is marked as used
5. **Cleanup**: Used OTPs remain in database for audit purposes but are marked with `used = 1`

## Security Features

### 1. Multi-Factor Authentication (MFA)
The system requires two factors for authentication:
- **Factor 1**: Something you know (password)
- **Factor 2**: Something you have (access to Telegram account)

### 2. Out-of-Band Communication
OTPs are sent via Telegram, which is a separate communication channel from the web interface. This makes it significantly harder for attackers to intercept both the password and OTP through the same channel.

### 3. OTP Expiration
Each OTP is valid for only 60 seconds. This time-based security ensures that even if an OTP is intercepted, it becomes useless after a short period.

### 4. IP Address Validation
The system validates that the OTP verification request comes from the same IP address as the login request. This prevents session hijacking attacks where an attacker steals a session cookie but cannot use it from a different location.

### 5. Replay Attack Prevention
Each OTP can only be used once. After successful verification, the OTP is marked as used and cannot be reused, preventing replay attacks.

## Setup Instructions

### Prerequisites
- Python 3.11 or higher
- Telegram account with bot token and chat ID
- Internet connection for Telegram API

### Local Installation

1. **Clone or download the project**
   ```bash
   cd MFA_Project
   ```

2. **Install Python dependencies**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

3. **Run the Flask application**
   ```bash
   python app.py
   ```
   
   > **Note**: The SQLite database (`mfa.db`) will be automatically created in the project root on first run, and a demo user will be seeded with hashed credentials.

5. **Access the application**
   - Open your browser and navigate to `http://localhost:5000`
   - The login page should be displayed

### Docker Deployment

1. **Build the Docker image**
   ```bash
   docker build -t mfa-system ./backend
   ```

2. **Run the container**
   ```bash
   docker run -p 5000:5000 mfa-system
   ```

3. **Access the application**
   - Open your browser and navigate to `http://localhost:5000`

## Usage

### Demo Credentials
- **Username**: `student`
- **Password**: `password123`

### Authentication Flow

1. **Login Page** (`/`)
   - Enter username and password
   - Click "Login"
   - System validates credentials

2. **OTP Generation**
   - Upon successful password verification, a 6-digit OTP is generated
   - OTP is sent to your Telegram account
   - OTP is stored with timestamp and IP address

3. **OTP Verification Page** (`/otp_page`)
   - Check your Telegram for the OTP
   - Enter the 6-digit OTP
   - Click "Verify OTP"
   - System performs 5 security checks:
     - OTP exists for username
     - OTP has not been used
     - OTP has not expired (60 seconds)
     - IP address matches login IP
     - OTP code is correct

4. **Success**
   - If all checks pass, authentication is successful
   - Access is granted to the system

## Project Structure

```
MFA_Project/
├── backend/
│   ├── app.py              # Flask application with routes and security logic
│   ├── requirements.txt    # Python dependencies
│   └── Dockerfile          # Docker configuration
├── frontend/
│   ├── login.html          # Login page with form
│   └── otp.html            # OTP verification page
├── README.md               # This documentation
└── .gitignore             # Git ignore rules
```

## Security Analysis

### Strengths

1. **Two-Factor Authentication**: Requires both password and OTP
2. **Out-of-Band Channel**: OTP sent via Telegram (separate from web)
3. **Time-Limited OTPs**: 60-second expiration reduces attack window
4. **IP Validation**: Prevents session hijacking from different locations
5. **One-Time Use**: OTPs cannot be reused (prevents replay attacks)
6. **Error Handling**: Graceful error handling prevents information leakage
7. **Cryptographically Secure OTP**: Uses Python's `secrets` module instead of `random`
8. **Password Hashing**: Passwords stored as hashes using werkzeug.security
9. **Rate Limiting**: Max 3 OTP attempts per login prevents brute force
10. **Persistent Storage**: SQLite database with ACID compliance
11. **Relational Integrity**: Foreign key constraints ensure data consistency
12. **CORS Configuration**: Open to all origins for demo simplicity; in production this would be restricted

### Limitations and Considerations

1. **Single User**: Only one user configured for demo purposes
   - **Production Solution**: Implement user registration and management system

2. **Development Server**: Uses Flask development server
   - **Production Solution**: Use Gunicorn or uWSGI with proper configuration

3. **No HTTPS**: HTTP only (credentials transmitted in plain text over network)
   - **Production Solution**: Deploy behind HTTPS/TLS reverse proxy

4. **Telegram Dependency**: Requires Telegram API availability
   - **Production Solution**: Implement fallback mechanisms (SMS, email)

5. **IP Validation Limitations**: May fail behind proxies/NAT
   - **Production Solution**: Use session tokens or more sophisticated validation

6. **No Audit Logging**: No comprehensive logging of authentication attempts
   - **Production Solution**: Implement comprehensive audit logging with timestamps

7. **Client-Side Storage**: Uses sessionStorage (can be cleared)
    - **Production Solution**: Use secure HTTP-only cookies

## Raspberry Pi / MPU Readiness

The application is containerized using Docker, allowing portable deployment across different hardware environments and operating systems. Since Raspberry Pi supports Docker natively on Raspberry Pi OS, the same Docker image can be built and executed on ARM-based devices.

**Key Points:**
- Docker provides platform abstraction, ensuring consistent behavior across x86 and ARM architectures
- The `python:3.11-slim` base image supports multiple architectures including `linux/arm64` (Raspberry Pi 4/5)
- To deploy on Raspberry Pi, simply build the Docker image directly on the target device:
  ```bash
  docker build -t mfa-system -f backend/Dockerfile .
  docker run -p 5000:5000 mfa-system
  ```
- For cross-compilation from a development machine, use Docker Buildx:
  ```bash
  docker buildx build --platform linux/arm64 -t mfa-system .
  ```

This containerization approach demonstrates MPU-readiness and portability, making the MFA system suitable for deployment on embedded systems and IoT devices where security is critical.

## Testing

### Manual Testing Steps

1. **Test Valid Login**
   - Enter correct username and password
   - Verify Telegram receives OTP
   - Enter correct OTP within 60 seconds
   - Verify successful authentication

2. **Test Invalid Password**
   - Enter incorrect password
   - Verify error message displayed

3. **Test Expired OTP**
   - Login successfully
   - Wait more than 60 seconds
   - Try to verify OTP
   - Verify expiration error

4. **Test Invalid OTP**
   - Login successfully
   - Enter incorrect OTP
   - Verify error message

5. **Test Reused OTP**
   - Login and verify OTP successfully
   - Try to use the same OTP again
   - Verify "already used" error

## Troubleshooting

### Telegram Not Receiving Messages
- Verify bot token is correct
- Verify chat ID is correct
- Check internet connection
- Ensure bot is started (send `/start` to bot in Telegram)

### OTP Verification Fails
- Ensure OTP is entered within 60 seconds
- Verify OTP is exactly 6 digits
- Check that you're using the same device/IP as login
- Ensure OTP hasn't been used before

### Server Errors
- Check Flask server logs for error messages
- Verify all dependencies are installed
- Ensure port 5000 is not in use
- Check file paths are correct

## Future Enhancements

- HTTPS/TLS support
- Multiple OTP delivery methods (SMS, email)
- Session management with secure cookies
- Audit logging and monitoring
- User registration and management
- Password reset functionality

## License

This project is created for educational purposes as part of a System Security course.

## Author

Created for System Security Course Project PRJ-7_23

