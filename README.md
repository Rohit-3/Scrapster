# Scrapster - Universal Web Scraper v3.0 🚀

A professional-grade Flask-based web application for scraping anything from the web - profiles, companies, products, or general content. No API keys needed with Direct Scraper mode!

## ✨ Features

### 🎯 Universal Scraping
- **Multiple Content Types**: Scrape profiles, companies, products, or general web content
- **Multiple Sources**: LinkedIn, GitHub, Google, and more
- **Smart Keyword Validation**: Ensures results match your search terms
- **Original Email Extraction**: Only personal emails that match names

### 🚀 Direct Scraper Mode (No API Keys!)
- **Pure Code-Based**: Works like Apple/Google products - just powerful code
- **No Limits**: Unlimited scraping (up to 1000 results)
- **Completely Free**: No API costs, no quotas
- **Multiple Sources**: Searches LinkedIn, GitHub, Google directly

### 📊 Advanced Export
- **Multiple Formats**: CSV, JSON, Excel (XLSX)
- **Rich Data Fields**: Name, email, job title, company, URL, snippet, source, relevance score
- **Deduplication**: Automatically removes duplicates
- **Relevance Scoring**: See why each result matches

### 🎨 Modern UI/UX
- **Beautiful Design**: Gradient backgrounds, smooth animations
- **Real-time Progress**: Live progress bar during scraping
- **AJAX Integration**: No page reloads
- **Responsive**: Works on mobile and desktop

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

For Direct Scraper mode (recommended):
```bash
pip install playwright
playwright install chromium
```

### 2. Run the Application

```bash
python app.py
```

### 3. Access Scrapster

Open your browser and go to:
```
http://127.0.0.1:5001
```

## 📖 Usage Guide

### Basic Usage

1. **Enable Direct Scraper Mode** (recommended - no API keys needed!)

2. **Choose Scraping Type**:
   - **Profiles**: Personal and professional profiles
   - **Companies**: Company profiles and information
   - **Products**: Product listings
   - **General**: General web content

3. **Choose Source**:
   - **All Internet**: Searches LinkedIn, GitHub, Google (recommended)
   - **LinkedIn Only**: Focuses on LinkedIn profiles
   - **GitHub Only**: Focuses on GitHub profiles
   - **Google Only**: General Google search

4. **Enter Search Terms** (one per line):
   ```
   software engineer
   product manager
   data scientist
   python developer
   ```

5. **Enter Locations** (optional, one per line):
   ```
   San Francisco
   India
   Remote
   ```

6. **Set Number of Results** (up to 1000 with Direct Scraper)

7. **Enable Email Extraction** (optional):
   - Only extracts personal emails that match names
   - Filters out generic emails (info@, contact@, etc.)

8. **Click "🚀 Start Scraping & Download"**

### Advanced Usage

#### API Mode (Optional)
If you have Google API keys:
1. Uncheck "Direct Scraper Mode"
2. Enter your Google API Key and CSE ID
3. Enable "API Key Rotation" for unlimited scraping

#### Email Extraction
When enabled:
- Only profiles with personal emails are included
- Emails must match the person's name
- Generic emails are automatically filtered

#### Keyword Validation
Scrapster automatically validates that results match your keywords:
- Filters out irrelevant results (e.g., product sellers vs professionals)
- Scores relevance (0-1)
- Shows why each result matches

## 📤 Export Formats

### CSV Format
Standard CSV with columns:
- name, job_title, company, email, profile_url, snippet, source, profile_type, relevance_score, relevance_reason

### JSON Format
Structured JSON array with all fields

### Excel Format
Excel workbook with formatted columns

## 🎯 Scraping Types

### Profiles
- Personal and professional profiles
- Extracts: name, email, job title, company, location, bio
- Sources: LinkedIn, GitHub, Google

### Companies
- Company profiles and information
- Extracts: name, website, industry, size, location, description
- Sources: LinkedIn, Google, Crunchbase

### Products
- Product listings
- Extracts: name, price, description, rating, seller, URL
- Sources: Google, Amazon, eBay

### General Web Content
- General web content
- Extracts: title, URL, snippet, content
- Sources: Google, Bing, DuckDuckGo

## 🔧 Technical Details

### Direct Scraper Mode
- Uses Playwright browser automation
- No API keys needed
- Supports unlimited scraping
- Slower but more thorough

### API Mode
- Uses Google Custom Search API
- Requires API keys
- Faster but limited to 100 results per key
- Supports API key rotation for unlimited scraping

### Rate Limiting
- Direct Scraper: 1-2 seconds between requests
- API Mode: 1 second between API calls
- Respects source rate limits

## 🛡️ Privacy & Security

- All processing happens locally
- No data sent to external services (except API calls in API mode)
- Private and secure
- Emails are validated before extraction

## 📝 License

This project is provided as-is for educational and authorized use only.

## 🤝 Contributing

Contributions welcome! Please ensure:
- Code follows existing style
- All features are tested
- Documentation is updated

## ⚠️ Disclaimer

This tool is for authorized reconnaissance only. Respect robots.txt and terms of service. Use responsibly and ethically.
