"""
Multi-platform search engine for facial recognition
"""

import time
from typing import Dict, List, Any, Optional, Callable
from concurrent.futures import ThreadPoolExecutor, as_completed

# Import scrapers with fallback handling
try:
    from ..scrapers.instagram_scraper import InstagramScraper
    from ..scrapers.facebook_scraper import FacebookScraper  
    from ..scrapers.twitter_scraper import TwitterScraper
    from ..scrapers.reddit_scraper import RedditScraper
    from ..scrapers.google_images_scraper import GoogleImagesScraper
    SCRAPERS_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Some scrapers not available: {e}")
    SCRAPERS_AVAILABLE = False

from ..utils.config import Config
from ..utils.logger import get_logger

logger = get_logger()

class SearchEngine:
    """Orchestrates searches across multiple platforms"""
    
    def __init__(self, config: Config, aggressive_mode: bool = False, platforms: str = "all"):
        """
        Initialize search engine
        
        Args:
            config: Configuration object
            aggressive_mode: Enable aggressive searching with higher risk
            platforms: Platforms to search ('all', 'social', 'web', or comma-separated list)
        """
        self.config = config
        self.aggressive_mode = aggressive_mode
        self.logger = logger
        
        # For now, create dummy scrapers for testing
        self.scrapers = self._initialize_dummy_scrapers(platforms)
        
        # Threading for parallel searches
        self.max_workers = 6 if aggressive_mode else 3
        
 #   def _initialize_dummy_scrapers(self, platforms: str) -> Dict[str, Any]:
 #       """Initialize dummy scrapers for testing"""
 #       return {
 #           "instagram": DummyScraper("instagram"),
 #           "facebook": DummyScraper("facebook"),
 #           "twitter": DummyScraper("twitter"),
 #           "reddit": DummyScraper("reddit"),
 #           "google_images": DummyScraper("google_images")
 #       }

    def _initialize_real_scrapers(self, platforms: str) -> Dict[str, Any]:
    """Initialize real scrapers"""
    scraper_map = {}

    if SCRAPERS_AVAILABLE:
        if platforms in ("all", "social"):
            scraper_map.update({
                "instagram": InstagramScraper(self.config),
                "facebook": FacebookScraper(self.config),
                "twitter": TwitterScraper(self.config),
                "reddit": RedditScraper(self.config),
            })
        if platforms in ("all", "web"):
            scraper_map["google_images"] = GoogleImagesScraper(self.config)
    else:
        self.logger.warning("No scrapers available, falling back to dummy mode.")
        return self._initialize_dummy_scrapers(platforms)

    return scraper_map
    
    def search_all_platforms(self, faces_data: Dict[str, Any], 
                           progress_callback: Optional[Callable] = None) -> Dict[str, Any]:
        """
        Search across all enabled platforms
        
        Args:
            faces_data: Face detection results from input image
            progress_callback: Function to call with progress updates
            
        Returns:
            Comprehensive search results from all platforms
        """
        start_time = time.time()
        results = {
            "platform_results": {},
            "search_metadata": {
                "start_time": time.time(),
                "platforms_searched": list(self.scrapers.keys()),
                "aggressive_mode": self.aggressive_mode
            }
        }
        
        if not faces_data.get("faces_found", False):
            self.logger.error("❌ No faces found to search for")
            return results
        
        total_platforms = len(self.scrapers)
        completed_platforms = 0
        
        self.logger.info(f"🚀 Starting search across {total_platforms} platforms...")
        
        # Simple sequential search for testing
        for platform, scraper in self.scrapers.items():
            try:
                self.logger.info(f"🔍 Searching {platform.title()}...")
                platform_results = scraper.search_face(faces_data["faces"][0])
                results["platform_results"][platform] = platform_results
                
                completed_platforms += 1
                if progress_callback:
                    progress = (completed_platforms / total_platforms) * 100
                    progress_callback(progress)
                    
            except Exception as e:
                self.logger.error(f"❌ {platform.title()} search failed: {str(e)}")
                results["platform_results"][platform] = {
                    "error": str(e),
                    "matches": [],
                    "status": "failed"
                }
        
        # Finalize results
        end_time = time.time()
        results["search_metadata"].update({
            "end_time": end_time,
            "duration_seconds": round(end_time - start_time, 2),
            "total_matches": sum(
                len(platform_data.get("matches", [])) 
                for platform_data in results["platform_results"].values()
            )
        })
        
        self.logger.info(f"🎯 Search completed in {results['search_metadata']['duration_seconds']}s")
        return results

class DummyScraper:
    """Dummy scraper for testing without real platform access"""
    
    def __init__(self, platform_name: str):
        self.platform_name = platform_name
    
    def search_face(self, face_data: Dict[str, Any]) -> Dict[str, Any]:
        """Dummy search that returns test results"""
        time.sleep(1)  # Simulate search time
        
        # Return dummy results for testing
        return {
            "platform": self.platform_name,
            "status": "success",
            "matches": [
                {
                    "platform": self.platform_name,
                    "similarity_score": 85.5,
                    "url": f"https://{self.platform_name}.com/test/123",
                    "image_url": f"https://{self.platform_name}.com/images/test.jpg",
                    "context": f"{self.platform_name} test result",
                    "timestamp": time.time(),
                    "verified": False
                }
            ],
            "total_found": 1,
            "search_time": time.time()
        }
