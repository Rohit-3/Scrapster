# 🚀 Unlimited Scraping Guide

## How to Scrape Unlimited Contacts

Google Custom Search API has a limit of **100 results per API key per day** (free tier). To scrape unlimited contacts, you need to use **multiple API keys** and enable **key rotation**.

## 📋 Step-by-Step Setup

### Step 1: Get Multiple Google API Keys

1. **Create Multiple Google Cloud Projects**:
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project (e.g., "Scraper-Project-1", "Scraper-Project-2", etc.)
   - Enable Custom Search API for each project
   - Create API keys for each project

2. **Create Multiple Custom Search Engines**:
   - Go to [Google Programmable Search](https://programmablesearchengine.google.com/)
   - Create a new search engine for each API key
   - Get the CSE ID for each search engine

### Step 2: Setup Config File

1. **Create `config.env` file** (copy from `config.env.example`):
   ```bash
   cp config.env.example config.env
   ```

2. **Add your credentials** to `config.env`:
   ```env
   # Option 1: Single API Key (100 results/day)
   GOOGLE_API_KEY=AIzaSy1234567890abcdefghijklmnopqrstuvwxyz
   GOOGLE_CSE_ID=012345678901234567890:abcdefghijk
   
   # Option 2: Multiple API Keys (unlimited results)
   # Format: api_key1:cse_id1,api_key2:cse_id2,api_key3:cse_id3
   MULTIPLE_API_KEYS=AIzaSy111:abc111,AIzaSy222:def222,AIzaSy333:ghi333
   
   # Enable auto-rotation
   AUTO_ROTATE_KEYS=true
   
   # Rate limiting (seconds between requests)
   RATE_LIMIT_DELAY=1
   ```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Run the Application

```bash
python app.py
```

### Step 5: Use in Web Interface

1. **Check "💾 Use Saved Credentials from config.env"**
2. **Check "🔄 Enable API Key Rotation"** (if using multiple keys)
3. Enter your keywords and locations
4. Set the number of profiles you want (can be > 100 with key rotation)
5. Click "🚀 Start Scraping & Download"

## 🎯 How It Works

### Single API Key (100 results/day)
- Uses one API key from `GOOGLE_API_KEY` in config.env
- Maximum 100 results per day
- No rotation needed

### Multiple API Keys (Unlimited)
- Automatically rotates through multiple API keys
- When one key reaches quota (100 results), switches to next key
- Continues until all keys are exhausted or you reach your limit
- **Example**: 5 API keys = 500 results/day

## 📊 Calculation Examples

### Example 1: 3 API Keys
- **Results per day**: 3 × 100 = **300 results/day**
- **Config**:
  ```
  MULTIPLE_API_KEYS=key1:cse1,key2:cse2,key3:cse3
  AUTO_ROTATE_KEYS=true
  ```

### Example 2: 10 API Keys
- **Results per day**: 10 × 100 = **1,000 results/day**
- **Config**:
  ```
  MULTIPLE_API_KEYS=key1:cse1,key2:cse2,key3:cse3,key4:cse4,key5:cse5,key6:cse6,key7:cse7,key8:cse8,key9:cse9,key10:cse10
  AUTO_ROTATE_KEYS=true
  ```

### Example 3: 50 API Keys
- **Results per day**: 50 × 100 = **5,000 results/day**
- Perfect for large-scale scraping campaigns

## 🔧 Advanced Configuration

### Manual API Key Management

If you want to manually manage keys, you can:

1. **Disable auto-rotation**:
   ```env
   AUTO_ROTATE_KEYS=false
   ```

2. **Use only form-based credentials**: Don't check "Use Saved Credentials"

3. **Rotate manually**: Enter different API keys in the form for each scraping session

### Rate Limiting

Adjust the delay between requests:

```env
RATE_LIMIT_DELAY=2  # 2 seconds between requests (more conservative)
```

**Recommendations**:
- **1 second**: Standard (default)
- **2 seconds**: More conservative, less likely to hit rate limits
- **0.5 seconds**: Faster but riskier

## ⚠️ Important Notes

### Google API Limits

1. **Free Tier**: 100 queries/day per API key
2. **Paid Tier**: Can request higher quotas
3. **Quota Resets**: Daily at midnight Pacific Time

### Best Practices

1. **Don't abuse the API**: Respect rate limits
2. **Use multiple projects**: One API key per Google Cloud project
3. **Monitor usage**: Check Google Cloud Console for quota usage
4. **Rotate keys**: Use key rotation for large scraping jobs
5. **Save credentials**: Use config.env instead of entering in form each time

### Troubleshooting

#### "All API keys have exceeded quota"
- **Solution**: Wait 24 hours or add more API keys

#### "No available API keys found"
- **Solution**: Check your `config.env` file format
- Ensure `MULTIPLE_API_KEYS` follows the format: `key1:cse1,key2:cse2`

#### "API Quota Exceeded"
- **Solution**: Enable key rotation or wait for quota reset

## 💰 Cost Considerations

### Free Tier
- **100 queries/day per API key**: FREE
- **Multiple API keys**: FREE (as long as you stay within free tier)

### Paid Tier
- **$5 per 1,000 queries** (after free tier)
- **Cost-effective for large-scale scraping**

## 🎯 Example Scenarios

### Scenario 1: Small Project (100-500 contacts)
- **Setup**: 1-5 API keys
- **Config**: Single or multiple keys
- **Time**: 1-5 minutes per scraping session

### Scenario 2: Medium Project (500-2,000 contacts)
- **Setup**: 5-20 API keys
- **Config**: Multiple keys with rotation
- **Time**: 5-20 minutes per scraping session

### Scenario 3: Large Project (2,000+ contacts)
- **Setup**: 20+ API keys
- **Config**: Multiple keys with rotation
- **Time**: 20+ minutes per scraping session
- **Consider**: Paid tier for higher quotas

## 🔐 Security Best Practices

1. **Never commit `config.env` to Git**:
   - Add to `.gitignore`:
     ```
     config.env
     .env
     ```

2. **Use environment variables** in production instead of files

3. **Rotate API keys** regularly for security

4. **Restrict API keys** to specific IPs/domains in Google Cloud Console

## 📝 Summary

✅ **Unlimited scraping** = Multiple API keys + Key rotation enabled  
✅ **100 results/day** = 1 API key  
✅ **N × 100 results/day** = N API keys  
✅ **Automatic rotation** = Enable in config.env and UI  
✅ **Secure storage** = Use config.env file (never commit to Git)

---

**Ready to scrape unlimited contacts?** Set up your `config.env` file and enable key rotation! 🚀

