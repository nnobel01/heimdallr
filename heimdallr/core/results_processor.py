"""
Results processing and ranking for law enforcement use
"""

import json
import csv
import pandas as pd
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path
import hashlib
import uuid

from ..utils.logger import get_logger

logger = get_logger()

class ResultsProcessor:
    """Process and format search results for law enforcement analysis"""
    
    def __init__(self, threshold: float = 80.0):
        """
        Initialize results processor
        
        Args:
            threshold: Minimum similarity threshold for matches
        """
        self.threshold = threshold
        self.logger = logger
        
        # Create results directory
        self.results_dir = Path("results")
        self.results_dir.mkdir(exist_ok=True)
    
    def process_results(self, search_results: Dict[str, Any], 
                       faces_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process and rank all search results
        
        Args:
            search_results: Raw search results from all platforms
            faces_data: Original face detection data
            
        Returns:
            Processed and ranked results with metadata
        """
        processed_results = {
            "case_metadata": self._generate_case_metadata(faces_data),
            "search_summary": self._generate_search_summary(search_results),
            "high_confidence_matches": [],
            "medium_confidence_matches": [],
            "low_confidence_matches": [],
            "platform_results": {},
            "evidence_chain": self._generate_evidence_chain(search_results, faces_data),
            "legal_disclaimer": self._get_legal_disclaimer()
        }
        
        all_matches = []
        
        # Process each platform's results
        for platform, platform_data in search_results.get("platform_results", {}).items():
            if platform_data.get("status") == "success":
                processed_platform = self._process_platform_results(platform, platform_data)
                processed_results["platform_results"][platform] = processed_platform
                
                # Collect all matches for ranking
                all_matches.extend(processed_platform.get("matches", []))
        
        # Rank and categorize all matches
        self._categorize_matches(all_matches, processed_results)
        
        # Generate investigation recommendations
        processed_results["investigation_recommendations"] = self._generate_recommendations(
            processed_results
        )
        
        return processed_results
    
    def _generate_case_metadata(self, faces_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate case metadata for law enforcement documentation"""
        case_id = str(uuid.uuid4())[:8].upper()
        
        return {
            "case_id": f"HEIMDALLR-{case_id}",
            "timestamp": datetime.now().isoformat(),
            "operator": "REDACTED",  # Would be filled by actual operator
            "jurisdiction": "TBD",   # Would be specified by agency
            "original_image": faces_data.get("original_image"),
            "faces_detected": faces_data.get("face_count", 0),
            "image_hash": self._generate_image_hash(faces_data.get("original_image", "")),
            "processing_version": "1.0.0",
            "legal_authority": "TBD"  # Must be specified by operator
        }
    
    def _generate_search_summary(self, search_results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate summary of search operations"""
        platform_results = search_results.get("platform_results", {})
        metadata = search_results.get("search_metadata", {})
        
        total_matches = 0
        successful_platforms = 0
        failed_platforms = 0
        
        for platform, data in platform_results.items():
            if data.get("status") == "success":
                successful_platforms += 1
                total_matches += len(data.get("matches", []))
            else:
                failed_platforms += 1
        
        return {
            "total_platforms_searched": len(platform_results),
            "successful_platforms": successful_platforms,
            "failed_platforms": failed_platforms,
            "total_matches_found": total_matches,
            "search_duration": metadata.get("duration_seconds", 0),
            "aggressive_mode_used": metadata.get("aggressive_mode", False),
            "platforms_searched": metadata.get("platforms_searched", [])
        }
    
    def _process_platform_results(self, platform: str, 
                                 platform_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process results from a single platform"""
        matches = platform_data.get("matches", [])
        
        # Filter matches above threshold
        valid_matches = [
            match for match in matches 
            if match.get("similarity_score", 0) >= self.threshold
        ]
        
        # Sort by similarity score
        valid_matches.sort(key=lambda x: x.get("similarity_score", 0), reverse=True)
        
        # Add evidence metadata to each match
        for i, match in enumerate(valid_matches):
            match["evidence_id"] = f"{platform.upper()}-{i+1:03d}"
            match["discovery_timestamp"] = datetime.now().isoformat()
            match["chain_of_custody"] = {
                "discovered_by": "HEIMDALLR",
                "platform": platform,
                "collection_method": "automated_search",
                "verification_needed": True
            }
        
        return {
            "platform": platform,
            "status": platform_data.get("status", "unknown"),
            "total_matches": len(matches),
            "valid_matches": len(valid_matches),
            "matches": valid_matches,
            "search_time": platform_data.get("search_time"),
            "error": platform_data.get("error")
        }
    
    def _categorize_matches(self, all_matches: List[Dict[str, Any]], 
                          results: Dict[str, Any]):
        """Categorize matches by confidence level"""
        
        for match in all_matches:
            similarity = match.get("similarity_score", 0)
            
            if similarity >= 95:
                results["high_confidence_matches"].append(match)
            elif similarity >= 85:
                results["medium_confidence_matches"].append(match)
            elif similarity >= self.threshold:
                results["low_confidence_matches"].append(match)
        
        # Sort each category by similarity
        for category in ["high_confidence_matches", "medium_confidence_matches", "low_confidence_matches"]:
            results[category].sort(key=lambda x: x.get("similarity_score", 0), reverse=True)
    
    def _generate_evidence_chain(self, search_results: Dict[str, Any], 
                               faces_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate evidence chain documentation"""
        chain = []
        
        # Original image processing
        chain.append({
            "step": 1,
            "action": "Original Image Processing",
            "timestamp": datetime.now().isoformat(),
            "details": {
                "image_path": faces_data.get("original_image"),
                "faces_detected": faces_data.get("face_count", 0),
                "processing_method": "face_recognition library",
                "image_dimensions": faces_data.get("image_dimensions")
            },
            "integrity_hash": self._generate_image_hash(faces_data.get("original_image", ""))
        })
        
        # Search operations
        step = 2
        for platform, data in search_results.get("platform_results", {}).items():
            chain.append({
                "step": step,
                "action": f"Platform Search - {platform.title()}",
                "timestamp": data.get("search_time"),
                "details": {
                    "platform": platform,
                    "status": data.get("status"),
                    "matches_found": len(data.get("matches", [])),
                    "search_method": "automated_scraping"
                }
            })
            step += 1
        
        return chain
    
    def _generate_recommendations(self, results: Dict[str, Any]) -> List[str]:
        """Generate investigation recommendations based on results"""
        recommendations = []
        
        high_confidence = len(results["high_confidence_matches"])
        medium_confidence = len(results["medium_confidence_matches"])
        total_matches = high_confidence + medium_confidence + len(results["low_confidence_matches"])
        
        if high_confidence > 0:
            recommendations.append(
                f"PRIORITY: {high_confidence} high-confidence matches (95%+) require immediate manual verification"
            )
        
        if medium_confidence > 5:
            recommendations.append(
                f"INVESTIGATE: {medium_confidence} medium-confidence matches (85-94%) should be manually reviewed"
            )
        
        if total_matches == 0:
            recommendations.append(
                "NO MATCHES: Consider expanding search parameters or using different source images"
            )
        elif total_matches > 50:
            recommendations.append(
                "HIGH VOLUME: Large number of matches detected - prioritize highest confidence results"
            )
        
        # Platform-specific recommendations
        successful_platforms = results["search_summary"]["successful_platforms"]
        failed_platforms = results["search_summary"]["failed_platforms"]
        
        if failed_platforms > 0:
            recommendations.append(
                f"TECHNICAL: {failed_platforms} platforms failed - retry with different parameters if needed"
            )
        
        recommendations.append(
            "LEGAL: Ensure proper legal authority before acting on any matches"
        )
        recommendations.append(
            "VERIFICATION: All matches require manual verification before use as evidence"
        )
        
        return recommendations
    
    def _get_legal_disclaimer(self) -> str:
        """Get legal disclaimer for law enforcement use"""
        return """
        LEGAL DISCLAIMER FOR LAW ENFORCEMENT USE:
        
        1. This tool is intended for use by authorized law enforcement personnel only
        2. All searches must be conducted under proper legal authority
        3. Results are investigative leads only and require manual verification
        4. Respect applicable privacy laws and constitutional protections
        5. Maintain proper chain of custody for any evidence derived from this tool
        6. Document all uses in accordance with agency policies
        7. Results may include false positives - verify before acting
        
        By using this tool, operator confirms proper legal authority and training.
        """
    
    def save_csv(self, results: Dict[str, Any], output_file: Path):
        """Save results in CSV format for analysis"""
        rows = []
        
        # Combine all matches
        all_matches = (
            results.get("high_confidence_matches", []) +
            results.get("medium_confidence_matches", []) +
            results.get("low_confidence_matches", [])
        )
        
        for match in all_matches:
            rows.append({
                "Evidence_ID": match.get("evidence_id", ""),
                "Platform": match.get("platform", ""),
                "Similarity_Score": match.get("similarity_score", 0),
                "Confidence_Category": self._get_confidence_category(match.get("similarity_score", 0)),
                "URL": match.get("url", ""),
                "Image_URL": match.get("image_url", ""),
                "Context": match.get("context", ""),
                "Discovery_Time": match.get("discovery_timestamp", ""),
                "Verification_Status": "PENDING",
                "Notes": ""
            })
        
        df = pd.DataFrame(rows)
        df.to_csv(output_file, index=False)
    
    def _get_confidence_category(self, similarity_score: float) -> str:
        """Get confidence category for a similarity score"""
        if similarity_score >= 95:
            return "HIGH"
        elif similarity_score >= 85:
            return "MEDIUM"
        else:
            return "LOW"
    
    def _generate_image_hash(self, image_path: str) -> str:
        """Generate hash for image integrity verification"""
        if not image_path:
            return ""
        
        try:
            with open(image_path, 'rb') as f:
                content = f.read()
            return hashlib.sha256(content).hexdigest()
        except:
            return ""
