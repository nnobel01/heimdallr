"""
Twitter/X scraper for facial recognition search (Law Enforcement Use)
"""

import re
import json
import time
from typing import Dict, List, Any, Optional
from urllib.parse import quote_plus
import tweepy

from .base_scraper import BaseScraper
from ..core.face_detector import FaceDetector

class TwitterScraper(BaseScraper):
    """Twitter/X platform scraper for law enforcement investigations"""
    
    def __init__(self, config, aggressive_mode: bool = False):
        super().__init__(config, aggressive_mode)
        self.face_detector = FaceDetector()
        self.api = None
        self.client = None
        self._setup_twitter_api()
    
    def _setup_twitter_api(self):
        """Setup Twitter API authentication"""
        try:
            # Get API credentials from config
            api_key = self.config.get_api_key("twitter")
            api_secret = self.config.get_api_key("twitter_secret")
            access_token = self.config.get_api_key("twitter_access_token")
            access_token_secret = self.config.get_api_key("twitter_access_token_secret")
            bearer_token = self.config.get_api_key("twitter_bearer_token")
            
            if not all([api_key, api_secret, access_token, access_token_secret]):
                self.logger.warning("⚠️  Twitter API credentials not configured")
                return
            
            # Setup API v1.1 (for media search)
            auth = tweepy.OAuthHandler(api_key, api_secret)
            auth.set_access_token(access_token, access_token_secret)
            self.api = tweepy.API(auth, wait_on_rate_limit=True)
            
            # Setup API v2 (for advanced search)
            if bearer_token:
                self.client = tweepy.Client(bearer_token=bearer_token)
            
            self.logger.info("✅ Twitter API configured")
            
        except Exception as e:
            self.logger.error(f"Failed to setup Twitter API: {str(e)}")
    
    def search_face(self, face_data: Dict[str, Any], leads: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Search for face matches on Twitter/X.
        If leads (names, URLs) are provided, it will perform a targeted search.
        """
        try:
            self._log_search_attempt("Face Search", "Twitter image posts")
            
            matches = []

            # --- Targeted Search Logic ---
            # If leads are provided, use them to perform targeted searches.
            if leads:
                self.logger.info("Conducting targeted search on Twitter using leads.")
                if leads.get("potential_names"):
                    for name in leads["potential_names"]:
                        # This is a placeholder for searching for users by name.
                        # The actual implementation would call a method like self._search_user_by_name_api(name, face_data)
                        self.logger.info(f"Targeted search for name: {name}")

                if leads.get("profile_urls"):
                    for url in leads["profile_urls"]:
                        if "twitter.com" in url:
                            # This is a placeholder for scraping a specific profile URL.
                            # The actual implementation would call a method like self._scrape_profile_url(url, face_data)
                            self.logger.info(f"Targeted search for URL: {url}")
            
            # --- Broad Search Logic ---
            # The original broad search methods will run if no leads are found,
            # or can be modified to supplement the targeted search.
            if self.api or self.client:
                # API-based search methods
                search_methods = [
                    self._search_images_api,
                    self._search_user_profiles_api,
                    self._search_hashtags_api
                ]
            else:
                # Fallback to web scraping
                search_methods = [
                    self._search_images_web,
                    self._search_trending_web
                ]
            
            # Execute search methods
            for search_method in search_methods:
                try:
                    method_matches = search_method(face_data)
                    matches.extend(method_matches)
                    
                    if not self.aggressive_mode:
                        time.sleep(5)  # Rate limiting pause
                        
                except Exception as e:
                    self.logger.warning(f"Twitter search method failed: {str(e)}")
                    continue
            
            # Process results
            unique_matches = self._deduplicate_matches(matches)
            unique_matches.sort(key=lambda x: x["similarity_score"], reverse=True)
            
            return {
                "platform": "twitter",
                "status": "success",
                "matches": unique_matches,
                "total_found": len(unique_matches),
                "search_time": time.time()
            }
            
        except Exception as e:
            return self._handle_search_error(e, "Twitter face search")
    
    def _search_images_api(self, face_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Search Twitter for image tweets using API"""
        matches = []
        
        if not self.client:
            return matches
        
        try:
            self.logger.info("🔍 Searching Twitter image posts via API")
            
            # Search for tweets with images using various queries
            search_queries = [
                "has:images",
                "filter:images person",
                "filter:images face",
                "has:media profile"
            ]
            
            for query in search_queries:
                try:
                    # Search recent tweets with images
                    tweets = tweepy.Paginator(
                        self.client.search_recent_tweets,
                        query=query,
                        max_results=20 if self.aggressive_mode else 10,
                        expansions=['attachments.media_keys', 'author_id'],
                        media_fields=['url', 'preview_image_url', 'type'],
                        user_fields=['profile_image_url']
                    ).flatten(limit=50 if self.aggressive_mode else 20)
                    
                    for tweet in tweets:
                        tweet_matches = self._analyze_tweet_api(tweet, face_data)
                        matches.extend(tweet_matches)
                        
                        if not self.aggressive_mode:
                            time.sleep(1)
                
                except Exception as e:
                    self.logger.debug(f"API search failed for query '{query}': {str(e)}")
                    continue
        
        except Exception as e:
            self.logger.error(f"Twitter API image search error: {str(e)}")
        
        return matches
    
    def _search_user_profiles_api(self, face_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Search Twitter user profiles for matching profile images"""
        matches = []
        
        if not self.client:
            return matches
        
        try:
            self.logger.info("👤 Searching Twitter profile images")
            
            # Search for users with common names/terms
            search_terms = ["person", "profile", "user", "account"]
            
            for term in search_terms[:2]:  # Limit to avoid rate limits
                try:
                    # Search users
                    users = self.client.search_users(
                        query=term,
                        max_results=20 if self.aggressive_mode else 10,
                        user_fields=['profile_image_url', 'public_metrics']
                    )
                    
                    if users.data:
                        for user in users.data:
                            if hasattr(user, 'profile_image_url') and user.profile_image_url:
                                match_data = self._analyze_profile_image(
                                    user.profile_image_url, 
                                    face_data, 
                                    user
                                )
                                if match_data:
                                    matches.append(match_data)
                
                except Exception as e:
                    self.logger.debug(f"User search failed for term '{term}': {str(e)}")
                    continue
        
        except Exception as e:
            self.logger.error(f"Twitter profile search error: {str(e)}")
        
        return matches
    
    def _search_hashtags_api(self, face_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Search specific hashtags for image content"""
        matches = []
        
        if not self.client:
            return matches
        
        try:
            self.logger.info("🏷️  Searching Twitter hashtags")
            
            # Person-related hashtags
            hashtags = [
                "#missing", "#found", "#help", "#search", 
                "#person", "#face", "#profile", "#selfie"
            ]
            
            for hashtag in hashtags[:3]:  # Limit hashtags
                try:
                    query = f"{hashtag} has:images"
                    tweets = tweepy.Paginator(
                        self.client.search_recent_tweets,
                        query=query,
                        max_results=10,
                        expansions=['attachments.media_keys'],
                        media_fields=['url', 'preview_image_url']
                    ).flatten(limit=20)
                    
                    for tweet in tweets:
                        tweet_matches = self._analyze_tweet_api(tweet, face_data)
                        matches.extend(tweet_matches)
                
                except Exception as e:
                    self.logger.debug(f"Hashtag search failed for {hashtag}: {str(e)}")
                    continue
        
        except Exception as e:
            self.logger.error(f"Twitter hashtag search error: {str(e)}")
        
        return matches
    
    def _search_images_web(self, face_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Fallback web scraping for Twitter images"""
        matches = []
        
        try:
            self.logger.info("🌐 Searching Twitter via web scraping")
            
            # This would require sophisticated scraping due to Twitter's
            # dynamic loading and anti-scraping measures
            # For now, return empty list as it requires complex implementation
            
            self.logger.warning("⚠️  Web scraping Twitter requires advanced implementation")
            
        except Exception as e:
            self.logger.debug(f"Twitter web scraping failed: {str(e)}")
        
        return matches
    
    def _search_trending_web(self, face_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Search trending topics for relevant images"""
        matches = []
        
        # Placeholder for trending search
        # Would require real-time trending topics analysis
        
        return matches
    
    def _analyze_tweet_api(self, tweet, face_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Analyze a tweet for face matches using API data
        
        Args:
            tweet: Tweet object from API
            face_data: Target face data
            
        Returns:
            List of matches found in the tweet
        """
        matches = []
        
        try:
            # Check if tweet has media attachments
            if hasattr(tweet, 'attachments') and tweet.attachments:
                media_keys = tweet.attachments.get('media_keys', [])
                
                # This would require additional API calls to get media URLs
                # For now, this is a simplified implementation
                
                for media_key in media_keys:
                    # In real implementation, would fetch media details
                    # and analyze images for faces
                    pass
        
        except Exception as e:
            self.logger.debug(f"Error analyzing tweet: {str(e)}")
        
        return matches
    
    def _analyze_profile_image(self, profile_image_url: str, face_data: Dict[str, Any], 
                             user_data) -> Optional[Dict[str, Any]]:
        """
        Analyze a Twitter profile image for face matches
        
        Args:
            profile_image_url: URL of the profile image
            face_data: Target face data
            user_data: User information
            
        Returns:
            Match data if similarity above threshold, None otherwise
        """
        try:
            # Remove size modifier from Twitter image URL to get full size
            full_size_url = profile_image_url.replace('_normal', '')
            
            # Download and analyze image
            image_data = self._download_image(full_size_url)
            if not image_data:
                return None
            
            # Extract faces
            found_encodings = self.face_detector.extract_face_from_url_image(
                full_size_url, image_data
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
                        url=f"https://twitter.com/{user_data.username}" if hasattr(user_data, 'username') else "",
                        image_url=full_size_url,
                        context="Twitter profile image",
                        additional_info={
                            "user_id": user_data.id if hasattr(user_data, 'id') else "",
                            "username": user_data.username if hasattr(user_data, 'username') else "",
                            "followers": getattr(user_data, 'public_metrics', {}).get('followers_count', 0),
                            "verified": getattr(user_data, 'verified', False),
                            "timestamp": time.time()
                        }
                    )
        
        except Exception as e:
            self.logger.debug(f"Error analyzing Twitter profile image: {str(e)}")
        
        return None
    
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