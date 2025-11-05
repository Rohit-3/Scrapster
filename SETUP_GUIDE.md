# 📋 Setup Guide - Where to Put API Keys

## 🔑 Where to Put Google API Key and CSE ID

You have **two options** for providing your credentials:

### Option 1: Using Config File (Recommended) ✅

**Best for**: Security, convenience, and unlimited scraping

1. **Create `config.env` file** (copy from `config.env.example`):
   ```bash
   cp config.env.example config.env
   ```

2. **Edit `config.env`** and add your credentials:
   ```env
   # Single API Key (for basic use)
   GOOGLE_API_KEY=AIzaSy1234567890abcdefghijklmnopqrstuvwxyz
   GOOGLE_CSE_ID=012345678901234567890:abcdefghijk
   
   # For unlimited scraping, add multiple keys:
   # MULTIPLE_API_KEYS=key1:cse1,key2:cse2,key3:cse3
   ```

3. **In the web interface**:
   - ✅ Check "💾 Use Saved Credentials from config.env"
   - The credentials form will be hidden
   - Your API keys will be loaded from `config.env`

**Benefits**:
- ✅ No need to enter credentials each time
- ✅ Supports multiple API keys for unlimited scraping
- ✅ More secure (file not in browser)
- ✅ Easy to switch between different API keys

### Option 2: Using Web Form (Quick Setup)

**Best for**: Quick testing or one-time use

1. **In the web interface**:
   - ❌ Don't check "Use Saved Credentials"
   - Enter your API Key in the "🔑 Google API Key" field
   - Enter your CSE ID in the "🆔 Custom Search Engine ID" field

2. **Fill in the rest of the form** and submit

**Benefits**:
- ✅ Quick setup, no file needed
- ✅ Good for testing

## 🔐 Security Note

**⚠️ IMPORTANT**: Never commit `config.env` to Git!

Add to `.gitignore`:
```
config.env
.env
*.env
```

## 📝 Getting Your API Credentials

### Step 1: Get Google API Key

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable **Custom Search API**
4. Go to **Credentials** → **Create Credentials** → **API Key**
5. Copy your API key

### Step 2: Get Custom Search Engine ID (CSE ID)

1. Go to [Google Programmable Search](https://programmablesearchengine.google.com/)
2. Click **Add** to create a new search engine
3. Configure your search engine:
   - **Sites to search**: Leave blank or add specific sites
   - **Language**: Your preferred language
   - **Name**: Give it a name (e.g., "RFID Profiler")
4. Click **Create**
5. Go to **Setup** → **Basics**
6. Copy your **Search Engine ID** (CX)

## 🚀 Quick Start

### Method 1: Using Config File

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Create `config.env`:
   ```bash
   cp config.env.example config.env
   # Edit config.env and add your credentials
   ```

3. Run the app:
   ```bash
   python app.py
   ```

4. Open browser:
   ```
   http://127.0.0.1:5000
   ```

5. Check "💾 Use Saved Credentials" and fill in the form

### Method 2: Using Web Form

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Run the app:
   ```bash
   python app.py
   ```

3. Open browser:
   ```
   http://127.0.0.1:5000
   ```

4. Enter your API Key and CSE ID in the form fields

## 🎯 Example Config File

**config.env**:
```env
# Basic setup (100 results/day)
GOOGLE_API_KEY=AIzaSy1234567890abcdefghijklmnopqrstuvwxyz
GOOGLE_CSE_ID=012345678901234567890:abcdefghijk

# Advanced setup (unlimited results)
# MULTIPLE_API_KEYS=key1:cse1,key2:cse2,key3:cse3
# AUTO_ROTATE_KEYS=true
# RATE_LIMIT_DELAY=1
```

## ✅ Troubleshooting

### "No available API keys found in config"
- **Solution**: Check that `config.env` exists and has correct format
- Ensure `GOOGLE_API_KEY` and `GOOGLE_CSE_ID` are set

### "API Key and CSE ID are required"
- **Solution**: Either use saved credentials (check the box) or enter them in the form

### "Invalid API Key"
- **Solution**: Verify your API key in Google Cloud Console
- Ensure Custom Search API is enabled

### "Invalid CSE ID"
- **Solution**: Verify your CSE ID in Google Programmable Search
- Ensure your search engine is active

## 📚 More Information

- **Unlimited Scraping**: See `UNLIMITED_SCRAPING_GUIDE.md`
- **Full Documentation**: See `README.md`

---

**That's it!** You're ready to start scraping! 🚀

