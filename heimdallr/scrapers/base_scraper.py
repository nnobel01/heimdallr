"""
Base scraper class for all platform scrapers
"""

import time
import random
import requests
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from fake_useragent import UserAgent
import logging

from ..utils.config import Config
from ..utils.logger import get_logger

logger = get_logger()

class BaseScraper(ABC):
    """Abstract base class for all platform scrapers"""
    
    def __init__(self, config: Config, aggressive_mode: bool = False):
        """
        Initialize base scraper
        
        Args:
            config: Configuration object
            aggressive_mode: Enable aggressive scraping (higher risk)
        """
        self.config = config
        self.aggressive_mode = aggressive_mode
        self.logger = logger
        self.platform_name = self.__class__.__name__.replace('Scraper', '').lower()
        
        # Rate limiting
        self.rate_limits = config.get_rate_limit(self.platform_name)
        self.last_request_time = 0
        
        # User agent rotation
        self.ua = UserAgent()
        self.session = requests.Session()
        
        # Results storage
        self.found_matches = []
    
    @abstractmethod
    def search_face(self, face_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Search for the given face on this platform
        
        Args:
            face_data: Face detection data including encoding and metadata
            
        Returns:
            Dictionary containing search results and matches
        """
        pass
    
    def _get_headers(self) -> Dict[str, str]:
        """Get randomized headers for requests"""
        user_agents = self.config.get("scraping.user_agents", [])
        
        if user_agents and not self.aggressive_mode:
            user_agent = random.choice(user_agents)
        else:
            user_agent = self.ua.random
        
        return {
            'User-Agent': user_agent,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
    
    def _respect_rate_limit(self):
        """Implement rate limiting to avoid being blocked"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        min_delay = self.rate_limits["delay"]
        
        # Reduce delay in aggressive mode but not eliminate it
        if self.aggressive_mode:
            min_delay *= 0.5
        else:
            # Add random variance to appear more human
            min_delay += random.uniform(0.5, 2.0)
        
        if time_since_last < min_delay:
            sleep_time = min_delay - time_since_last
            time.sleep(sleep_time)
        
        self.last_request_time = time.time()
    
    def _make_request(self, url: str, params: Optional[Dict] = None, 
                     method: str = "GET", **kwargs) -> Optional[requests.Response]:
        """
        Make HTTP request with rate limiting and error handling
        
        Args:
            url: Target URL
            params: Query parameters
            method: HTTP method
            **kwargs: Additional request arguments
            
        Returns:
            Response object or None if failed
        """
        self._respect_rate_limit()
        
        try:
            headers = self._get_headers()
            timeout = self.config.get("scraping.timeout", 30)
            
            response = self.session.request(
                method=method,
                url=url,
                params=params,
                headers=headers,
                timeout=timeout,
                **kwargs
            )
            
            # Check for rate limiting or blocking
            if response.status_code == 429:
                self.logger.warning(f"Rate limited on {self.platform_name}")
                time.sleep(60)  # Wait 1 minute
                return None
            elif response.status_code == 403:
                self.logger.warning(f"Access denied on {self.platform_name}")
                return None
            
            response.raise_for_status()
            return response
            
        except requests.RequestException as e:
            self.logger.error(f"Request failed for {self.platform_name}: {str(e)}")
            return None
    
    def _download_image(self, image_url: str) -> Optional[bytes]:
        """
        Download image from URL
        
        Args:
            image_url: URL of the image to download
            
        Returns:
            Image data as bytes or None if failed
        """
        try:
            response = self._make_request(image_url)
            if response and response.content:
                # Check file size
                max_size = self.config.get("scraping.max_image_size_mb", 10) * 1024 * 1024
                if len(response.content) > max_size:
                    self.logger.warning(f"Image too large: {len(response.content)} bytes")
                    return None
                
                return response.content
            
        except Exception as e:
            self.logger.debug(f"Failed to download image {image_url}: {str(e)}")
        
        return None
    
    def _create_match_result(self, similarity_score: float, url: str, 
                           image_url: str, context: str = "", 
                           additional_info: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Create standardized match result
        
        Args:
            similarity_score: Facial similarity percentage (0-100)
            url: URL where the match was found
            image_url: Direct URL to the image
            context: Context description (profile photo, post, etc.)
            additional_info: Extra metadata about the match
            
        Returns:
            Standardized match dictionary
        """
        return {
            "platform": self.platform_name,
            "similarity_score": round(similarity_score, 2),
            "url": url,
            "image_url": image_url,
            "context": context,
            "timestamp": time.time(),
            "additional_info": additional_info or {},
            "verified": False  # Requires manual verification
        }
    
    def _log_search_attempt(self, search_type: str, query: str = ""):
        """Log search attempts for audit trail"""
        self.logger.info(f"🔍 {self.platform_name.title()}: {search_type} - {query}")
    
    def _handle_search_error(self, error: Exception, context: str = "") -> Dict[str, Any]:
        """
        Handle search errors consistently
        
        Args:
            error: The exception that occurred
            context: Additional context about where the error occurred
            
        Returns:
            Error result dictionary
        """
        error_msg = f"{context}: {str(error)}" if context else str(error)
        self.logger.error(f"❌ {self.platform_name.title()} error: {error_msg}")
        
        return {
            "platform": self.platform_name,
            "status": "error",
            "error": error_msg,
            "matches": [],
            "search_time": time.time()
        }
