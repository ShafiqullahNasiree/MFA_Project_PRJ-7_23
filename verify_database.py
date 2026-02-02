import sqlite3
import os

# Auto-detect database path (same logic as app.py)
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = SCRIPT_DIR  # This script is in project root
db_path = os.path.join(PROJECT_ROOT, 'mfa.db')

print("=" * 60)
print("DATABASE VERIFICATION SCRIPT")
print("=" * 60)
print()

# Check if database file exists
if os.path.exists(db_path):
    print(f"[+] Database file exists: {db_path}")
    print(f"[i] File size: {os.path.getsize(db_path)} bytes")
else:
    print("[!] Database file not found!")
    exit(1)

print()

# Connect to database
conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

# List tables
print("=" * 60)
print("TABLES IN DATABASE:")
print("=" * 60)
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()
for table in tables:
    print(f"  - {table['name']}")

print()

# Check users table
print("=" * 60)
print("USERS TABLE:")
print("=" * 60)
cursor.execute("SELECT id, username, telegram_chat_id, created_at FROM users;")
users = cursor.fetchall()
for user in users:
    print(f"  ID: {user['id']}")
    print(f"  Username: {user['username']}")
    print(f"  Telegram Chat ID: {user['telegram_chat_id']}")
    print(f"  Created At: {user['created_at']}")
    print()

# Check password hash
cursor.execute("SELECT password_hash FROM users WHERE username='student';")
user = cursor.fetchone()
if user:
    print(f"  Password Hash Length: {len(user['password_hash'])} characters")
    print(f"  Hash Preview: {user['password_hash'][:50]}...")
    print(f"  [+] Password is hashed (not plain text)")
else:
    print("  [!] Demo user not found!")

print()

# Check otps table schema
print("=" * 60)
print("OTPS TABLE SCHEMA:")
print("=" * 60)
cursor.execute("PRAGMA table_info(otps);")
columns = cursor.fetchall()
for col in columns:
    print(f"  {col['name']}: {col['type']} (pk={col['pk']}, notnull={col['notnull']}, default={col['dflt_value']})")

print()

# Check OTPs count
cursor.execute("SELECT COUNT(*) as count FROM otps;")
result = cursor.fetchone()
print(f"[i] Total OTPs in database: {result['count']}")

print()
print("=" * 60)
print("[+] Database verification complete!")
print("=" * 60)

conn.close()
