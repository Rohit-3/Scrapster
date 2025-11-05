# app.py - Scrapster Universal Web Scraper v3.0
from flask import Flask, render_template, request, send_file, jsonify
import requests
import time
import csv
import io
import json
import re
import os
from urllib.parse import urlparse
from collections import OrderedDict

# Try to import config (optional - works without it)
try:
    from config import config
    CONFIG_AVAILABLE = True
except ImportError:
    CONFIG_AVAILABLE = False
    print("⚠️  Config file not found. Using form-based credentials only.")

# Try to import advanced scraper (optional - requires playwright)
try:
    from advanced_scraper import AdvancedProfileScraper
    ADVANCED_SCRAPER_AVAILABLE = True
except ImportError:
    ADVANCED_SCRAPER_AVAILABLE = False
    print("⚠️  Advanced scraper not available. Install playwright: pip install playwright && playwright install chromium")

# Try to import direct scraper (pure code-based, no API keys)
try:
    from direct_scraper import DirectWebScraper
    DIRECT_SCRAPER_AVAILABLE = True
except ImportError:
    DIRECT_SCRAPER_AVAILABLE = False
    print("⚠️  Direct scraper not available. Install playwright: pip install playwright && playwright install chromium")

app = Flask(__name__)

# Email regex pattern
EMAIL_PATTERN = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')

# Common contact/generic emails to exclude
GENERIC_EMAIL_PATTERNS = [
    'noreply', 'no-reply', 'donotreply', 'support@', 'info@', 'contact@', 
    'admin@', 'webmaster@', 'privacy@', 'hello@', 'mailer-', 'postmaster@',
    'sales@', 'marketing@', 'help@', 'customerservice@', 'service@',
    'broofa', 'example', 'test@', 'sample@'  # Common test/placeholder emails
]

# Common job title patterns
JOB_TITLE_PATTERNS = [
    r'(?:Senior|Junior|Lead|Principal|Staff)?\s*(?:Software|Hardware|Embedded|IoT|RF|Wireless|Systems|Data|AI|ML|Cloud|DevOps|Full.?Stack|Frontend|Backend)?\s*(?:Engineer|Developer|Architect|Specialist|Consultant|Manager|Director|Technician|Analyst|Scientist|Researcher|Designer|Product|Marketing|Sales|Business)',
    r'Product\s*(?:Manager|Owner|Lead)',
    r'Technical\s*(?:Lead|Manager|Director|Architect)',
    r'Engineering\s*(?:Manager|Director|Lead)',
]

# Company name extraction patterns
COMPANY_PATTERNS = [
    r'at\s+([A-Z][a-zA-Z0-9\s&,.-]+?)(?:\s|,|\.|$)',
    r'@\s*([A-Z][a-zA-Z0-9\s&,.-]+?)(?:\s|,|\.|$)',
    r'from\s+([A-Z][a-zA-Z0-9\s&,.-]+?)(?:\s|,|\.|$)',
]

def scrape_profile_for_email(url, use_advanced=False, advanced_scraper=None):
    """Try to scrape profile page to find email address using basic or advanced methods"""
    # Use advanced browser automation if available and enabled
    if use_advanced and ADVANCED_SCRAPER_AVAILABLE and advanced_scraper:
        try:
            result = advanced_scraper.scrape_profile_email(url)
            if result['success'] and result['emails']:
                return result['emails'][0]  # Return first email found
        except Exception as e:
            print(f"⚠️  Advanced scraping failed: {e}, falling back to basic method")
    
    # Fallback to basic HTTP scraping
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        resp = requests.get(url, headers=headers, timeout=5, allow_redirects=True)
        if resp.status_code == 200:
            content = resp.text
            # Look for emails in the page content
            emails = EMAIL_PATTERN.findall(content)
            if emails:
                # Filter out common non-personal emails
                filtered = [e for e in emails if not any(skip in e.lower() for skip in ['noreply', 'no-reply', 'donotreply', 'support@', 'info@', 'contact@', 'admin@', 'webmaster@', 'privacy@'])]
                if filtered:
                    return filtered[0]
                # If no filtered, return first email
                return emails[0]
    except:
        pass
    return ""

def infer_email_from_name_company(name, company):
    """Try to infer email from name and company using common patterns"""
    if not name or not company:
        return ""
    
    # Clean company name for domain
    company_clean = company.lower()
    company_clean = re.sub(r'\s+(inc|llc|ltd|corp|corporation|company|co)\.?$', '', company_clean, flags=re.IGNORECASE)
    company_clean = re.sub(r'[^a-z0-9.-]', '', company_clean)
    
    # Extract name parts
    name_parts = name.lower().split()
    if not name_parts:
        return ""
    
    first_name = name_parts[0]
    last_name = name_parts[-1] if len(name_parts) > 1 else ""
    
    # Common email patterns
    patterns = []
    if last_name:
        patterns = [
            f"{first_name}.{last_name}@{company_clean}",
            f"{first_name}{last_name}@{company_clean}",
            f"{first_name}_{last_name}@{company_clean}",
            f"{first_name[0]}{last_name}@{company_clean}",
            f"{first_name}{last_name[0]}@{company_clean}",
        ]
    else:
        patterns = [
            f"{first_name}@{company_clean}",
        ]
    
    # Return first pattern (we can't verify these, but user can try)
    # Note: These are inferred, not verified, so we'll mark them differently
    return patterns[0] if patterns else ""

def is_generic_email(email):
    """Check if email is generic/contact email (not personal)"""
    email_lower = email.lower()
    return any(pattern in email_lower for pattern in GENERIC_EMAIL_PATTERNS)

def is_profile_specific_email(email, name, profile_text=""):
    """Check if email matches the profile (name-based validation)"""
    if not name or not email:
        return False
    
    # Extract name parts
    name_parts = [p.lower() for p in name.split() if len(p) > 2]
    email_lower = email.lower()
    
    # Check if email contains name parts
    for part in name_parts:
        if part in email_lower:
            return True
    
    # Check if email domain matches profile context
    if profile_text:
        company = extract_company(profile_text)
        if company:
            company_domain = company.lower().replace(' ', '').replace('&', '').replace(',', '')
            company_domain = re.sub(r'[^a-z0-9.-]', '', company_domain)
            if company_domain in email_lower:
                return True
    
    return False

def extract_email(text, url="", name="", company="", profile_url=""):
    """Extract profile-specific email addresses using intelligent strategies"""
    all_found_emails = []
    
    # Strategy 1: Extract from text (profile description)
    text_emails = EMAIL_PATTERN.findall(text)
    for email in text_emails:
        if not is_generic_email(email):
            # Check if email seems profile-specific
            if is_profile_specific_email(email, name, text):
                return email  # High confidence match
            all_found_emails.append((email, 3))  # Medium confidence
    
    # Strategy 2: Extract from URL
    if url:
        url_emails = EMAIL_PATTERN.findall(url)
        for email in url_emails:
            if not is_generic_email(email):
                if is_profile_specific_email(email, name, text):
                    return email
                all_found_emails.append((email, 2))
    
    # Strategy 3: Try to scrape profile page (if profile URL)
    if profile_url and any(domain in profile_url.lower() for domain in ['linkedin.com/in', 'github.com', 'twitter.com', 'about.me']):
        scraped_email = scrape_profile_for_email(profile_url, use_advanced=False)
        if scraped_email and not is_generic_email(scraped_email):
            if is_profile_specific_email(scraped_email, name, text):
                return scraped_email
            all_found_emails.append((scraped_email, 4))  # High confidence from scraping
    
    # Strategy 4: Infer email from name/company (only if no direct match found)
    if not all_found_emails and name and company:
        inferred = infer_email_from_name_company(name, company)
        if inferred and not is_generic_email(inferred):
            all_found_emails.append((inferred, 1))  # Low confidence (inferred)
    
    # Strategy 5: Extract company and try inference
    if not all_found_emails and name and text:
        company_from_text = extract_company(text)
        if company_from_text:
            inferred = infer_email_from_name_company(name, company_from_text)
            if inferred and not is_generic_email(inferred):
                all_found_emails.append((inferred, 1))
    
    # Return best match (highest confidence, then first found)
    if all_found_emails:
        # Sort by confidence (higher is better)
        all_found_emails.sort(key=lambda x: x[1], reverse=True)
        return all_found_emails[0][0]
    
    return ""

def extract_job_title(text, title):
    """Extract job title from snippet and title"""
    combined = f"{title} {text}".lower()
    for pattern in JOB_TITLE_PATTERNS:
        match = re.search(pattern, combined, re.IGNORECASE)
        if match:
            return match.group(0).strip()
    return ""

def extract_company(text):
    """Extract company name from snippet"""
    for pattern in COMPANY_PATTERNS:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            company = match.group(1).strip()
            # Clean up common endings
            company = re.sub(r'\s+(Inc|LLC|Ltd|Corp|Corporation|Company|Co)\.?$', '', company, flags=re.IGNORECASE)
            return company
    return ""

def is_linkedin_profile(url):
    """Check if URL is a LinkedIn profile"""
    parsed = urlparse(url)
    return 'linkedin.com/in' in url.lower() or 'linkedin.com/pub' in url.lower()

def is_github_profile(url):
    """Check if URL is a GitHub profile"""
    parsed = urlparse(url)
    return 'github.com' in url.lower() and '/in/' not in url.lower()

def build_query(keywords, locations, keyword_operator, location_operator, target_individuals=True, strict_mode=False):
    """Build advanced search query with operators, targeting individual profiles"""
    # Process keywords
    keyword_list = [k.strip() for k in keywords.splitlines() if k.strip()]
    if not keyword_list:
        return ""
    
    # Build keyword query
    if len(keyword_list) == 1:
        keyword_query = f'"{keyword_list[0]}"'
    else:
        operator = " AND " if keyword_operator == "AND" else " OR "
        quoted_keywords = [f'"{k}"' for k in keyword_list]
        keyword_query = f'({operator.join(quoted_keywords)})'
    
    # Target individual profiles - but make it less restrictive
    if target_individuals and strict_mode:
        # Only in strict mode: target specific profile sites
        profile_sites = 'site:linkedin.com/in OR site:github.com OR site:about.me OR site:twitter.com'
        keyword_query = f'({keyword_query}) AND ({profile_sites})'
    elif target_individuals:
        # In normal mode: add profile keywords but don't restrict to specific sites
        # This broadens the search while still targeting individuals
        profile_keywords = 'profile OR "about me" OR linkedin OR contact'
        keyword_query = f'{keyword_query} {profile_keywords}'
    
    # Process locations
    location_list = [l.strip() for l in locations.splitlines() if l.strip()]
    
    # Build location query
    if location_list:
        operator = " AND " if location_operator == "AND" else " OR "
        quoted_locations = [f'"{loc}"' for loc in location_list]
        location_query = f' AND ({operator.join(quoted_locations)})'
    else:
        location_query = ""
    
    return keyword_query + location_query

def deduplicate_results(results):
    """Remove duplicate results based on profile URL and email"""
    seen_urls = set()
    seen_emails = {}  # email -> first profile URL
    unique_results = []
    
    for result in results:
        url = result.get('profile_url', '')
        email = result.get('email', '').lower().strip() if result.get('email') else ''
        
        # Skip if URL already seen
        if url and url in seen_urls:
            continue
        
        # Skip if email already used for a different profile
        if email and email in seen_emails:
            existing_url = seen_emails[email]
            if existing_url != url:
                # Same email, different profile - skip this one
                continue
        
        # Add to results
        if url:
            seen_urls.add(url)
        if email:
            seen_emails[email] = url
        
        unique_results.append(result)
    
    return unique_results

def scrape_with_direct_method():
    """Scrape using direct web scraping (no API keys needed) with keyword validation"""
    try:
        keywords = request.form.get('keywords', '').strip()
        locations = request.form.get('locations', '').strip()
        limit = int(request.form.get('limit', 50))
        export_format = request.form.get('export_format', 'csv')
        extract_emails_enabled = request.form.get('extract_emails', 'off') == 'on'
        source_mode = request.form.get('source_mode', 'all')  # 'all', 'linkedin', 'github', 'google'
        scrape_type = request.form.get('scrape_type', 'profiles')  # 'profiles', 'companies', 'products', 'general'
        
        if not keywords:
            return jsonify({'error': 'Search terms are required'}), 400
        
        # Initialize direct scraper
        direct_scraper = DirectWebScraper(headless=True, slow_mo=100)
        direct_scraper.start_browser()
        
        try:
            # Scrape based on type and source selection
            if scrape_type == 'profiles':
                results = direct_scraper.scrape_profiles(
                    keywords=keywords,
                    locations=locations,
                    max_results=limit,
                    extract_emails=extract_emails_enabled,
                    source=source_mode
                )
            elif scrape_type == 'companies':
                results = direct_scraper.scrape_companies(
                    keywords=keywords,
                    locations=locations,
                    max_results=limit,
                    source=source_mode
                )
            elif scrape_type == 'products':
                results = direct_scraper.scrape_products(
                    keywords=keywords,
                    locations=locations,
                    max_results=limit,
                    source=source_mode
                )
            else:  # general
                results = direct_scraper.scrape_general(
                    keywords=keywords,
                    locations=locations,
                    max_results=limit,
                    source=source_mode
                )
            
            if not results:
                return jsonify({'error': f'No relevant {scrape_type} found matching your search terms. Try different keywords or check if content exists.'}), 404
            
            # Export results
            return export_results(results, export_format)
            
        finally:
            direct_scraper.stop_browser()
            
    except Exception as e:
        return jsonify({'error': f'Direct scraping error: {str(e)}'}), 500

def export_results(results, export_format):
    """Export results in requested format"""
    if export_format == 'json':
        output = io.BytesIO()
        json_data = json.dumps(results, indent=2, ensure_ascii=False)
        output.write(json_data.encode('utf-8'))
        output.seek(0)
        return send_file(
            output,
            mimetype='application/json',
            as_attachment=True,
            download_name='profiles.json'
        )
    elif export_format == 'excel':
        try:
            import pandas as pd
            import openpyxl
            df = pd.DataFrame(results)
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name='Profiles')
            output.seek(0)
            return send_file(
                output,
                mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                as_attachment=True,
                download_name='profiles.xlsx'
            )
        except ImportError:
            export_format = 'csv'
    
    # Default: CSV export
    output = io.StringIO()
    fieldnames = ["name", "job_title", "company", "email", "profile_url", "snippet", "source", "profile_type", "title", "relevance_score", "relevance_reason"]
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(results)
    output.seek(0)
    
    return send_file(
        io.BytesIO(output.getvalue().encode('utf-8')),
        mimetype='text/csv',
        as_attachment=True,
        download_name='profiles.csv'
    )

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/scrape', methods=['POST'])
def scrape_profiles():
    try:
        # Check if using direct scraper (no API keys needed)
        use_direct_scraper = request.form.get('use_direct_scraper', 'off') == 'on'
        
        if use_direct_scraper and DIRECT_SCRAPER_AVAILABLE:
            # Use direct scraper - pure code, no API keys
            return scrape_with_direct_method()
        
        # Fallback to Google API method (original)
        # Get credentials - check config file first, then form
        use_saved_creds = request.form.get('use_saved_creds', 'off') == 'on'
        
        if use_saved_creds and CONFIG_AVAILABLE:
            # Use credentials from config file
            api_key_obj = config.get_available_key()
            if not api_key_obj:
                return jsonify({'error': 'No available API keys found in config. Please check config.env or use direct scraper (no API keys needed).'}), 400
            api_key = api_key_obj['api_key']
            cx = api_key_obj['cse_id']
            current_key_obj = api_key_obj
        else:
            # Use credentials from form
            api_key = request.form.get('api_key', '').strip()
            cx = request.form.get('cx', '').strip()
            current_key_obj = None
            
            # Validation
            if not api_key or not cx:
                return jsonify({'error': 'API Key and CSE ID are required. Or enable "Direct Scraper" mode (no API keys needed).'}), 400
        
        keywords = request.form.get('keywords', '').strip()
        locations = request.form.get('locations', '').strip()
        keyword_operator = request.form.get('keyword_operator', 'OR')
        location_operator = request.form.get('location_operator', 'OR')
        limit = int(request.form.get('limit', 50))
        export_format = request.form.get('export_format', 'csv')
        extract_emails_enabled = request.form.get('extract_emails', 'off') == 'on'
        enable_key_rotation = request.form.get('enable_key_rotation', 'off') == 'on'
        enable_advanced_scraping = request.form.get('enable_advanced_scraping', 'off') == 'on'
        target_individuals = request.form.get('target_individuals', 'on') == 'on'  # Default to targeting individuals
        
        # Initialize advanced scraper if enabled
        advanced_scraper = None
        if enable_advanced_scraping and ADVANCED_SCRAPER_AVAILABLE and extract_emails_enabled:
            try:
                advanced_scraper = AdvancedProfileScraper(headless=True, slow_mo=100)
                advanced_scraper.start_browser()
                print("✅ Advanced browser automation started")
            except Exception as e:
                print(f"⚠️  Failed to start advanced scraper: {e}")
                enable_advanced_scraping = False
        
        # Validation
        if not keywords:
            return jsonify({'error': 'Keywords are required'}), 400
        
        # Build query - target individuals but not too restrictive
        # Use strict_mode=False to get more results
        full_query = build_query(keywords, locations, keyword_operator, location_operator, target_individuals=True, strict_mode=False)
        
        if not full_query:
            return jsonify({'error': 'Invalid query'}), 400
        
        results = []
        RESULTS_PER_PAGE = 10
        max_results = min(limit, 100)  # Google API limit per key
        start = 1
        total_requests = 0
        max_requests = 10  # Google API limit: 100 results = 10 pages
        
        # API key rotation support
        api_keys_pool = []
        if enable_key_rotation and CONFIG_AVAILABLE:
            api_keys_pool = config.get_api_keys()
            if len(api_keys_pool) > 1:
                print(f"🔄 Using API key rotation with {len(api_keys_pool)} keys")
        
        while len(results) < limit and total_requests < max_requests:
            # Check if we need to rotate API keys
            if enable_key_rotation and CONFIG_AVAILABLE and api_keys_pool:
                current_key_obj = config.get_available_key()
                if not current_key_obj:
                    # All keys exhausted
                    if len(results) > 0:
                        break  # Return what we have
                    else:
                        return jsonify({'error': 'All API keys have exceeded quota. Please wait or add more keys.'}), 429
                api_key = current_key_obj['api_key']
                cx = current_key_obj['cse_id']
            
            url = "https://www.googleapis.com/customsearch/v1"
            params = {
                'key': api_key,
                'cx': cx,
                'q': full_query,
                'start': start,
                'num': RESULTS_PER_PAGE
            }
            
            try:
                resp = requests.get(url, params=params, timeout=30)
                resp.raise_for_status()
                data = resp.json()
                
                # Check for API errors
                if 'error' in data:
                    error_info = data['error']
                    error_code = error_info.get('code', 0)
                    error_msg = error_info.get('message', 'API Error')
                    
                    # Handle quota exceeded
                    if error_code == 429 or 'quota' in error_msg.lower() or 'quotaExceeded' in str(error_info):
                        if enable_key_rotation and CONFIG_AVAILABLE and api_keys_pool:
                            # Mark current key as quota exceeded and try next
                            config.mark_quota_exceeded(api_key)
                            print(f"⚠️  API key quota exceeded, rotating to next key...")
                            start = 1  # Reset to start with new key
                            continue
                        else:
                            return jsonify({'error': f'API Quota Exceeded: {error_msg}. Enable key rotation or wait 24 hours.'}), 429
                    else:
                        return jsonify({'error': f'Google API Error ({error_code}): {error_msg}'}), 400
                
                items = data.get("items", [])
                
                if not items:
                    # No more results available
                    break
                
                # Check if we've reached the API limit for this key
                total_requests += 1
                if total_requests >= max_requests:
                    # If we have more keys and need more results, rotate
                    if enable_key_rotation and CONFIG_AVAILABLE and len(api_keys_pool) > 1 and len(results) < limit:
                        print(f"📊 Reached 100 results limit for current key, rotating...")
                        start = 1
                        total_requests = 0
                        continue
                    break
                
                for item in items:
                    # Check if we have enough results
                    if len(results) >= limit:
                        break
                    
                    title = item.get("title", "")
                    link = item.get("link", "")
                    snippet = item.get("snippet", "")
                    display_link = item.get("displayLink", "")
                    
                    # Skip if essential fields are missing
                    if not title and not link:
                        continue
                    
                    # Skip obvious company/organization pages - but be less restrictive
                    link_lower = link.lower()
                    # Only skip if it's clearly a company page (not a profile)
                    if any(skip_term in link_lower for skip_term in ['/company/', '/careers/', '/jobs/', '/team/']):
                        # Skip company pages, but allow /in/ profiles
                        if '/in/' not in link_lower and '/profile/' not in link_lower and '/pub/' not in link_lower:
                            continue
                    
                    # Extract name from title
                    name = title.split(" | ")[0].split(" - ")[0].strip()
                    if not name:
                        name = title.split(" - ")[0].strip()
                    if not name:
                        name = "Unknown"  # Fallback
                    
                    # Skip if name looks like a company (has "Inc", "LLC", "Corp", etc.) - but be less strict
                    if any(term in name for term in ['Inc.', 'LLC', 'Corp.', 'Corporation', 'Company', 'Ltd.', 'Limited']):
                        # Only skip if it's clearly a company name (not a person's name with company)
                        if len(name.split()) <= 2:  # If it's short, likely a company
                            continue
                    
                    # Extract company first (needed for email inference)
                    company = extract_company(snippet)
                    job_title = extract_job_title(snippet, title)
                    
                    # Extract email - REQUIRED when email extraction is enabled
                    email = ""
                    if extract_emails_enabled:
                        # Strategy 1: Intelligent extraction from profile text
                        email = extract_email(f"{title} {snippet}", link, name, company, link)
                        
                        # Strategy 2: Try contact patterns (only if no email found)
                        if not email:
                            contact_patterns = [
                                r'contact[:\s]+([A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,})',
                                r'email[:\s]+([A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,})',
                                r'reach[:\s]+([A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,})',
                                r'mail[:\s]+([A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,})',
                            ]
                            for pattern in contact_patterns:
                                match = re.search(pattern, snippet, re.IGNORECASE)
                                if match:
                                    candidate_email = match.group(1)
                                    # Validate it's not generic
                                    if not is_generic_email(candidate_email):
                                        email = candidate_email
                                        break
                        
                        # Strategy 3: Advanced browser automation (if enabled)
                        if not email and enable_advanced_scraping and advanced_scraper:
                            try:
                                # Pass profile context for better email validation
                                advanced_result = advanced_scraper.scrape_profile_email(link, name, f"{title} {snippet}")
                                if advanced_result['success'] and advanced_result['emails']:
                                    # Filter and validate emails from advanced scraping
                                    for candidate_email in advanced_result['emails']:
                                        if not is_generic_email(candidate_email):
                                            if is_profile_specific_email(candidate_email, name, snippet):
                                                email = candidate_email
                                                print(f"✅ Found profile-specific email via advanced scraping: {email}")
                                                break
                                    # If no profile-specific email, use first non-generic
                                    if not email:
                                        for candidate_email in advanced_result['emails']:
                                            if not is_generic_email(candidate_email):
                                                email = candidate_email
                                                break
                            except Exception as e:
                                print(f"⚠️  Advanced scraping error: {e}")
                        
                        # EMAIL IS REQUIRED - skip profiles without email
                        if not email:
                            continue
                    
                    # Determine profile type
                    profile_type = "Other"
                    if is_linkedin_profile(link):
                        profile_type = "LinkedIn"
                    elif is_github_profile(link):
                        profile_type = "GitHub"
                    elif "linkedin.com" in link.lower():
                        profile_type = "LinkedIn"
                    elif "github.com" in link.lower():
                        profile_type = "GitHub"
                    
                    # Validate email matches person's name (REQUIRED for original emails)
                    if extract_emails_enabled and email:
                        email_lower = email.lower()
                        name_parts = [p.lower() for p in name.split() if len(p) > 2]
                        
                        # Check if email matches name
                        if name_parts:
                            if not any(part in email_lower for part in name_parts):
                                # Email doesn't match name - not original
                                continue
                    
                    results.append({
                        "name": name,
                        "job_title": job_title,
                        "company": company,
                        "email": email,
                        "profile_url": link,
                        "snippet": snippet,
                        "source": display_link,
                        "profile_type": profile_type,
                        "title": title,
                        "relevance_score": relevance_score if 'relevance_score' in locals() else 1.0,
                        "relevance_reason": relevance_reason if 'relevance_reason' in locals() else "Validated"
                    })
                
                # Check if we have enough results
                if len(results) >= limit:
                    break
                
                # Move to next page
                start += RESULTS_PER_PAGE
                
                # Rate limiting
                delay = config.rate_limit_delay if CONFIG_AVAILABLE else 1
                time.sleep(delay)
                
            except requests.exceptions.RequestException as e:
                return jsonify({'error': f'Request failed: {str(e)}'}), 500
            except json.JSONDecodeError:
                return jsonify({'error': 'Invalid response from Google API'}), 500
        
        # Clean up advanced scraper if used
        if advanced_scraper:
            try:
                advanced_scraper.stop_browser()
                print("✅ Advanced scraper stopped")
            except Exception as e:
                print(f"⚠️  Error stopping advanced scraper: {e}")
        
        # Deduplicate results
        results = deduplicate_results(results)
        
        # When email extraction is enabled, all results should have emails (filtered during collection)
        # But double-check to ensure all have emails
        if extract_emails_enabled:
            results = [r for r in results if r.get('email', '').strip()]
        
        # Limit results to requested amount
        results = results[:limit]
        
        if not results:
            error_msg = 'No results found with email addresses.'
            if extract_emails_enabled:
                error_msg += '\n\nEmail extraction is enabled - only profiles with emails are included.'
            error_msg += '\n\nSuggestions:\n'
            error_msg += '1. Try broader keywords (e.g., "engineer" instead of "RFID engineer")\n'
            error_msg += '2. Remove location filters\n'
            error_msg += '3. Try different search terms\n'
            error_msg += '4. Check if your Google API key and CSE ID are correct\n'
            error_msg += '5. Try disabling email requirement temporarily to see if profiles are found'
            return jsonify({'error': error_msg}), 404
        
        # Export in requested format
        if export_format == 'json':
            output = io.BytesIO()
            json_data = json.dumps(results, indent=2, ensure_ascii=False)
            output.write(json_data.encode('utf-8'))
            output.seek(0)
            return send_file(
                output,
                mimetype='application/json',
                as_attachment=True,
                download_name='profiles.json'
            )
        elif export_format == 'excel':
            try:
                import pandas as pd
                import openpyxl
                df = pd.DataFrame(results)
                output = io.BytesIO()
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    df.to_excel(writer, index=False, sheet_name='Profiles')
                output.seek(0)
                return send_file(
                    output,
                    mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                    as_attachment=True,
                    download_name='profiles.xlsx'
                )
            except ImportError:
                # Fallback to CSV if pandas/openpyxl not available
                return jsonify({'error': 'Excel export requires pandas and openpyxl. Install with: pip install pandas openpyxl'}), 400
        
        # Default: CSV export
        output = io.StringIO()
        fieldnames = ["name", "job_title", "company", "email", "profile_url", "snippet", "source", "profile_type", "title"]
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)
        output.seek(0)
        
        return send_file(
            io.BytesIO(output.getvalue().encode('utf-8')),
            mimetype='text/csv',
            as_attachment=True,
            download_name='profiles.csv'
        )
        
    except ValueError as e:
        return jsonify({'error': f'Invalid input: {str(e)}'}), 400
    except Exception as e:
        return jsonify({'error': f'Unexpected error: {str(e)}'}), 500

@app.route('/preview', methods=['POST'])
def preview_query():
    """Preview the query that will be built"""
    try:
        keywords = request.form.get('keywords', '').strip()
        locations = request.form.get('locations', '').strip()
        keyword_operator = request.form.get('keyword_operator', 'OR')
        location_operator = request.form.get('location_operator', 'OR')
        
        # Always target individuals for preview (not strict mode)
        query = build_query(keywords, locations, keyword_operator, location_operator, target_individuals=True, strict_mode=False)
        
        return jsonify({
            'query': query,
            'keyword_count': len([k for k in keywords.splitlines() if k.strip()]),
            'location_count': len([l for l in locations.splitlines() if l.strip()])
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5001)
