# direct_scraper.py - Scrapster Universal Scraper (No API Keys Needed)
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
import re
import time
import json
from typing import List, Dict, Set, Optional
import logging
from urllib.parse import quote, urljoin
import random

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

EMAIL_REGEX = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
GENERIC_EMAIL_PATTERNS = [
    'noreply', 'no-reply', 'donotreply', 'support@', 'info@', 'contact@', 
    'admin@', 'webmaster@', 'privacy@', 'hello@', 'mailer-', 'postmaster@',
    'sales@', 'marketing@', 'help@', 'customerservice@', 'service@',
    'broofa', 'example', 'test@', 'sample@'
]

class DirectWebScraper:
    """Pure code-based scraper - No API keys needed, just powerful code"""
    
    def __init__(self, headless=True, slow_mo=100):
        self.headless = headless
        self.slow_mo = slow_mo
        self.browser = None
        self.context = None
        self.page = None
        self.intercepted_emails: Set[str] = set()
    
    def start_browser(self):
        """Start Playwright browser"""
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(
            headless=self.headless,
            slow_mo=self.slow_mo
        )
        self.context = self.browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )
        self.page = self.context.new_page()
        self.page.on("response", self._intercept_emails)
    
    def stop_browser(self):
        """Stop browser"""
        if self.browser:
            self.browser.close()
        if hasattr(self, 'playwright'):
            self.playwright.stop()
    
    def _intercept_emails(self, response):
        """Intercept network responses to capture emails"""
        try:
            url = response.url
            if any(api in url for api in ['/api/', '/voyager/', '/graphql']):
                if response.status == 200:
                    try:
                        data = response.json()
                        text = json.dumps(data)
                        emails = EMAIL_REGEX.findall(text)
                        for email in emails:
                            if not any(pattern in email.lower() for pattern in GENERIC_EMAIL_PATTERNS):
                                self.intercepted_emails.add(email.lower())
                    except:
                        pass
        except:
            pass
    
    def _simulate_human(self, page):
        """Simulate human behavior"""
        try:
            height = page.evaluate("document.body.scrollHeight")
            for i in range(0, min(height, 2000), 200):
                page.evaluate(f"window.scrollTo(0, {i})")
                time.sleep(random.uniform(0.1, 0.3))
                page.mouse.move(random.randint(100, 500), random.randint(100, 500))
            page.evaluate("window.scrollTo(0, 0)")
            time.sleep(0.5)
        except:
            pass
    
    def search_linkedin(self, keywords: str, location: str = "", max_results: int = 50) -> List[Dict]:
        """Search LinkedIn directly without API"""
        results = []
        try:
            # Build LinkedIn search URL
            query = f"{keywords} {location}".strip()
            search_url = f"https://www.linkedin.com/search/results/people/?keywords={quote(query)}&origin=SWITCH_SEARCH_VERTICAL"
            
            logger.info(f"🔍 Searching LinkedIn: {query}")
            self.page.goto(search_url, wait_until='networkidle', timeout=30000)
            time.sleep(3)
            
            # Simulate human behavior
            self._simulate_human(self.page)
            
            # Extract profile links
            profile_links = self.page.query_selector_all('a[href*="/in/"]:not([href*="detail/recent-activity"])')
            
            for link_elem in profile_links[:max_results]:
                try:
                    href = link_elem.get_attribute("href")
                    if href and "/in/" in href:
                        profile_url = f"https://www.linkedin.com{href.split('?')[0]}"
                        
                        # Try to get name from link text or nearby
                        try:
                            name = link_elem.inner_text().strip()
                            if not name or len(name) < 3:
                                # Try to find name in parent element
                                parent = link_elem.evaluate_handle("el => el.closest('div')")
                                if parent:
                                    name = parent.inner_text().strip().split('\n')[0]
                        except:
                            name = "Unknown"
                        
                        if profile_url not in [r.get('profile_url', '') for r in results]:
                            results.append({
                                'name': name,
                                'profile_url': profile_url,
                                'source': 'linkedin.com',
                                'profile_type': 'LinkedIn'
                            })
                except:
                    continue
            
            logger.info(f"✅ Found {len(results)} LinkedIn profiles")
            return results
            
        except Exception as e:
            logger.error(f"Error searching LinkedIn: {e}")
            return []
    
    def search_github(self, keywords: str, max_results: int = 50) -> List[Dict]:
        """Search GitHub directly"""
        results = []
        try:
            query = quote(keywords)
            search_url = f"https://github.com/search?q={query}&type=Users"
            
            logger.info(f"🔍 Searching GitHub: {keywords}")
            self.page.goto(search_url, wait_until='networkidle', timeout=30000)
            time.sleep(2)
            
            self._simulate_human(self.page)
            
            # Extract profile links
            profile_links = self.page.query_selector_all('a[href^="/"]')
            
            for link_elem in profile_links[:max_results]:
                try:
                    href = link_elem.get_attribute("href")
                    if href and href.startswith("/") and not href.startswith("/search") and not href.startswith("/settings"):
                        # Check if it looks like a profile
                        parts = href.strip("/").split("/")
                        if len(parts) == 1 and parts[0] and not any(char in parts[0] for char in ['?', '=', '&']):
                            profile_url = f"https://github.com{href}"
                            name = link_elem.inner_text().strip() or parts[0]
                            
                            if profile_url not in [r.get('profile_url', '') for r in results]:
                                results.append({
                                    'name': name,
                                    'profile_url': profile_url,
                                    'source': 'github.com',
                                    'profile_type': 'GitHub'
                                })
                except:
                    continue
            
            logger.info(f"✅ Found {len(results)} GitHub profiles")
            return results
            
        except Exception as e:
            logger.error(f"Error searching GitHub: {e}")
            return []
    
    def search_google_direct(self, keywords: str, location: str = "", max_results: int = 50) -> List[Dict]:
        """Search Google directly without API"""
        results = []
        try:
            query = f"{keywords} {location}".strip()
            search_url = f"https://www.google.com/search?q={quote(query)}+site:linkedin.com/in+OR+site:github.com"
            
            logger.info(f"🔍 Searching Google: {query}")
            self.page.goto(search_url, wait_until='networkidle', timeout=30000)
            time.sleep(2)
            
            self._simulate_human(self.page)
            
            # Extract search results
            result_elements = self.page.query_selector_all('a[href*="linkedin.com/in"], a[href*="github.com"]')
            
            for elem in result_elements[:max_results]:
                try:
                    href = elem.get_attribute("href")
                    if href:
                        # Extract actual URL (Google adds tracking)
                        if "/url?q=" in href:
                            actual_url = href.split("/url?q=")[1].split("&")[0]
                        else:
                            actual_url = href
                        
                        # Validate it's a profile URL
                        if "linkedin.com/in" in actual_url or "github.com" in actual_url:
                            name = elem.inner_text().strip()
                            if not name:
                                # Try to find name in parent
                                try:
                                    parent = elem.evaluate_handle("el => el.closest('h3')")
                                    if parent:
                                        name = parent.inner_text().strip()
                                except:
                                    name = actual_url.split("/")[-1]
                            
                            profile_type = "LinkedIn" if "linkedin.com" in actual_url else "GitHub"
                            
                            if actual_url not in [r.get('profile_url', '') for r in results]:
                                results.append({
                                    'name': name,
                                    'profile_url': actual_url.split('?')[0],
                                    'source': actual_url.split('/')[2],
                                    'profile_type': profile_type
                                })
                except:
                    continue
            
            logger.info(f"✅ Found {len(results)} profiles from Google")
            return results
            
        except Exception as e:
            logger.error(f"Error searching Google: {e}")
            return []
    
    def extract_profile_data(self, profile_url: str, name: str = "") -> Dict:
        """Extract full profile data including email"""
        try:
            logger.info(f"📧 Extracting data from: {profile_url}")
            self.page.goto(profile_url, wait_until='networkidle', timeout=30000)
            time.sleep(2)
            
            self._simulate_human(self.page)
            
            # Extract page content
            content = self.page.content()
            text_content = self.page.evaluate("document.body.innerText")
            
            # Extract email
            emails = EMAIL_REGEX.findall(text_content)
            email = ""
            for e in emails:
                if not any(pattern in e.lower() for pattern in GENERIC_EMAIL_PATTERNS):
                    # Check if email matches name
                    if name:
                        name_parts = [p.lower() for p in name.split() if len(p) > 2]
                        if any(part in e.lower() for part in name_parts):
                            email = e
                            break
                    else:
                        email = e
                        break
            
            # If no email found, check intercepted emails
            if not email and self.intercepted_emails:
                email = list(self.intercepted_emails)[0]
            
            # Extract job title
            job_title = ""
            try:
                # Try to find job title in common patterns
                title_patterns = [
                    r'(?:at|@|from)\s+([A-Z][a-zA-Z\s&]+?)(?:\s|,|\.|$)',
                    r'(?:Senior|Junior|Lead|Principal|Staff)?\s*(?:Software|Hardware|Embedded|IoT|RF|Wireless|Systems)?\s*(?:Engineer|Developer|Architect|Specialist|Consultant|Manager|Director)',
                ]
                for pattern in title_patterns:
                    match = re.search(pattern, text_content, re.IGNORECASE)
                    if match:
                        job_title = match.group(0).strip()
                        break
            except:
                pass
            
            # Extract company
            company = ""
            try:
                company_patterns = [
                    r'at\s+([A-Z][a-zA-Z0-9\s&,.-]+?)(?:\s|,|\.|$)',
                    r'@\s*([A-Z][a-zA-Z0-9\s&,.-]+?)(?:\s|,|\.|$)',
                ]
                for pattern in company_patterns:
                    match = re.search(pattern, text_content, re.IGNORECASE)
                    if match:
                        company = match.group(1).strip()
                        break
            except:
                pass
            
            # Extract snippet (first 200 chars of text)
            snippet = text_content[:200].strip()
            
            return {
                'name': name or "Unknown",
                'email': email,
                'job_title': job_title,
                'company': company,
                'profile_url': profile_url,
                'snippet': snippet,
                'source': profile_url.split('/')[2],
                'profile_type': 'LinkedIn' if 'linkedin.com' in profile_url else ('GitHub' if 'github.com' in profile_url else 'Other'),
                'title': name or profile_url.split('/')[-1]
            }
            
        except Exception as e:
            logger.error(f"Error extracting profile data: {e}")
            return {
                'name': name or "Unknown",
                'email': "",
                'job_title': "",
                'company': "",
                'profile_url': profile_url,
                'snippet': "",
                'source': profile_url.split('/')[2] if '/' in profile_url else "",
                'profile_type': 'Other',
                'title': name or "Unknown"
            }
    
    def scrape_profiles(self, keywords: str, locations: str = "", max_results: int = 50, extract_emails: bool = True, source: str = "all") -> List[Dict]:
        """
        Main scraping method - combines all sources with keyword validation
        
        Args:
            keywords: Search keywords
            locations: Location filters
            max_results: Maximum results to return
            extract_emails: Whether to extract emails
            source: "all" or "linkedin" - which source to use
        """
        all_profiles = []
        
        # Import keyword validator
        try:
            from keyword_validator import KeywordRelevanceValidator
            keyword_list = [k.strip() for k in keywords.splitlines() if k.strip()]
            validator = KeywordRelevanceValidator(keyword_list)
        except:
            validator = None
        
        # Search multiple sources based on selection
        logger.info(f"🚀 Starting search (source: {source})...")
        
        if source == "linkedin" or source == "all":
            # 1. Search LinkedIn
            linkedin_profiles = self.search_linkedin(keywords, locations, max_results if source == "linkedin" else max_results // 3)
            all_profiles.extend(linkedin_profiles)
        
        if source == "all":
            # 2. Search GitHub
            github_profiles = self.search_github(keywords, max_results // 3)
            all_profiles.extend(github_profiles)
            
            # 3. Search Google (for additional sources)
            google_profiles = self.search_google_direct(keywords, locations, max_results // 3)
            all_profiles.extend(google_profiles)
        
        # Deduplicate by URL
        seen_urls = set()
        unique_profiles = []
        for profile in all_profiles:
            url = profile.get('profile_url', '')
            if url and url not in seen_urls:
                seen_urls.add(url)
                unique_profiles.append(profile)
        
        # Limit results
        unique_profiles = unique_profiles[:max_results]
        
        # Extract detailed data for each profile
        logger.info(f"📊 Extracting detailed data for {len(unique_profiles)} profiles...")
        detailed_results = []
        
        for i, profile in enumerate(unique_profiles):
            try:
                logger.info(f"[{i+1}/{len(unique_profiles)}] Processing: {profile.get('name', 'Unknown')}")
                detailed_data = self.extract_profile_data(
                    profile['profile_url'],
                    profile.get('name', '')
                )
                
                # Validate keyword relevance
                if validator:
                    validation = validator.validate_profile(
                        name=detailed_data.get('name', ''),
                        profile_text=detailed_data.get('snippet', '') + " " + detailed_data.get('job_title', ''),
                        title=detailed_data.get('title', ''),
                        job_title=detailed_data.get('job_title', ''),
                        company=detailed_data.get('company', ''),
                        url=detailed_data.get('profile_url', '')
                    )
                    
                    if not validation['is_valid']:
                        logger.info(f"  ⚠️  Profile not relevant to keywords (score: {validation['score']:.2f}, reason: {validation['reason']})")
                        continue
                    
                    # Add validation info to profile
                    detailed_data['relevance_score'] = validation['score']
                    detailed_data['relevance_reason'] = validation['reason']
                    detailed_data['confidence'] = validation['confidence']
                
                # Validate email is original/personal (not generic)
                email = detailed_data.get('email', '')
                if extract_emails and email:
                    email_lower = email.lower()
                    
                    # Skip generic emails
                    if any(pattern in email_lower for pattern in GENERIC_EMAIL_PATTERNS):
                        logger.info(f"  ⚠️  Generic email found ({email}), skipping...")
                        continue
                    
                    # Check if email matches person's name (REQUIRED for original emails)
                    name = detailed_data.get('name', '')
                    if name and name != "Unknown":
                        name_parts = [p.lower() for p in name.split() if len(p) > 2]
                        if name_parts:
                            if not any(part in email_lower for part in name_parts):
                                # Email doesn't match name - not original
                                logger.info(f"  ⚠️  Email doesn't match name ({email} for {name}), skipping...")
                                continue
                    else:
                        # No valid name - skip
                        logger.info(f"  ⚠️  No valid name found, skipping...")
                        continue
                
                # If email extraction is required, skip if no email
                if extract_emails and not detailed_data.get('email'):
                    logger.info(f"  ⚠️  No email found, skipping...")
                    continue
                
                detailed_results.append(detailed_data)
                
                # Rate limiting
                time.sleep(random.uniform(1, 2))
                
            except Exception as e:
                logger.error(f"Error processing profile: {e}")
                continue
        
        logger.info(f"✅ Scraping complete: {len(detailed_results)} profiles with emails")
        return detailed_results

