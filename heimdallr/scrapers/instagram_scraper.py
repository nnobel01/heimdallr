"""
Instagram scraper for facial recognition search (Law Enforcement Use)
"""

import re
import json
import time
from typing import Dict, List, Any, Optional
from urllib.parse import quote_plus
import instaloader

from .base_scraper import BaseScraper
from ..core.face_detector import FaceDetector

class InstagramScraper(BaseScraper):
    """Instagram platform scraper for law enforcement investigations"""
    
    def __init__(self, config, aggressive_mode: bool = False):
        super().__init__(config, aggressive_mode)
        self.face_detector = FaceDetector()
        
        # Initialize Instaloader
        self.loader = instaloader.Instaloader(
            download_videos=False,
            download_video_thumbnails=False,
            download_geotags=False,
            download_comments=False,
            save_metadata=False,
            compress_json=False
        )
        
        # Set session to avoid being blocked
        if not aggressive_mode:
            self.loader.context.sleep = True
            self.loader.context.request_timeout = 300
    
    def search_face(self, face_data: Dict[str, Any], leads: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Search for face matches on Instagram.
        If leads are provided, it will perform a targeted search.
        """
        try:
            self._log_search_attempt("Face Search", "Instagram public posts")
            
            matches = []

            # --- Targeted Search Logic ---
            # If leads (names, URLs) are provided from Google search, use them first.
            if leads:
                self.logger.info("Conducting targeted search on Instagram using leads.")
                if leads.get("profile_urls"):
                    for url in leads["profile_urls"]:
                        if "instagram.com" in url:
                            try:
                                # Extract username from URL and fetch profile
                                username = url.split('/')[-2] if url.endswith('/') else url.split('/')[-1]
                                self.logger.info(f"Targeted search for profile: {username}")
                                profile = instaloader.Profile.from_username(self.loader.context, username)
                                # Analyze profile's posts
                                for post in profile.get_posts():
                                    matches.extend(self._analyze_post(post, face_data))
                                    if len(matches) > (20 if self.aggressive_mode else 10):
                                        break
                            except Exception as e:
                                self.logger.warning(f"Failed to scrape Instagram profile {url}: {e}")
            
            # --- Broad Search Logic ---
            # Original broad search methods to supplement targeted search or run if no leads.
            search_methods = [
                self._search_hashtags,
                self._search_locations,
                self._search_recent_posts
            ]
            
            # Execute multiple search strategies
            for search_method in search_methods:
                try:
                    method_matches = search_method(face_data)
                    matches.extend(method_matches)
                    
                    if not self.aggressive_mode:
                        time.sleep(5)  # Pause between search methods
                        
                except Exception as e:
                    self.logger.warning(f"Instagram search method failed: {str(e)}")
                    continue
            
            # Remove duplicates and sort by similarity
            unique_matches = self._deduplicate_matches(matches)
            unique_matches.sort(key=lambda x: x["similarity_score"], reverse=True)
            
            return {
                "platform": "instagram",
                "status": "success",
                "matches": unique_matches,
                "total_found": len(unique_matches),
                "search_time": time.time()
            }
            
        except Exception as e:
            return self._handle_search_error(e, "Instagram face search")
    
    def _search_hashtags(self, face_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Search Instagram hashtags for matching faces"""
        matches = []
        
        # Common hashtags for person searches
        hashtags = [
            "people", "portraits", "selfie", "person", "human", "face",
            "missing", "found", "help", "search", "looking"
        ]
        
        try:
            for hashtag in hashtags[:3]:  # Limit to avoid rate limiting
                self.logger.info(f"🔍 Searching hashtag: #{hashtag}")
                
                try:
                    hashtag_obj = instaloader.Hashtag.from_name(self.loader.context, hashtag)
                    
                    # Get recent posts (limited number to avoid blocking)
                    post_count = 0
                    max_posts = 20 if self.aggressive_mode else 10
                    
                    for post in hashtag_obj.get_posts():
                        if post_count >= max_posts:
                            break
                        
                        post_matches = self._analyze_post(post, face_data)
                        matches.extend(post_matches)
                        post_count += 1
                        
                        # Rate limiting
                        if not self.aggressive_mode:
                            time.sleep(2)
                
                except Exception as e:
                    self.logger.debug(f"Hashtag search failed for #{hashtag}: {str(e)}")
                    continue
                
                # Pause between hashtags
                if not self.aggressive_mode:
                    time.sleep(5)
        
        except Exception as e:
            self.logger.error(f"Instagram hashtag search error: {str(e)}")
        
        return matches
    
    def _search_locations(self, face_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Search Instagram location tags for matching faces"""
        matches = []
        
        # This would require specific location data
        # For now, return empty list as location search needs coordinates
        self.logger.info("📍 Location search requires specific coordinates")
        return matches
    
    def _search_recent_posts(self, face_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Search recent public posts for matching faces"""
        matches = []
        
        try:
            # This is a simplified approach - in practice would use Instagram's API
            # or more sophisticated scraping methods
            self.logger.info("🕐 Searching recent public posts")
            
            # Placeholder for recent posts search
            # Real implementation would require Instagram Graph API or
            # sophisticated scraping techniques
            
        except Exception as e:
            self.logger.debug(f"Recent posts search failed: {str(e)}")
        
        return matches
    
    def _analyze_post(self, post, face_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Analyze a single Instagram post for face matches
        
        Args:
            post: Instagram post object
            face_data: Target face data
            
        Returns:
            List of matches found in this post
        """
        matches = []
        
        try:
            # Get post image URL
            image_url = post.url
            
            # Download and analyze image
            image_data = self._download_image(image_url)
            if not image_data:
                return matches
            
            # Extract faces from the image
            found_encodings = self.face_detector.extract_face_from_url_image(
                image_url, image_data
            )
            
            if not found_encodings:
                return matches
            
            # Compare faces
            target_encoding = face_data["encoding"]
            comparisons = self.face_detector.compare_faces(target_encoding, found_encodings)
            
            # Process matches above threshold
            for comparison in comparisons:
                if comparison["is_match"]:
                    match = self._create_match_result(
                        similarity_score=comparison["similarity_score"],
                        url=f"https://instagram.com/p/{post.shortcode}",
                        image_url=image_url,
                        context="Instagram post",
                        additional_info={
                            "post_id": post.shortcode,
                            "caption": post.caption[:200] if post.caption else "",
                            "likes": post.likes,
                            "timestamp": post.date.isoformat() if post.date else "",
                            "owner": post.owner_username if hasattr(post, 'owner_username') else ""
                        }
                    )
                    matches.append(match)
        
        except Exception as e:
            self.logger.debug(f"Error analyzing Instagram post: {str(e)}")
        
        return matches
    
    def _deduplicate_matches(self, matches: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate matches based on URL"""
        seen_urls = set()
        unique_matches = []
        
        for match in matches:
            url = match.get("url", "")
            if url not in seen_urls:
                seen_urls.add(url)
                unique_matches.append(match)
        
        return unique_matches