# MFA System Testing Guide

This guide will help you test all features of the MFA system to ensure everything is working correctly.

## Prerequisites

1. Python 3.11 or higher installed
2. Telegram account with bot access
3. Internet connection for Telegram API

## Step 1: Install Dependencies

Open a terminal/command prompt in the project root directory and run:

```bash
cd backend
pip install -r requirements.txt
```

Expected output: Flask and requests packages should install successfully.

## Step 2: Configure Telegram Credentials

1. Create a `.env` file from the template:

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

2. Fill in your `TELEGRAM_TOKEN` and `TELEGRAM_CHAT_ID` values in the `.env` file.

3. **Test Telegram Bot** (Optional but recommended):
   - Open Telegram
   - Find your bot
   - Send `/start` to verify the bot is active
   - The bot should respond (if configured)

## Step 3: Start the Flask Server

In the terminal (from `backend` directory):

```bash
python app.py
```

Expected output:
```
 * Running on http://0.0.0.0:5000
 * Debug mode: on
```

**Keep this terminal window open** - the server must be running.

## Step 4: Test the Login Page

1. Open your web browser
2. Navigate to: `http://localhost:5000`
3. You should see:
   - Purple/blue gradient background
   - White login card
   - Title: "🔐 Secure MFA Login"
   - Demo credentials box showing: `student / password123`
   - Username and Password input fields
   - Login button

## Step 5: Test Invalid Login (Security Check)

**Test 5.1: Wrong Username**
- Enter username: `wronguser`
- Enter password: `password123`
- Click "Login"
- **Expected**: Red error message "Invalid username or password"

**Test 5.2: Wrong Password**
- Enter username: `student`
- Enter password: `wrongpass`
- Click "Login"
- **Expected**: Red error message "Invalid username or password"

## Step 6: Test Valid Login and OTP Generation

1. Enter username: `student`
2. Enter password: `password123`
3. Click "Login"
4. **Expected Results**:
   - Green success message: "OTP sent to your Telegram. Please check your messages."
   - Page automatically redirects to OTP page after 1.5 seconds
   - **Check Telegram**: You should receive a message with:
     - 🔐 Your MFA OTP is: [6-digit number]
     - Valid for 60 seconds message

5. **Verify OTP Format**:
   - OTP should be exactly 6 digits
   - Example: `123456` or `789012`

## Step 7: Test OTP Verification Page

After login, you should see:
- Title: "📱 Enter OTP"
- Yellow warning box: "⚠️ Check Telegram" and "OTP valid for 60 seconds"
- 6-digit OTP input field (centered, large)
- Green "Verify OTP" button
- "← Back to Login" link

## Step 8: Test All 5 Security Checks

### Security Check 1: Invalid OTP Code
1. Enter any wrong 6-digit OTP (e.g., `000000`)
2. Click "Verify OTP"
3. **Expected**: Red error "Invalid OTP. Please try again."

### Security Check 2: OTP Expiration (60 seconds)
1. Login again to get a new OTP
2. **Wait 61 seconds** (use a timer)
3. Enter the OTP you received
4. Click "Verify OTP"
5. **Expected**: Red error "OTP has expired. Please login again."

### Security Check 3: OTP Reuse Prevention
1. Login to get a new OTP
2. Check Telegram for the OTP
3. Enter the correct OTP
4. Click "Verify OTP"
5. **Expected**: 
   - Green success message
   - Alert popup: "✅ Authentication Successful! Access granted to the system."
6. **Now test reuse**:
   - Try to login again
   - Use the SAME OTP from before
   - **Expected**: Red error "OTP has already been used. Please login again."

### Security Check 4: IP Address Validation
**Note**: This test requires two different IP addresses. For local testing:
- This check works when accessing from different networks
- On localhost, both login and OTP will have same IP (127.0.0.1)
- This security feature is more relevant in production with real IPs

**To test** (if possible):
1. Login from one network/IP
2. Try to verify OTP from a different network/IP
3. **Expected**: Red error "IP address mismatch. Security violation detected."

### Security Check 5: Missing OTP (No Login)
1. Go directly to: `http://localhost:5000/otp_page`
2. Try to enter any OTP
3. **Expected**: 
   - Either redirects to login page, OR
   - Red error "No OTP found. Please login again."

## Step 9: Test Complete Successful Flow

1. **Login**:
   - Username: `student`
   - Password: `password123`
   - Click "Login"

2. **Check Telegram**:
   - Open Telegram immediately
   - Find the OTP message
   - Copy the 6-digit OTP

3. **Verify OTP** (within 60 seconds):
   - Enter the OTP in the input field
   - Click "Verify OTP"

4. **Expected Final Result**:
   - Green success message
   - Alert popup: "✅ Authentication Successful! Access granted to the system."
   - Redirects back to login page

## Step 10: Test Error Handling

### Test Network Error Simulation
1. Stop the Flask server (Ctrl+C in terminal)
2. Try to login
3. **Expected**: Error message about network/connection

### Test Empty Fields
1. Try to login with empty username or password
2. **Expected**: Browser validation prevents submission

### Test Invalid OTP Format
1. Login successfully
2. Enter non-numeric characters in OTP field
3. **Expected**: Field only accepts numbers (auto-filtered)

## Step 11: Check Server Logs

While testing, watch the terminal where Flask is running. You should see:
- HTTP requests logged (GET /, POST /login, POST /verify_otp)
- Any error messages if something fails

## Step 12: Verify Telegram Integration

**Test Telegram Message Sending**:
1. Login with correct credentials
2. Check Telegram within 5 seconds
3. **Expected**: Message arrives quickly
4. If message doesn't arrive:
   - Check bot token is correct
   - Check chat ID is correct
   - Check internet connection
   - Check Flask terminal for error messages

## Troubleshooting

### Problem: "ModuleNotFoundError: No module named 'flask'"
**Solution**: Run `pip install -r requirements.txt` in the backend directory

### Problem: "Address already in use"
**Solution**: Port 5000 is busy. Either:
- Stop other applications using port 5000
- Or change port in `app.py` (line 259): `app.run(host='0.0.0.0', port=5001, debug=True)`

### Problem: Telegram not receiving messages
**Solutions**:
1. Verify bot token is correct in `app.py`
2. Verify chat ID is correct
3. Make sure bot is started (send `/start` in Telegram)
4. Check internet connection
5. Check Flask terminal for error messages

### Problem: "No OTP found" error immediately
**Solution**: Make sure you're using the same browser session and didn't clear sessionStorage

### Problem: OTP page shows "Please login first"
**Solution**: This happens if sessionStorage is cleared. Just go back to login page and login again.

## Quick Test Checklist

- [ ] Dependencies installed successfully
- [ ] Flask server starts without errors
- [ ] Login page loads correctly
- [ ] Invalid credentials show error
- [ ] Valid login sends OTP to Telegram
- [ ] OTP page loads after login
- [ ] Wrong OTP shows error
- [ ] Correct OTP (within 60s) shows success
- [ ] Expired OTP (after 60s) shows error
- [ ] Used OTP cannot be reused
- [ ] Complete flow works end-to-end

## Expected Behavior Summary

✅ **Working Correctly**:
- Login with wrong credentials → Error
- Login with correct credentials → OTP sent to Telegram
- Enter wrong OTP → Error
- Enter correct OTP within 60s → Success
- Enter expired OTP → Error
- Reuse OTP → Error
- All security checks functioning

❌ **Not Working** (needs fixing):
- Server won't start → Check Python/Flask installation
- Telegram not receiving messages → Check credentials
- Pages not loading → Check file paths
- OTP always fails → Check security logic

## Testing Complete!

Once all tests pass, your MFA system is working correctly. All 5 security checks should be functioning, and the complete authentication flow should work smoothly.

