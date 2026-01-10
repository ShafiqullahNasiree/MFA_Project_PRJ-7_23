# How to Run the MFA System

This guide shows you two ways to run the MFA system: **Without Docker** (simple) and **With Docker** (containerized).

---

## Method 1: Run Without Docker (Simple - Recommended for Testing)

### Step 1: Install Python Dependencies

Open PowerShell or Command Prompt in the project root directory:

```powershell
cd backend
pip install -r requirements.txt
```

### Step 2: Configure Telegram Credentials

Create a `.env` file from the template:

**Windows PowerShell:**
```powershell
Copy-Item .env.example .env
notepad .env
```

**Linux/macOS:**
```bash
cp .env.example .env
nano .env
```

Fill in your `TELEGRAM_TOKEN` and `TELEGRAM_CHAT_ID` values.

**Alternative:** Set environment variables directly in PowerShell:
```powershell
$env:TELEGRAM_TOKEN="your_token_here"
$env:TELEGRAM_CHAT_ID="your_chat_id_here"
```

### Step 3: Start the Flask Server

In the `backend` directory:

```powershell
python app.py
```

You should see:
```
 * Running on http://0.0.0.0:5000
 * Debug mode: on
```

**Keep this terminal window open!** The server must keep running.

### Step 3: Open the Website

1. Open your web browser (Chrome, Edge, Firefox, etc.)
2. Go to: **http://localhost:5000**
3. You should see the login page!

### Step 4: Test the System

- **Username**: `student`
- **Password**: `password123`
- Click "Login"
- Check Telegram for the OTP
- Enter OTP and verify

### To Stop the Server

Press `Ctrl + C` in the terminal window.

---

## Method 2: Run With Docker

### Prerequisites

- Docker Desktop must be installed and running
- Check if Docker is running: Open Docker Desktop application

### Step 1: Build the Docker Image

Open PowerShell or Command Prompt in the **project root directory** (not backend):

```powershell
docker build -t mfa-system -f backend/Dockerfile .
```

This will:
- Download Python 3.11 image
- Install Flask and requests
- Copy all necessary files
- Create the Docker image

**Wait for it to finish** - it may take 1-2 minutes the first time.

### Step 2: Run the Docker Container

```powershell
docker run -p 5000:5000 mfa-system
```

You should see:
```
 * Running on http://0.0.0.0:5000
 * Debug mode: on
```

**Keep this terminal window open!**

### Step 3: Open the Website

1. Open your web browser
2. Go to: **http://localhost:5000**
3. You should see the login page!

### Step 4: Test the System

Same as Method 1:
- **Username**: `student`
- **Password**: `password123`
- Click "Login"
- Check Telegram for the OTP
- Enter OTP and verify

### To Stop the Docker Container

Press `Ctrl + C` in the terminal window.

### To Remove the Container (Optional)

After stopping, you can remove it:
```powershell
docker ps -a
docker rm <container-id>
```

---

## Troubleshooting

### Problem: "pip: command not found" or "python: command not found"

**Solution**: 
- Make sure Python is installed
- Try: `python3` instead of `python`
- Try: `pip3` instead of `pip`
- Or install Python from python.org

### Problem: "Port 5000 is already in use"

**Solution**: 
- Another application is using port 5000
- Stop that application, OR
- Change port in `backend/app.py` line 257:
  ```python
  app.run(host='0.0.0.0', port=5001, debug=True)
  ```
- Then use: `http://localhost:5001`

### Problem: Docker build fails with "COPY failed"

**Solution**: 
- Make sure you're running the build command from the **project root** directory
- The command should be: `docker build -t mfa-system -f backend/Dockerfile .`
- The `.` at the end is important!

### Problem: "Docker daemon is not running"

**Solution**: 
- Open Docker Desktop application
- Wait for it to start (whale icon in system tray)
- Try again

### Problem: Website shows "This site can't be reached"

**Solution**: 
- Make sure the Flask server is running (check terminal)
- Make sure you're using: `http://localhost:5000` (not https)
- Check if firewall is blocking port 5000

### Problem: Telegram not receiving OTP

**Solution**: 
- Check `backend/app.py` lines 13-14 have correct credentials
- Make sure internet connection is working
- Check Flask terminal for error messages

---

## Quick Reference

### Without Docker (Fastest for Testing)
```powershell
cd backend
pip install -r requirements.txt
python app.py
```
Then open: **http://localhost:5000**

### With Docker
```powershell
docker build -t mfa-system -f backend/Dockerfile .
docker run -p 5000:5000 mfa-system
```
Then open: **http://localhost:5000**

---

## Which Method Should I Use?

- **Use Method 1 (Without Docker)** if:
  - You want to test quickly
  - You don't have Docker installed
  - You're making changes to the code

- **Use Method 2 (With Docker)** if:
  - You want to test containerization
  - You want to ensure consistent environment
  - You're preparing for deployment

---

## Testing Checklist

Once the website is running:

- [ ] Login page loads at http://localhost:5000
- [ ] Can see login form with username/password fields
- [ ] Wrong password shows error
- [ ] Correct login (student/password123) sends OTP to Telegram
- [ ] OTP page loads after login
- [ ] Can enter OTP and verify
- [ ] Success message appears after correct OTP

---

**Need Help?** Check the `TESTING_GUIDE.md` for detailed testing instructions!

