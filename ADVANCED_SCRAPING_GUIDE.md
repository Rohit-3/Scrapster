# 🚀 Advanced Browser Automation Guide

## Overview

The app now includes **advanced browser automation** using Playwright to extract real emails from profile pages using deep scraping techniques.

## What It Does

### Standard Mode (Default)
- Extracts emails from search snippets
- Uses pattern inference
- Fast but limited

### Advanced Mode (Optional)
- **Browser Automation**: Opens real browser to visit profile pages
- **Shadow DOM Parsing**: Extracts emails from hidden DOM elements
- **API Interception**: Monitors network calls to capture emails from API responses
- **Contact Modal Interaction**: Clicks Connect/Message buttons to reveal hidden emails
- **Human Behavior Simulation**: Mimics real user behavior to avoid detection

## Installation

### Step 1: Install Playwright

```bash
pip install playwright
```

### Step 2: Install Browser

```bash
playwright install chromium
```

### Step 3: Verify Installation

```bash
python -c "from playwright.sync_api import sync_playwright; print('✅ Playwright installed')"
```

## Usage

### Enable Advanced Scraping

1. Open the web interface: `http://127.0.0.1:5001`
2. Check **"📧 Extract Email Addresses"** (required)
3. Check **"🚀 Enable Advanced Browser Automation"**
4. Fill in your search parameters
5. Click **"🚀 Start Scraping & Download"**

### How It Works

1. **Google Search**: Finds profiles using Google Custom Search API
2. **Profile Collection**: Collects profile URLs from search results
3. **Advanced Scraping** (if enabled):
   - Opens each profile in a real browser
   - Simulates human behavior (scrolling, mouse movement)
   - Extracts emails from:
     - Page content
     - Shadow DOM elements
     - API responses (intercepted)
     - Contact modals (by clicking Connect/Message)
4. **Email Validation**: Filters out generic emails (noreply, support@, etc.)
5. **Export**: Saves results to CSV/JSON/Excel

## Features

### ✅ Multiple Extraction Strategies

1. **Text Extraction**: Finds emails in page HTML
2. **Shadow DOM**: Traverses shadow root elements
3. **API Interception**: Monitors network requests/responses
4. **Modal Interaction**: Clicks buttons to reveal hidden content
5. **Pattern Inference**: Constructs emails from name+company

### ✅ Human Behavior Simulation

- Gradual scrolling
- Random mouse movements
- Natural pauses
- Scroll back/forward patterns

### ✅ Smart Filtering

- Filters out generic emails (noreply, support@, etc.)
- Removes duplicates
- Validates email format
- Prioritizes personal emails

## Performance

- **Standard Mode**: Fast (~1-2 seconds per profile)
- **Advanced Mode**: Slower (~5-10 seconds per profile) but more thorough
- **Recommendation**: Use advanced mode for critical profiles where email is essential

## Limitations

### ⚠️ LinkedIn Restrictions

- LinkedIn may require login for full access
- Some profiles may be restricted
- Rate limiting may apply

### ⚠️ Best Practices

1. **Respect Rate Limits**: Don't scrape too aggressively
2. **Authorized Use Only**: Only use for authorized reconnaissance
3. **Legal Compliance**: Ensure you have permission to scrape
4. **Ethical Use**: Follow terms of service

## Troubleshooting

### "Advanced scraper not available"

**Solution**: Install Playwright:
```bash
pip install playwright
playwright install chromium
```

### "No emails found with advanced scraping"

**Possible causes**:
- Profile requires login
- Profile has no email visible
- LinkedIn blocking automation

**Solutions**:
1. Try without advanced scraping first
2. Check if profile is accessible
3. Verify LinkedIn login if required

### "Playwright timeout"

**Solution**: Increase timeout in `advanced_scraper.py`:
```python
self.page.goto(profile_url, wait_until='networkidle', timeout=60000)  # 60 seconds
```

## Advanced Configuration

### Customize Browser Settings

Edit `advanced_scraper.py`:

```python
# Change headless mode
advanced_scraper = AdvancedProfileScraper(headless=False)  # Show browser

# Change speed
advanced_scraper = AdvancedProfileScraper(slow_mo=200)  # Slower (more human-like)
```

### Customize Email Extraction

Edit extraction patterns in `advanced_scraper.py`:

```python
# Add custom email patterns
EMAIL_REGEX = re.compile(r'[\w\.-]+@[\w\.-]+\.\w+')
```

## Comparison: Standard vs Advanced

| Feature | Standard Mode | Advanced Mode |
|---------|--------------|---------------|
| Speed | ⚡ Fast | 🐌 Slower |
| Email Extraction | ✅ Basic | ✅✅✅ Deep |
| Shadow DOM | ❌ No | ✅ Yes |
| API Interception | ❌ No | ✅ Yes |
| Modal Interaction | ❌ No | ✅ Yes |
| Human Simulation | ❌ No | ✅ Yes |
| Setup Required | ✅ None | ⚠️ Playwright |

## Security Notes

⚠️ **Important**: 
- This tool is for **authorized reconnaissance only**
- Ensure you have permission to scrape profiles
- Follow all applicable laws and terms of service
- Use responsibly and ethically

## Next Steps

1. ✅ Install Playwright
2. ✅ Enable advanced scraping in UI
3. ✅ Test with a small batch first
4. ✅ Monitor results and adjust as needed

---

**Ready to extract real emails?** Enable advanced scraping and start scraping! 🚀

