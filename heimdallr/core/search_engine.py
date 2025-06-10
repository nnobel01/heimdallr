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
        self.scrapers = self._initialize_real_scrapers(platforms)
        # Threading for parallel searches
        self.max_workers = 6 if aggressive_mode else 3

    def _initialize_real_scrapers(self, platforms: str) -> Dict[str, Any]:
        """Initialize real scrapers"""
        scraper_map = {}

        # Determine which platforms to initialize based on the 'platforms' argument
        platform_list = []
        if platforms == "all":
            platform_list = ["instagram", "facebook", "twitter", "reddit", "google_images"]
        elif platforms == "social":
            platform_list = ["instagram", "facebook", "twitter", "reddit"]
        elif platforms == "web":
            platform_list = ["google_images"]
        else:
            platform_list = [p.strip() for p in platforms.split(',')]

        if SCRAPERS_AVAILABLE:
            if "instagram" in platform_list:
                scraper_map["instagram"] = InstagramScraper(self.config)
            if "facebook" in platform_list:
                scraper_map["facebook"] = FacebookScraper(self.config)
            if "twitter" in platform_list:
                scraper_map["twitter"] = TwitterScraper(self.config)
            if "reddit" in platform_list:
                scraper_map["reddit"] = RedditScraper(self.config)
            if "google_images" in platform_list:
                scraper_map["google_images"] = GoogleImagesScraper(self.config)
        else:
            self.logger.warning("No scrapers available, operating in a dummy mode.")
            # Fallback to dummy scrapers if real ones fail to import
            for p_name in platform_list:
                scraper_map[p_name] = DummyScraper(p_name)

        return scraper_map

    def search_all_platforms(self, faces_data: Dict[str, Any],
                           progress_callback: Optional[Callable] = None) -> Dict[str, Any]:
        """
        Search across all enabled platforms using a lead-driven approach.
        It starts with a broad search on Google and then uses the leads
        from that search to perform targeted searches on other platforms.
        """
        start_time = time.time()
        results = {
            "platform_results": {},
            "search_metadata": {
                "start_time": start_time,
                "platforms_searched": list(self.scrapers.keys()),
                "aggressive_mode": self.aggressive_mode
            },
            "leads_generated": {}
        }

        if not faces_data.get("faces_found", False):
            self.logger.error("❌ No faces found to search for")
            return results

        face_to_search = faces_data["faces"][0]
        leads = {"potential_names": [], "profile_urls": []}

        # 1. Run Google reverse image search first to generate leads
        self.logger.info("🚀 Starting search with Google to generate leads...")
        google_scraper = self.scrapers.pop("google_images", None)

        if google_scraper:
            try:
                self.logger.info("🔍 Searching Google Images...")
                google_results = google_scraper.search_face(face_to_search)
                results["platform_results"]["google_images"] = google_results

                # Extract leads if the search was successful
                if google_results.get("status") == "success":
                    generated_leads = google_results.get("leads", {})
                    leads["potential_names"].extend(generated_leads.get("potential_names", []))
                    leads["profile_urls"].extend(generated_leads.get("profile_urls", []))
                    results["leads_generated"] = leads
                    self.logger.info(f"✅ Google search generated {len(leads['potential_names'])} name leads and {len(leads['profile_urls'])} URL leads.")
                if progress_callback:
                    progress_callback(25)  # Assume Google is 25% of the work
            except Exception as e:
                self.logger.error(f"❌ Google Images search failed: {str(e)}")
                results["platform_results"]["google_images"] = {"error": str(e), "matches": [], "status": "failed"}
        else:
            self.logger.warning("⚠️ Google Images scraper not available or not selected. Proceeding with broad searches.")

        # 2. Launch other scrapers in a targeted way using the generated leads
        self.logger.info("🚀 Launching targeted searches on other platforms using generated leads...")
        remaining_platforms = len(self.scrapers)
        if remaining_platforms == 0:
            self.logger.info("No other platforms to search.")
        else:
            with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                # The 'leads' dictionary is passed to each scraper
                future_to_platform = {
                    executor.submit(scraper.search_face, face_to_search, leads): platform
                    for platform, scraper in self.scrapers.items()
                }

                for i, future in enumerate(as_completed(future_to_platform)):
                    platform = future_to_platform[future]
                    try:
                        platform_results = future.result()
                        results["platform_results"][platform] = platform_results
                    except Exception as exc:
                        self.logger.error(f"❌ {platform.title()} search generated an exception: {exc}")
                        results["platform_results"][platform] = {"error": str(exc), "matches": [], "status": "failed"}

                    if progress_callback:
                        progress = 25 + ((i + 1) / remaining_platforms) * 75
                        progress_callback(progress)

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

    def search_face(self, face_data: Dict[str, Any], leads: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Dummy search that returns test results"""
        time.sleep(1)  # Simulate search time
        self.logger.info(f"Dummy searching {self.platform_name} with {len(leads.get('potential_names',[]))} name leads.")

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
            "search_time": time.time(),
            "leads": {"potential_names": ["John Smith"], "profile_urls": []} if self.platform_name == "google_images" else {}
        }