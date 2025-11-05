# advanced_scraper.py - Advanced Browser Automation for Email Extraction
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
import re
import time
import json
from typing import List, Dict, Set
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

EMAIL_REGEX = re.compile(r'[\w\.-]+@[\w\.-]+\.\w+')
# Filter out common non-personal emails
EXCLUDED_EMAIL_PATTERNS = ['noreply', 'no-reply', 'donotreply', 'support@', 'info@', 'contact@', 'admin@', 'webmaster@', 'privacy@', 'hello@', 'mailer-', 'postmaster@']

class AdvancedProfileScraper:
    """Advanced browser automation scraper for extracting real emails from profiles"""
    
    def __init__(self, headless=False, slow_mo=100):
        self.headless = headless
        self.slow_mo = slow_mo
        self.intercepted_emails: Set[str] = set()
        self.browser = None
        self.context = None
        self.page = None
    
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
        
        # Set up network interception
        self.page.on("response", self._check_email_intercept)
    
    def stop_browser(self):
        """Stop browser"""
        if self.browser:
            self.browser.close()
        if hasattr(self, 'playwright'):
            self.playwright.stop()
    
    def _check_email_intercept(self, response):
        """Intercept network responses to capture emails from API calls"""
        url = response.url
        try:
            # Check LinkedIn API endpoints
            if any(api_path in url for api_path in ['/voyager/api/', '/voyager/api/', '/api/']):
                if response.status == 200:
                    try:
                        data = response.json()
                        raw_text = json.dumps(data)
                        matches = EMAIL_REGEX.findall(raw_text)
                        for email in matches:
                            email_lower = email.lower()
                            if not any(excluded in email_lower for excluded in EXCLUDED_EMAIL_PATTERNS):
                                self.intercepted_emails.add(email)
                                logger.info(f"✅ Intercepted email from API: {email}")
                    except:
                        # Try text extraction if not JSON
                        try:
                            text = response.text()
                            matches = EMAIL_REGEX.findall(text)
                            for email in matches:
                                email_lower = email.lower()
                                if not any(excluded in email_lower for excluded in EXCLUDED_EMAIL_PATTERNS):
                                    self.intercepted_emails.add(email)
                        except:
                            pass
        except Exception as e:
            logger.debug(f"Error intercepting response: {e}")
    
    def _simulate_human_behavior(self, page):
        """Simulate human-like scrolling and mouse movements"""
        try:
            # Get page height
            height = page.evaluate("document.body.scrollHeight")
            
            # Scroll gradually with pauses
            scroll_amount = 300
            current_position = 0
            
            while current_position < height:
                # Random mouse movement
                try:
                    page.mouse.move(100 + (current_position % 200), 200 + (current_position % 100))
                except:
                    pass
                
                # Scroll down
                page.evaluate(f"window.scrollTo(0, {current_position})")
                time.sleep(0.2)
                
                current_position += scroll_amount
                
                # Sometimes scroll back up a bit (human behavior)
                if current_position % 1000 == 0:
                    page.evaluate(f"window.scrollTo(0, {current_position - 200})")
                    time.sleep(0.3)
            
            # Scroll to top
            page.evaluate("window.scrollTo(0, 0)")
            time.sleep(0.5)
        except Exception as e:
            logger.debug(f"Error simulating human behavior: {e}")
    
    def _extract_emails_from_content(self, content: str) -> List[str]:
        """Extract emails from HTML/text content"""
        matches = EMAIL_REGEX.findall(content)
        emails = []
        for email in matches:
            email_lower = email.lower()
            # Filter out excluded patterns
            if not any(excluded in email_lower for excluded in EXCLUDED_EMAIL_PATTERNS):
                emails.append(email)
        return list(set(emails))  # Remove duplicates
    
    def _is_profile_specific(self, email: str, profile_name: str, context: str = "") -> bool:
        """Check if email seems specific to the profile (not generic)"""
        if not profile_name or not email:
            return False
        
        email_lower = email.lower()
        name_parts = [p.lower() for p in profile_name.split() if len(p) > 2]
        
        # Check if email contains name parts
        for part in name_parts:
            if part in email_lower:
                return True
        
        return False
    
    def _extract_from_shadow_dom(self, page) -> List[str]:
        """Try to extract emails from shadow DOM elements"""
        emails = []
        try:
            # Execute script to traverse shadow DOM
            script = """
            function extractEmailsFromShadowDOM() {
                const emails = new Set();
                const emailRegex = /[\\w\\.-]+@[\\w\\.-]+\\.[a-z]+/gi;
                
                function traverseShadowDOM(node) {
                    if (node.shadowRoot) {
                        const shadowContent = node.shadowRoot.innerHTML;
                        const matches = shadowContent.match(emailRegex);
                        if (matches) {
                            matches.forEach(m => emails.add(m.toLowerCase()));
                        }
                        // Traverse children
                        node.shadowRoot.querySelectorAll('*').forEach(child => {
                            traverseShadowDOM(child);
                        });
                    }
                    // Traverse regular children
                    node.querySelectorAll('*').forEach(child => {
                        traverseShadowDOM(child);
                    });
                }
                
                traverseShadowDOM(document.body);
                return Array.from(emails);
            }
            return extractEmailsFromShadowDOM();
            """
            shadow_emails = page.evaluate(script)
            emails.extend(shadow_emails)
        except Exception as e:
            logger.debug(f"Error extracting from shadow DOM: {e}")
        return emails
    
    def _try_contact_modal(self, page) -> List[str]:
        """Try to open contact/message modals to reveal hidden emails"""
        emails = []
        try:
            # Look for Connect/Message buttons
            selectors = [
                'button[aria-label*="Connect"]',
                'button[aria-label*="Message"]',
                'button[aria-label*="Contact"]',
                'a[href*="message"]',
                'button:has-text("Connect")',
                'button:has-text("Message")',
            ]
            
            for selector in selectors:
                try:
                    button = page.locator(selector).first
                    if button.count() > 0 and button.is_visible():
                        button.click()
                        time.sleep(2)  # Wait for modal to load
                        
                        # Extract from modal content
                        modal_content = page.content()
                        modal_emails = self._extract_emails_from_content(modal_content)
                        emails.extend(modal_emails)
                        
                        # Try to close modal
                        try:
                            close_btn = page.locator('button[aria-label*="Dismiss"], button[aria-label*="Close"], [class*="close"]').first
                            if close_btn.count() > 0:
                                close_btn.click()
                                time.sleep(0.5)
                        except:
                            # Press Escape
                            page.keyboard.press('Escape')
                            time.sleep(0.5)
                        
                        break  # Found and tried one, move on
                except:
                    continue
        except Exception as e:
            logger.debug(f"Error trying contact modal: {e}")
        return emails
    
    def scrape_profile_email(self, profile_url: str, profile_name: str = "", profile_text: str = "") -> Dict[str, any]:
        """
        Scrape a single profile for email addresses using multiple strategies with profile-specific validation
        
        Returns:
            dict with 'emails' (list), 'success' (bool), 'error' (str)
        """
        all_emails = []
        profile_specific_emails = []
        
        try:
            logger.info(f"🔍 Scraping profile: {profile_url}")
            
            # Navigate to profile
            self.page.goto(profile_url, wait_until='networkidle', timeout=30000)
            time.sleep(2)  # Let page fully load
            
            # Simulate human behavior
            self._simulate_human_behavior(self.page)
            
            # Strategy 1: Extract from page content (prioritize profile-specific areas)
            page_content = self.page.content()
            content_emails = self._extract_emails_from_content(page_content)
            
            # Try to extract from specific profile sections (avoid footer/header)
            try:
                # Look for profile-specific sections (avoid common footer/header emails)
                profile_sections = self.page.query_selector_all('section, div[class*="profile"], div[class*="about"], div[class*="contact"]')
                for section in profile_sections[:10]:  # Limit to first 10 sections
                    try:
                        section_text = section.inner_text()
                        section_emails = self._extract_emails_from_content(section_text)
                        # Prioritize emails found in profile sections
                        for email in section_emails:
                            if email not in all_emails:
                                all_emails.append(email)
                                # Check if email seems profile-specific
                                if profile_name and self._is_profile_specific(email, profile_name, section_text):
                                    profile_specific_emails.append(email)
                    except:
                        continue
            except:
                pass
            
            # Add all content emails
            all_emails.extend(content_emails)
            logger.info(f"  📧 Found {len(content_emails)} emails in page content")
            
            # Strategy 2: Extract from shadow DOM
            shadow_emails = self._extract_from_shadow_dom(self.page)
            all_emails.extend(shadow_emails)
            if shadow_emails:
                logger.info(f"  📧 Found {len(shadow_emails)} emails in shadow DOM")
            
            # Strategy 3: Try contact modals
            modal_emails = self._try_contact_modal(self.page)
            all_emails.extend(modal_emails)
            if modal_emails:
                logger.info(f"  📧 Found {len(modal_emails)} emails in modals")
            
            # Strategy 4: Include intercepted emails from network calls
            all_emails.extend(list(self.intercepted_emails))
            if self.intercepted_emails:
                logger.info(f"  📧 Found {len(self.intercepted_emails)} emails from API interception")
            
            # Clean and deduplicate
            unique_emails = list(set([e.lower().strip() for e in all_emails if e]))
            
            # Filter out excluded patterns
            final_emails = [
                e for e in unique_emails 
                if not any(excluded in e for excluded in EXCLUDED_EMAIL_PATTERNS)
            ]
            
            # Prioritize profile-specific emails
            if profile_specific_emails:
                # Remove duplicates and prioritize
                profile_specific_clean = [e.lower().strip() for e in profile_specific_emails if e.lower().strip() in final_emails]
                if profile_specific_clean:
                    # Return profile-specific emails first
                    return {
                        'emails': profile_specific_clean + [e for e in final_emails if e not in profile_specific_clean],
                        'success': len(profile_specific_clean) > 0,
                        'error': None
                    }
            
            return {
                'emails': final_emails,
                'success': len(final_emails) > 0,
                'error': None
            }
            
        except PlaywrightTimeout:
            return {
                'emails': [],
                'success': False,
                'error': 'Timeout loading profile'
            }
        except Exception as e:
            logger.error(f"Error scraping profile {profile_url}: {e}")
            return {
                'emails': [],
                'success': False,
                'error': str(e)
            }
    
    def search_profiles(self, keyword: str, location: str = "", max_results: int = 10) -> List[str]:
        """
        Search for profiles on LinkedIn (requires manual login first)
        
        Returns:
            list of profile URLs
        """
        profile_urls = []
        
        try:
            # Build search URL
            search_query = keyword.replace(' ', '%20')
            if location:
                search_query += f"%20{location.replace(' ', '%20')}"
            
            search_url = f"https://www.linkedin.com/search/results/people/?keywords={search_query}&origin=SWITCH_SEARCH_VERTICAL"
            
            logger.info(f"🔎 Searching LinkedIn: {search_url}")
            self.page.goto(search_url, wait_until='networkidle', timeout=30000)
            time.sleep(3)  # Wait for results to load
            
            # Simulate scrolling to load more results
            self._simulate_human_behavior(self.page)
            
            # Extract profile links
            profile_links = self.page.query_selector_all('a[href^="/in/"]:not([href*="detail/recent-activity"]):not([href*="voyager"])')
            
            for link in profile_links[:max_results]:
                try:
                    href = link.get_attribute("href")
                    if href and href.startswith("/in/"):
                        full_url = "https://www.linkedin.com" + href.split('?')[0]  # Remove query params
                        if full_url not in profile_urls:
                            profile_urls.append(full_url)
                except:
                    continue
            
            logger.info(f"✅ Found {len(profile_urls)} profile URLs")
            return profile_urls
            
        except Exception as e:
            logger.error(f"Error searching profiles: {e}")
            return []

