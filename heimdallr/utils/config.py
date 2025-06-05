"""
Configuration management for Heimdallr
"""

import os
import json
from pathlib import Path
from typing import Dict, Any, Optional

class Config:
    """Configuration manager for Heimdallr settings and API keys"""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or os.path.join(os.getcwd(), '.heimdallr_config.json')
        self.config_data = {}
        self.verbose = False
        
        # Load configuration file if exists
        if os.path.exists(self.config_path):
            self.load_config()
        else:
            self.create_default_config()
    
    def load_config(self):
        """Load configuration from file"""
        try:
            with open(self.config_path, 'r') as f:
                self.config_data = json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            self.create_default_config()
    
    def create_default_config(self):
        """Create default configuration"""
        self.config_data = {
            "platforms": {
                "instagram": {"enabled": True, "rate_limit_delay": 2.0},
                "facebook": {"enabled": True, "rate_limit_delay": 3.0},
                "twitter": {"enabled": True, "rate_limit_delay": 1.5},
                "reddit": {"enabled": True, "rate_limit_delay": 1.0},
                "google_images": {"enabled": True, "rate_limit_delay": 1.0}
            },
            "scraping": {
                "user_agents": [
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
                ],
                "timeout": 30,
                "headless_browser": True
            }
        }
        self.save_config()
    
    def save_config(self):
        """Save configuration to file"""
        with open(self.config_path, 'w') as f:
            json.dump(self.config_data, f, indent=2)
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value with dot notation support"""
        keys = key.split('.')
        value = self.config_data
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set_verbose(self, verbose: bool):
        """Enable/disable verbose logging"""
        self.verbose = verbose
    
    def get_api_key(self, service: str) -> Optional[str]:
        """Get API key for a service from environment"""
        env_key = f"{service.upper()}_API_KEY"
        return os.getenv(env_key)
    
    def is_platform_enabled(self, platform: str) -> bool:
        """Check if a platform is enabled"""
        return self.get(f"platforms.{platform}.enabled", False)
    
    def get_rate_limit(self, platform: str) -> Dict[str, float]:
        """Get rate limiting settings for a platform"""
        return {
            "delay": self.get(f"platforms.{platform}.rate_limit_delay", 2.0),
            "max_requests": 30
        }
