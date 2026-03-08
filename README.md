<br/>
<p align="center">
  <h1 align="center">🔐 Multi-Factor Authentication (MFA) System</h1>

  <p align="center">
    A robust, Python-based Two-Factor Authentication System demonstrating critical security concepts. Designed for System Security (PRJ-7_23).
    <br/>
    <br/>
    <a href="https://github.com/ShafiqullahNasiree/MFA_Project_PRJ-7_23/issues">Report Bug</a>
    .
    <a href="https://github.com/ShafiqullahNasiree/MFA_Project_PRJ-7_23/issues">Request Feature</a>
  </p>
</p>

![Downloads](https://img.shields.io/github/downloads/ShafiqullahNasiree/MFA_Project_PRJ-7_23/total) ![Contributors](https://img.shields.io/github/contributors/ShafiqullahNasiree/MFA_Project_PRJ-7_23?color=dark-green) ![Issues](https://img.shields.io/github/issues/ShafiqullahNasiree/MFA_Project_PRJ-7_23) ![License](https://img.shields.io/github/license/ShafiqullahNasiree/MFA_Project_PRJ-7_23)

## 📝 About The Project

This project is a fully functional **Multi-Factor Authentication (MFA)** implementation built strictly around cybersecurity best practices. For a university **System Security course requirement**, this web app forces users to provide both standard credentials (password) and a time-sensitive One-Time Password (OTP) sent directly to their Telegram account.

It acts as a controlled academic demonstration showing exactly how standard applications handle secure out-of-band communication, replay attack prevention, and cryptographic data validation before granting access.

### Built With

The project uses a lightweight Python framework combined with a persistent SQLite database to ensure clean, readable, and highly secure code.

* ![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white) 
* ![Flask](https://img.shields.io/badge/Flask-000000?style=for-the-badge&logo=flask&logoColor=white)
* ![SQLite](https://img.shields.io/badge/SQLite-003B57?style=for-the-badge&logo=sqlite&logoColor=white)
* ![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)
* ![HTML5](https://img.shields.io/badge/HTML-E34F26?style=for-the-badge&logo=html5&logoColor=white)
* ![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black)

---

## ✨ Core Security Features

### 🛡️ Out-of-Band Validation
Rather than delivering OTPs through the same web interface the user is logging into, this system utilizes the **Telegram API** to send the 6-digit code. This severely mitigates risks if the primary HTTP channel is compromised.

### ⏱️ Time-Based Expiration & Rate Limiting
- **Expiration Limits:** A generated OTP strictly expires after **60 seconds**.
- **Rate Constraints:** The system allows a maximum of 3 failed verification attempts before forcing the user to re-authenticate from scratch.

### 🔐 Cryptographic Integrity
- **Secure Hash Generation:** Passwords are never stored in plain text. They are hashed using `werkzeug.security` (scrypt/pbkdf2).
- **True Randomness:** OTPs are generated using Python's cryptographically secure `secrets` module, rather than predictable pseudo-random integers.

### 🚫 Exploit Overrides
- **IP Address Binding:** The IP address initiating the login *must exactly match* the IP address verifying the OTP to prevent remote session hijacking.
- **Replay Attack Prevention:** A used OTP is immediately flagged in the SQLite database and cannot be reused, successfully defeating replay attacks.

---

## 🚀 Getting Started

Follow these steps to deploy the MFA System locally for testing.

### Prerequisites
- Python 3.11+
- A Telegram account (you will need a Telegram Bot API Token and your unique Chat ID)
- Docker (optional, but recommended for clean environments)

### Manual Installation 

1. **Clone the repository:**
   ```bash
   git clone https://github.com/ShafiqullahNasiree/MFA_Project_PRJ-7_23.git
   cd MFA_Project_PRJ-7_23/backend
   ```
2. **Install Required Python Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
3. **Run the Flask Application:**
   *(The SQLite database `mfa.db` will be auto-generated upon the first launch!)*
   ```bash
   python app.py
   ```
4. **Access the Interface:**
   Navigate in your browser to: `http://localhost:5000`

### 🐳 Docker Deployment (Cross-Architecture/MPU Ready)

Built for ultimate portability, this system easily deploys across servers or Raspberry Pis (ARM64).

1. Build the target image:
   ```bash
   docker build -t mfa-system ./backend
   ```
2. Run the secure container on Port 5000:
   ```bash
   docker run -p 5000:5000 mfa-system
   ```

---

## 🔑 Demonstration Credentials

To interact with the running system, use the built-in demo account:

- **Username**: `student`
- **Password**: `password123`

*(Since this is an academic demo, Telegram bot tokens are embedded in the script for instructor replication. In true production, these secrets would be injected via ENV variables!)*

---

## 📂 Project Architecture

```text
MFA_Project_PRJ-7_23/
├── backend/
│   ├── app.py              # Core application & security logic
│   ├── requirements.txt    # Python PIP dependencies
│   └── Dockerfile          # Portable Docker specification
├── frontend/
│   ├── login.html          # Phase 1: Identity Authentication
│   └── otp.html            # Phase 2: Token Verification
├── screenshots/            # Project execution proofs
├── verify_database.py      # Script to validate SQL transactions
├── HOW_TO_RUN.md           # Deployment overview
├── TESTING_GUIDE.md        # Security testing test-cases
└── README.md               # Main Documentation
```

---

## 🤝 Contributing

Contributions are what make the open source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📫 Contact

Shafiqullah Nasiree - [GitHub Profile](https://github.com/ShafiqullahNasiree)

Project Link: [https://github.com/ShafiqullahNasiree/MFA_Project_PRJ-7_23](https://github.com/ShafiqullahNasiree/MFA_Project_PRJ-7_23)
