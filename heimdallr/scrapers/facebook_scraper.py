"""
Facebook scraper for facial recognition search (Law Enforcement Use)
"""

import re
import json
import time
from typing import Dict, List, Any, Optional
from urllib.parse import quote_plus, urljoin
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

from .base_scraper import BaseScraper
from ..core.face_detector import FaceDetector

class FacebookScraper(BaseScraper):
    """Facebook platform scraper for law enforcement investigations"""
    
    def __init__(self, config, aggressive_mode: bool = False):
        super().__init__(config, aggressive_mode)
        self.face_detector = FaceDetector()
        self.driver = None
        self._setup_selenium()
    
    def _setup_selenium(self):
        """Setup Selenium WebDriver for Facebook scraping"""
        try:
            chrome_options = Options()
            
            # Headless mode
            if self.config.get("scraping.headless_browser", True):
                chrome_options.add_argument("--headless")
            
            # Anti-detection measures
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
            # User agent
            user_agent = self._get_headers()["User-Agent"]
            chrome_options.add_argument(f"--user-agent={user_agent}")
            
            # Initialize driver
            self.driver = webdriver.Chrome(
                service=webdriver.chrome.service.Service(ChromeDriverManager().install()),
                options=chrome_options
            )
            
            # Execute script to remove webdriver property
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
        except Exception as e:
            self.logger.error(f"Failed to setup Selenium for Facebook: {str(e)}")
            self.driver = None
    
    def search_face(self, face_data: Dict[str, Any], leads: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Search for face matches on Facebook.
        If leads (URLs) are provided, it will navigate to them directly.
        """
        if not self.driver:
            return self._handle_search_error(
                Exception("Selenium driver not available"),
                "Facebook search initialization"
            )
        
        try:
            self._log_search_attempt("Face Search", "Facebook public content")
            
            matches = []

            # --- Targeted Search Logic ---
            if leads and leads.get("profile_urls"):
                self.logger.info("Conducting targeted search on Facebook using URL leads.")
                for url in leads["profile_urls"]:
                    if "facebook.com" in url:
                        try:
                            self.logger.info(f"Navigating to Facebook URL lead: {url}")
                            self.driver.get(url)
                            time.sleep(5) # Allow page to load
                            # Scrape the page for images to analyze
                            img_elements = self.driver.find_elements(By.TAG_NAME, "img")
                            for img in img_elements[:15]: # Limit analysis
                                matches.extend(self._analyze_image_url(img.get_attribute("src"), face_data, "profile_lead"))
                        except Exception as e:
                            self.logger.warning(f"Failed to process Facebook URL {url}: {e}")

            # --- Broad Search Logic ---
            search_methods = [
                self._search_public_posts,
                self._search_public_pages,
                self._search_marketplace
            ]
            
            for search_method in search_methods:
                try:
                    method_matches = search_method(face_data)
                    matches.extend(method_matches)
                    
                    if not self.aggressive_mode:
                        time.sleep(10)  # Longer pauses for Facebook
                        
                except Exception as e:
                    self.logger.warning(f"Facebook search method failed: {str(e)}")
                    continue
            
            # Process results
            unique_matches = self._deduplicate_matches(matches)
            unique_matches.sort(key=lambda x: x["similarity_score"], reverse=True)
            
            return {
                "platform": "facebook",
                "status": "success",
                "matches": unique_matches,
                "total_found": len(unique_matches),
                "search_time": time.time()
            }
            
        except Exception as e:
            return self._handle_search_error(e, "Facebook face search")
        finally:
            if self.driver:
                try:
                    self.driver.quit()
                except:
                    pass
    
    def _search_public_posts(self, face_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Search Facebook public posts for matching faces"""
        matches = []
        
        try:
            self.logger.info("🔍 Searching Facebook public posts")
            
            # Navigate to Facebook (public search)
            search_url = "https://www.facebook.com/search/photos-of"
            self.driver.get(search_url)
            
            WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            self.logger.warning("⚠️  Facebook requires authentication for most content")
            
            img_elements = self.driver.find_elements(By.TAG_NAME, "img")
            
            for img in img_elements[:10]:
                try:
                    img_url = img.get_attribute("src")
                    if img_url and "profile" in img_url.lower():
                        match_data = self._analyze_image_url(img_url, face_data, "profile")
                        if match_data:
                            matches.append(match_data)
                except Exception as e:
                    continue
        
        except Exception as e:
            self.logger.debug(f"Facebook public posts search failed: {str(e)}")
        
        return matches
    
    def _search_public_pages(self, face_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Search Facebook public pages for matching faces"""
        matches = []
        
        try:
            self.logger.info("📄 Searching Facebook public pages")
            
            search_terms = ["community", "local", "news", "public"]
            
            for term in search_terms:
                try:
                    search_url = f"https://www.facebook.com/search/pages/?q={quote_plus(term)}"
                    self.driver.get(search_url)
                    time.sleep(5)
                    
                    img_elements = self.driver.find_elements(By.CSS_SELECTOR, "img[src*='profile']")
                    
                    for img in img_elements[:5]:
                        try:
                            img_url = img.get_attribute("src")
                            if img_url:
                                match_data = self._analyze_image_url(img_url, face_data, "page profile")
                                if match_data:
                                    matches.append(match_data)
                        except Exception:
                            continue
                
                except Exception as e:
                    self.logger.debug(f"Page search failed for term '{term}': {str(e)}")
                    continue
        
        except Exception as e:
            self.logger.debug(f"Facebook pages search failed: {str(e)}")
        
        return matches
    
    def _search_marketplace(self, face_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Search Facebook Marketplace for profile photos in listings"""
        matches = []
        
        try:
            self.logger.info("🛒 Searching Facebook Marketplace")
            
            marketplace_url = "https://www.facebook.com/marketplace"
            self.driver.get(marketplace_url)
            time.sleep(5)
            
            profile_imgs = self.driver.find_elements(By.CSS_SELECTOR, "img[data-imgperflogname*='profile']")
            
            for img in profile_imgs[:10]:
                try:
                    img_url = img.get_attribute("src")
                    if img_url:
                        match_data = self._analyze_image_url(img_url, face_data, "marketplace seller")
                        if match_data:
                            matches.append(match_data)
                except Exception:
                    continue
        
        except Exception as e:
            self.logger.debug(f"Facebook Marketplace search failed: {str(e)}")
        
        return matches
    
    def _analyze_image_url(self, image_url: str, face_data: Dict[str, Any], 
                          context: str) -> Optional[List[Dict[str, Any]]]:
        """
        Analyze a single image URL for face matches. Returns a list of matches.
        """
        matches = []
        if not image_url:
            return matches

        try:
            image_data = self._download_image(image_url)
            if not image_data:
                return matches
            
            found_encodings = self.face_detector.extract_face_from_url_image(
                image_url, image_data
            )
            
            if not found_encodings:
                return matches
            
            target_encoding = face_data["encoding"]
            comparisons = self.face_detector.compare_faces(target_encoding, found_encodings)
            
            for comparison in comparisons:
                if comparison["is_match"]:
                    matches.append(self._create_match_result(
                        similarity_score=comparison["similarity_score"],
                        url=self.driver.current_url,
                        image_url=image_url,
                        context=f"Facebook {context}",
                        additional_info={
                            "discovery_method": "selenium_scraping",
                            "page_title": self.driver.title if self.driver else "",
                            "timestamp": time.time()
                        }
                    ))
            return matches
        
        except Exception as e:
            self.logger.debug(f"Error analyzing Facebook image: {str(e)}")
            return matches
    
    def _deduplicate_matches(self, matches: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate matches based on image URL"""
        seen_images = set()
        unique_matches = []
        
        for match in matches:
            img_url = match.get("image_url", "")
            if img_url not in seen_images:
                seen_images.add(img_url)
                unique_matches.append(match)
        
        return unique_matches