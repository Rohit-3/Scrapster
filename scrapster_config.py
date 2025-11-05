# scrapster_config.py - Scrapster Configuration
# Universal scraping configuration for different content types

SCRAPING_CONFIGS = {
    'profiles': {
        'description': 'Personal and professional profiles',
        'sources': ['linkedin', 'github', 'google'],
        'extract_fields': ['name', 'email', 'job_title', 'company', 'location', 'bio', 'profile_url'],
        'keywords_pattern': r'(profile|about|contact|linkedin|github)',
        'validation_keywords': ['engineer', 'developer', 'manager', 'specialist', 'consultant', 'director']
    },
    'companies': {
        'description': 'Company profiles and information',
        'sources': ['linkedin', 'google', 'crunchbase'],
        'extract_fields': ['name', 'website', 'industry', 'size', 'location', 'description', 'contact'],
        'keywords_pattern': r'(company|corporation|inc|llc|ltd|about us)',
        'validation_keywords': ['company', 'corp', 'inc', 'llc', 'business', 'organization']
    },
    'products': {
        'description': 'Product listings and information',
        'sources': ['google', 'amazon', 'ebay'],
        'extract_fields': ['name', 'price', 'description', 'rating', 'seller', 'url', 'image'],
        'keywords_pattern': r'(product|price|buy|sell|review|rating)',
        'validation_keywords': ['product', 'price', 'buy', 'sell', 'review']
    },
    'general': {
        'description': 'General web content',
        'sources': ['google', 'bing', 'duckduckgo'],
        'extract_fields': ['title', 'url', 'snippet', 'content', 'author', 'date'],
        'keywords_pattern': r'.*',
        'validation_keywords': []
    }
}

def get_config(scrape_type='profiles'):
    """Get configuration for scraping type"""
    return SCRAPING_CONFIGS.get(scrape_type, SCRAPING_CONFIGS['general'])

def get_sources(scrape_type='profiles'):
    """Get available sources for scraping type"""
    config = get_config(scrape_type)
    return config.get('sources', ['google'])

def get_extract_fields(scrape_type='profiles'):
    """Get fields to extract for scraping type"""
    config = get_config(scrape_type)
    return config.get('extract_fields', [])

