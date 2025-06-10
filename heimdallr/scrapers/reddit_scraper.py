"""
Reddit scraper for facial recognition search (Law Enforcement Use)
"""

import time
import re
from typing import Dict, List, Any, Optional
import praw

from .base_scraper import BaseScraper
from ..core.face_detector import FaceDetector

class RedditScraper(BaseScraper):
    """Reddit platform scraper for law enforcement investigations"""
    
    def __init__(self, config, aggressive_mode: bool = False):
        super().__init__(config, aggressive_mode)
        self.face_detector = FaceDetector()
        self.reddit = None
        self._setup_reddit_api()
    
    def _setup_reddit_api(self):
        """Setup Reddit API (PRAW) authentication"""
        try:
            # Get Reddit API credentials
            client_id = self.config.get_api_key("reddit_client_id")
            client_secret = self.config.get_api_key("reddit_client_secret")
            user_agent = self.config.get("scraping.user_agents", ["heimdallr/1.0"])[0]
            
            if not all([client_id, client_secret]):
                self.logger.warning("⚠️  Reddit API credentials not configured")
                return
            
            # Initialize PRAW
            self.reddit = praw.Reddit(
                client_id=client_id,
                client_secret=client_secret,
                user_agent=user_agent
            )
            
            self.logger.info("✅ Reddit API configured")
            
        except Exception as e:
            self.logger.error(f"Failed to setup Reddit API: {str(e)}")
    
    def search_face(self, face_data: Dict[str, Any], leads: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Search for face matches on Reddit.
        If leads are provided, it will perform a targeted search.
        """
        try:
            self._log_search_attempt("Face Search", "Reddit image posts")
            
            matches = []

            # --- Targeted Search Logic ---
            if self.reddit and leads:
                self.logger.info("Conducting targeted search on Reddit using leads.")
                if leads.get("potential_names"):
                    for name in leads["potential_names"]:
                        self.logger.info(f"Targeted search for Reddit user: {name}")
                        try:
                            # Search for users (redditors) by name
                            user = self.reddit.redditor(name)
                            # Analyze recent submissions from this user
                            for submission in user.submissions.new(limit=10):
                                if self._has_image_content(submission):
                                    matches.extend(self._analyze_submission(submission, face_data))
                        except Exception as e:
                            self.logger.warning(f"Could not find or search Reddit user '{name}': {e}")
            
            # --- Broad Search Logic ---
            if self.reddit:
                search_methods = [
                    self._search_image_subreddits,
                    self._search_missing_persons,
                    self._search_help_subreddits,
                    self._search_local_subreddits
                ]
            else:
                search_methods = [self._search_web_fallback]
            
            for search_method in search_methods:
                try:
                    method_matches = search_method(face_data)
                    matches.extend(method_matches)
                    
                    if not self.aggressive_mode:
                        time.sleep(3)  # Reddit rate limiting
                        
                except Exception as e:
                    self.logger.warning(f"Reddit search method failed: {str(e)}")
                    continue
            
            # Process results
            unique_matches = self._deduplicate_matches(matches)
            unique_matches.sort(key=lambda x: x["similarity_score"], reverse=True)
            
            return {
                "platform": "reddit",
                "status": "success",
                "matches": unique_matches,
                "total_found": len(unique_matches),
                "search_time": time.time()
            }
            
        except Exception as e:
            return self._handle_search_error(e, "Reddit face search")
    
    def _search_image_subreddits(self, face_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Search popular image subreddits for matching faces"""
        matches = []
        
        if not self.reddit:
            return matches
        
        try:
            self.logger.info("🖼️  Searching Reddit image subreddits")
            
            image_subreddits = [
                "pics", "oldschoolcool", "mildlyinteresting", "interestingasfuck",
                "photoshopbattles", "portraits", "HumanPorn", "peopleporn"
            ]
            
            for subreddit_name in image_subreddits[:4]:
                try:
                    subreddit = self.reddit.subreddit(subreddit_name)
                    max_posts = 15 if self.aggressive_mode else 10
                    
                    for submission in subreddit.hot(limit=max_posts):
                        if self._has_image_content(submission):
                            matches.extend(self._analyze_submission(submission, face_data))
                except Exception as e:
                    self.logger.debug(f"Subreddit search failed for r/{subreddit_name}: {str(e)}")
        
        except Exception as e:
            self.logger.error(f"Reddit image subreddits search error: {str(e)}")
        
        return matches
    
    def _search_missing_persons(self, face_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Search missing persons and help subreddits"""
        matches = []
        
        if not self.reddit: return matches
        
        try:
            self.logger.info("🔍 Searching Reddit missing persons subreddits")
            
            help_subreddits = [
                "MissingPersons", "WithoutATrace", "UnresolvedMysteries",
                "RBI", "tipofmytongue", "HelpMeFind"
            ]
            
            for subreddit_name in help_subreddits:
                try:
                    subreddit = self.reddit.subreddit(subreddit_name)
                    for submission in subreddit.new(limit=20):
                        if self._has_image_content(submission):
                           matches.extend(self._analyze_submission(submission, face_data))
                except Exception as e:
                    self.logger.debug(f"Help subreddit search failed for r/{subreddit_name}: {str(e)}")
        
        except Exception as e:
            self.logger.error(f"Reddit missing persons search error: {str(e)}")
        
        return matches
    
    def _search_help_subreddits(self, face_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Search help and identification subreddits"""
        matches = []
        
        if not self.reddit: return matches
        
        try:
            self.logger.info("❓ Searching Reddit help subreddits")
            
            search_terms = ["person", "face", "identify", "who is", "help find"]
            
            for term in search_terms[:3]:
                try:
                    for submission in self.reddit.subreddit("all").search(
                        term, sort="new", time_filter="month", limit=10):
                        if self._has_image_content(submission):
                            matches.extend(self._analyze_submission(submission, face_data))
                except Exception as e:
                    self.logger.debug(f"Reddit search failed for term '{term}': {str(e)}")
        
        except Exception as e:
            self.logger.error(f"Reddit help search error: {str(e)}")
        
        return matches
    
    def _search_local_subreddits(self, face_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Search local/city subreddits for relevant posts"""
        matches = []
        if not self.reddit: return matches
        
        try:
            self.logger.info("🌍 Searching Reddit local subreddits")
            
            city_subreddits = ["nyc", "LosAngeles", "chicago", "houston", "phoenix"]
            
            for city in city_subreddits[:3]:
                try:
                    subreddit = self.reddit.subreddit(city)
                    for submission in subreddit.search("missing OR found OR help OR person", 
                                                       sort="new", time_filter="month", limit=5):
                        if self._has_image_content(submission):
                           matches.extend(self._analyze_submission(submission, face_data))
                except Exception as e:
                    self.logger.debug(f"Local subreddit search failed for r/{city}: {str(e)}")
        
        except Exception as e:
            self.logger.error(f"Reddit local search error: {str(e)}")
        
        return matches

    def _search_web_fallback(self, face_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Fallback web scraping method when API is not available"""
        self.logger.warning("⚠️ Reddit API not available. Web scraping requires advanced implementation.")
        return []

    def _has_image_content(self, submission) -> bool:
        """Check if a Reddit submission contains image content"""
        url = submission.url.lower()
        return any(ext in url for ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp']) or \
               any(domain in url for domain in ['imgur.com', 'i.redd.it', 'reddit.com/gallery']) or \
               (hasattr(submission, 'is_gallery') and submission.is_gallery)
    
    def _analyze_submission(self, submission, face_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Analyze a Reddit submission for face matches"""
        matches = []
        image_urls = self._extract_image_urls(submission)
        
        for image_url in image_urls:
            try:
                image_data = self._download_image(image_url)
                if not image_data: continue
                
                found_encodings = self.face_detector.extract_face_from_url_image(image_url, image_data)
                if not found_encodings: continue
                
                target_encoding = face_data["encoding"]
                comparisons = self.face_detector.compare_faces(target_encoding, found_encodings)
                
                for comparison in comparisons:
                    if comparison["is_match"]:
                        matches.append(self._create_match_result(
                            similarity_score=comparison["similarity_score"],
                            url=f"https://reddit.com{submission.permalink}",
                            image_url=image_url,
                            context="Reddit post",
                            additional_info={
                                "post_id": submission.id, "subreddit": str(submission.subreddit),
                                "title": submission.title[:200], "author": str(submission.author) if submission.author else "[deleted]",
                                "score": submission.score, "comments": submission.num_comments,
                                "created": submission.created_utc, "nsfw": submission.over_18
                            }
                        ))
            except Exception as e:
                self.logger.debug(f"Error analyzing Reddit image {image_url}: {str(e)}")
        
        return matches
    
    def _extract_image_urls(self, submission) -> List[str]:
        """Extract image URLs from a Reddit submission"""
        urls = []
        url = submission.url
        if any(ext in url.lower() for ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp']):
            urls.append(url)
        elif 'i.redd.it' in url:
            urls.append(url)
        elif 'imgur.com' in url and '/a/' not in url and '/gallery/' not in url:
            urls.append(url)
        elif hasattr(submission, 'is_gallery') and submission.is_gallery and hasattr(submission, 'media_metadata'):
            for item in submission.media_metadata.values():
                if 's' in item and 'u' in item['s']:
                    urls.append(item['s']['u'].replace('&amp;', '&'))
        return urls
    
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