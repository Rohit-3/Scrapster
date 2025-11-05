# config.py - Configuration management
import os
from dotenv import load_dotenv

# Load environment variables from config.env file (or .env if it exists)
# Try config.env first, then fall back to .env
if os.path.exists('config.env'):
    load_dotenv('config.env')
elif os.path.exists('.env'):
    load_dotenv('.env')
else:
    load_dotenv()  # Try default .env

class Config:
    """Configuration class for managing API keys and settings"""
    
    def __init__(self):
        self.rate_limit_delay = float(os.getenv('RATE_LIMIT_DELAY', 1))
        self.auto_rotate_keys = os.getenv('AUTO_ROTATE_KEYS', 'false').lower() == 'true'
        
        # Single API key setup
        self.default_api_key = os.getenv('GOOGLE_API_KEY', '')
        self.default_cse_id = os.getenv('GOOGLE_CSE_ID', '')
        
        # Multiple API keys setup
        self.multiple_keys = self._parse_multiple_keys()
    
    def _parse_multiple_keys(self):
        """Parse multiple API keys from environment variable"""
        keys_str = os.getenv('MULTIPLE_API_KEYS', '')
        if not keys_str:
            return []
        
        keys_list = []
        for key_pair in keys_str.split(','):
            key_pair = key_pair.strip()
            if ':' in key_pair:
                api_key, cse_id = key_pair.split(':', 1)
                keys_list.append({
                    'api_key': api_key.strip(),
                    'cse_id': cse_id.strip(),
                    'quota_exceeded': False,
                    'requests_used': 0
                })
        return keys_list
    
    def get_api_keys(self):
        """Get all available API keys"""
        keys = []
        
        # Add default key if available
        if self.default_api_key and self.default_cse_id:
            keys.append({
                'api_key': self.default_api_key,
                'cse_id': self.default_cse_id,
                'quota_exceeded': False,
                'requests_used': 0
            })
        
        # Add multiple keys
        keys.extend(self.multiple_keys)
        
        return keys
    
    def get_available_key(self):
        """Get next available API key that hasn't exceeded quota"""
        keys = self.get_api_keys()
        for key_config in keys:
            if not key_config.get('quota_exceeded', False):
                return key_config
        return None
    
    def mark_quota_exceeded(self, api_key):
        """Mark an API key as quota exceeded"""
        keys = self.get_api_keys()
        for key_config in keys:
            if key_config['api_key'] == api_key:
                key_config['quota_exceeded'] = True
                break

# Global config instance
config = Config()

