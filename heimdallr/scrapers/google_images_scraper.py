"""
Google Images reverse search scraper for facial recognition (Law Enforcement Use)
"""

import time
import re
import base64
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

class GoogleImagesScraper(BaseScraper):
    """Google Images reverse search scraper for law enforcement investigations"""
    
    def __init__(self, config, aggressive_mode: bool = False):
        super().__init__(config, aggressive_mode)
        self.face_detector = FaceDetector()
        self.driver = None
        self._setup_selenium()
    
    def _setup_selenium(self):
        """Setup Selenium WebDriver for Google Images"""
        try:
            chrome_options = Options()
            
            # Headless mode
            if self.config.get("scraping.headless_browser", True):
                chrome_options.add_argument("--headless")
            
            # Performance and stealth options
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
            # User agent
            user_agent = self._get_headers()["User-Agent"]
            chrome_options.add_argument(f"--user-agent={user_agent}")
            
            # Additional options for Google
            chrome_options.add_argument("--disable-extensions")
            chrome_options.add_argument("--disable-plugins")
            chrome_options.add_argument("--disable-images")  # Faster loading
            
            # Initialize driver
            self.driver = webdriver.Chrome(
                service=webdriver.chrome.service.Service(ChromeDriverManager().install()),
                options=chrome_options
            )
            
            # Remove webdriver property
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
        except Exception as e:
            self.logger.error(f"Failed to setup Selenium for Google Images: {str(e)}")
            self.driver = None
    
    def search_face(self, face_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Search for face matches using Google Images reverse search
        
        Args:
            face_data: Face detection data with encoding
            
        Returns:
            Dictionary with search results and matches
        """
        if not self.driver:
            return self._handle_search_error(
                Exception("Selenium driver not available"),
                "Google Images search initialization"
            )
        
        try:
            self._log_search_attempt("Reverse Image Search", "Google Images")
            
            matches = []
            search_methods = [
                self._reverse_image_search,
                self._similar_images_search,
                self._related_searches
            ]
            
            # Execute search methods
            for search_method in search_methods:
                try:
                    method_matches = search_method(face_data)
                    matches.extend(method_matches)
                    
                    if not self.aggressive_mode:
                        time.sleep(5)  # Pause between methods
                        
                except Exception as e:
                    self.logger.warning(f"Google Images search method failed: {str(e)}")
                    continue
            
            # Process results
            unique_matches = self._deduplicate_matches(matches)
            unique_matches.sort(key=lambda x: x["similarity_score"], reverse=True)
            
            return {
                "platform": "google_images",
                "status": "success",
                "matches": unique_matches,
                "total_found": len(unique_matches),
                "search_time": time.time()
            }
            
        except Exception as e:
            return self._handle_search_error(e, "Google Images face search")
        finally:
            # Clean up
            if self.driver:
                try:
                    self.driver.quit()
                except:
                    pass
    
    def _reverse_image_search(self, face_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Perform reverse image search using the face crop"""
        matches = []
        
        try:
            self.logger.info("🔍 Performing Google reverse image search")
            
            # Get face crop image path
            face_crop_path = face_data.get("face_crop_path")
            if not face_crop_path:
                return matches
            
            # Navigate to Google Images
            self.driver.get("https://images.google.com")
            
            # Wait for page load
            WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='file']"))
            )
            
            # Click camera icon for image upload
            camera_button = self.driver.find_element(By.CSS_SELECTOR, "[aria-label*='camera']")
            camera_button.click()
            
            time.sleep(2)
            
            # Upload image file
            file_input = self.driver.find_element(By.CSS_SELECTOR, "input[type='file']")
            file_input.send_keys(face_crop_path)
            
            # Wait for search results
            WebDriverWait(self.driver, 30).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "[data-ri]"))
            )
            
            time.sleep(5)  # Allow results to load
            
            # Extract search results
            result_matches = self._extract_search_results(face_data)
            matches.extend(result_matches)
            
        except Exception as e:
            self.logger.error(f"Reverse image search failed: {str(e)}")
        
        return matches
    
    def _similar_images_search(self, face_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Search for visually similar images"""
        matches = []
        
        try:
            self.logger.info("🔍 Searching for visually similar images")
            
            # Look for "Visually similar images" section
            try:
                similar_link = self.driver.find_element(
                    By.XPATH, "//a[contains(text(), 'Visually similar')]"
                )
                similar_link.click()
                
                time.sleep(5)
                
                # Extract similar image results
                similar_matches = self._extract_similar_images(face_data)
                matches.extend(similar_matches)
                
            except Exception:
                self.logger.debug("No visually similar images section found")
        
        except Exception as e:
            self.logger.debug(f"Similar images search failed: {str(e)}")
        
        return matches
    
    def _related_searches(self, face_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Search using Google's suggested related searches"""
        matches = []
        
        try:
            self.logger.info("🔍 Following related search suggestions")
            
            # Look for related search suggestions
            try:
                related_searches = self.driver.find_elements(
                    By.CSS_SELECTOR, "[data-lpage] a"
                )
                
                for search_link in related_searches[:3]:  # Limit to first 3
                    try:
                        search_text = search_link.text
                        if search_text and any(keyword in search_text.lower() 
                                             for keyword in ["person", "people", "face", "profile"]):
                            
                            search_link.click()
                            time.sleep(5)
                            
                            # Extract results from related search
                            related_matches = self._extract_search_results(face_data)
                            matches.extend(related_matches)
                            
                            # Go back
                            self.driver.back()
                            time.sleep(3)
                    
                    except Exception as e:
                        self.logger.debug(f"Related search failed: {str(e)}")
                        continue
            
            except Exception:
                self.logger.debug("No related searches found")
        
        except Exception as e:
            self.logger.debug(f"Related searches failed: {str(e)}")
        
        return matches
    
    def _extract_search_results(self, face_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extracts and analyzes search results for facial matches and generates
        investigative leads (potential names and profile URLs).
        """
        matches = []
        leads = {
            "potential_names": set(),
            "profile_urls": set()
        }

        try:
            # Use a more stable selector if possible. 'div.g' is a common container for Google results.
            # You may need to inspect the current Google results page to find the best top-level container for each result.
            result_containers = self.driver.find_elements(By.CSS_SELECTOR, "div.g")
            if not result_containers:
                # Fallback to another potential selector if the first one fails
                result_containers = self.driver.find_elements(By.CSS_SELECTOR, "div.tF2Cxc")


            for container in result_containers:
                # --- Facial Match Logic ---
                try:
                    img_element = container.find_element(By.TAG_NAME, "img")
                    img_src = img_element.get_attribute("src")

                    if img_src and not img_src.startswith("data:"):
                        parent_link = container.find_element(By.TAG_NAME, "a")
                        result_url = parent_link.get_attribute("href") if parent_link else ""
                    
                        match_data = self._analyze_result_image(
                            img_src, result_url, face_data, "Google Result"
                    )
                    if match_data:
                        matches.append(match_data)
                except Exception:
                # It's normal for some containers not to have images, so we can ignore these errors.
                    pass

            # --- Lead Generation Logic ---
            try:
                # Extract text from the result for context
                # The h3 tag usually contains the main title of the result
                title_text = container.find_element(By.TAG_NAME, "h3").text
                
                # A simple regex to find things that look like names.
                # This can be tuned for better accuracy.
                found_names = re.findall(r'([A-Z][a-z]+(?: [A-Z][a-z]+)?)', title_text)
                for name in found_names:
                    # Filter out common non-name words if necessary
                    if len(name.split()) > 1: # Prioritize multi-word names
                        leads["potential_names"].add(name)

                # Extract the primary link from the result
                link_element = container.find_element(By.TAG_NAME, "a")
                href = link_element.get_attribute("href")
                
                # Check if the link is a potential social media profile
                if href:
                    if any(domain in href for domain in ["facebook.com/", "twitter.com/", "instagram.com/", "linkedin.com/in/"]):
                        leads["profile_urls"].add(href)
            except Exception:
                # Ignore errors if a container doesn't have the expected text or link structure.
                pass

        except Exception as e:
            self.logger.error(f"Could not extract search results: {str(e)}")

    # Convert sets to lists for JSON serialization
        leads["potential_names"] = list(leads["potential_names"])
        leads["profile_urls"] = list(leads["profile_urls"])

    # Return a dictionary containing both direct image matches and the new leads
        return {"matches": matches, "leads": leads}
    
    def _extract_similar_images(self, face_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract similar images from Google's visually similar section"""
        matches = []
        
        try:
            # Similar images have different structure
            similar_images = self.driver.find_elements(By.CSS_SELECTOR, ".rg_i")
            
            max_similar = 15 if self.aggressive_mode else 10
            
            for i, img_element in enumerate(similar_images[:max_similar]):
                try:
                    # Get image URL
                    img_src = img_element.get_attribute("src")
                    if not img_src:
                        # Try data-src
                        img_src = img_element.get_attribute("data-src")
                    
                    if not img_src or img_src.startswith("data:"):
                        continue
                    
                    # Get source page URL
                    parent_link = img_element.find_element(By.XPATH, "./ancestor::a")
                    result_url = parent_link.get_attribute("href") if parent_link else ""
                    
                    # Analyze for matches
                    match_data = self._analyze_result_image(
                        img_src, result_url, face_data, f"Similar image #{i+1}"
                    )
                    
                    if match_data:
                        matches.append(match_data)
                
                except Exception as e:
                    self.logger.debug(f"Error processing similar image: {str(e)}")
                    continue
        
        except Exception as e:
            self.logger.debug(f"Error extracting similar images: {str(e)}")
        
        return matches
    
    def _analyze_result_image(self, image_url: str, result_url: str, 
                            face_data: Dict[str, Any], context: str) -> Optional[Dict[str, Any]]:
        """
        Analyze a single result image for face matches
        
        Args:
            image_url: URL of the image to analyze
            result_url: URL of the page containing the image
            face_data: Target face data
            context: Context description
            
        Returns:
            Match data if similarity above threshold, None otherwise
        """
        try:
            # Download and analyze image
            image_data = self._download_image(image_url)
            if not image_data:
                return None
            
            # Extract faces from the image
            found_encodings = self.face_detector.extract_face_from_url_image(
                image_url, image_data
            )
            
            if not found_encodings:
                return None
            
            # Compare faces
            target_encoding = face_data["encoding"]
            comparisons = self.face_detector.compare_faces(target_encoding, found_encodings)
            
            # Return best match if above threshold
            for comparison in comparisons:
                if comparison["is_match"]:
                    return self._create_match_result(
                        similarity_score=comparison["similarity_score"],
                        url=result_url,
                        image_url=image_url,
                        context=f"Google Images - {context}",
                        additional_info={
                            "search_method": "reverse_image_search",
                            "discovery_source": "google_images",
                            "timestamp": time.time()
                        }
                    )
        
        except Exception as e:
            self.logger.debug(f"Error analyzing Google Images result: {str(e)}")
        
        return None
    
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
