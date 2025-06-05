# Heimdallr - Advanced Facial Recognition Search Tool

🚔 **LAW ENFORCEMENT USE ONLY** 🚔

## Overview

Heimdallr is an advanced facial recognition search tool designed specifically for law enforcement investigations. It searches across multiple platforms including social media sites and web search engines to locate instances of faces and similar individuals.

## ⚠️ LEGAL DISCLAIMER

**THIS TOOL IS INTENDED FOR USE BY AUTHORIZED LAW ENFORCEMENT PERSONNEL ONLY**

- All searches must be conducted under proper legal authority
- Results are investigative leads only and require manual verification
- Respect applicable privacy laws and constitutional protections
- Maintain proper chain of custody for any evidence derived from this tool
- Document all uses in accordance with agency policies
- Results may include false positives - verify before acting

By using this tool, operator confirms proper legal authority and training.

## Features

### 🔍 Multi-Platform Search
- **Instagram**: Public posts, hashtags, profile images
- **Facebook**: Public pages, marketplace listings, accessible content
- **Twitter/X**: Image tweets, profile photos, hashtag searches
- **Reddit**: Image subreddits, missing persons posts, help communities
- **Google Images**: Reverse image search, similar images, related results

### 🎯 Advanced Face Recognition
- 80%+ similarity threshold for high accuracy
- Multiple face detection models (HOG/CNN)
- Batch processing capabilities
- Face encoding caching for performance

### 📊 Professional Results
- **JSON/CSV Export**: Structured data for analysis
- **Evidence Chain**: Complete audit trail
- **Confidence Scoring**: High/Medium/Low match categories
- **Case Management**: Unique case IDs and metadata

### 🛡️ Anti-Detection Features
- User agent rotation
- Rate limiting compliance
- Proxy support ready
- Headless browser operations

## Installation

### Prerequisites
- Python 3.8+
- Chrome/Chromium browser
- CMake (for dlib compilation)

### Install Dependencies
```bash
# Install system dependencies
sudo apt-get update
sudo apt-get install cmake build-essential

# Install Python packages
pip install -r requirements.txt

# Install Heimdallr
pip install -e .
```

## Configuration

### 1. Create Configuration File
```bash
# Will be created automatically on first run
.heimdallr_config.json
```

### 2. API Keys Setup
Create a `.env` file in the project root:

```bash
# Twitter API
TWITTER_API_KEY=your_api_key
TWITTER_API_SECRET=your_api_secret
TWITTER_ACCESS_TOKEN=your_access_token
TWITTER_ACCESS_TOKEN_SECRET=your_access_token_secret
TWITTER_BEARER_TOKEN=your_bearer_token

# Reddit API
REDDIT_CLIENT_ID=your_client_id
REDDIT_CLIENT_SECRET=your_client_secret

# Instagram (Optional - uses web scraping by default)
INSTAGRAM_USERNAME=your_username
INSTAGRAM_PASSWORD=your_password
```

### 3. Platform Configuration
The tool automatically creates a configuration file with:
- Rate limiting settings
- Search parameters
- Output preferences
- Platform toggles

## Usage

### Basic Search
```bash
# Simple face search
heimdallr photo.jpg

# Specify output directory
heimdallr photo.jpg --output investigation_001

# JSON output only
heimdallr photo.jpg --format json
```

### Advanced Options
```bash
# Aggressive search mode (higher speed, higher detection risk)
heimdallr photo.jpg --aggressive

# Custom similarity threshold
heimdallr photo.jpg --threshold 85

# Specific platforms only
heimdallr photo.jpg --platforms instagram,facebook,reddit

# Verbose logging
heimdallr photo.jpg --verbose
```

### Platform-Specific Searches
```bash
# Social media only
heimdallr photo.jpg --platforms social

# Web search only
heimdallr photo.jpg --platforms web

# Specific combination
heimdallr photo.jpg --platforms instagram,google_images
```

## Output Format

### JSON Structure
```json
{
  "case_metadata": {
    "case_id": "HEIMDALLR-A1B2C3D4",
    "timestamp": "2024-01-15T10:30:00Z",
    "operator": "REDACTED",
    "legal_authority": "TBD"
  },
  "search_summary": {
    "total_platforms_searched": 5,
    "total_matches_found": 12,
    "search_duration": 127.3
  },
  "high_confidence_matches": [
    {
      "evidence_id": "INSTAGRAM-001",
      "platform": "instagram",
      "similarity_score": 96.8,
      "url": "https://instagram.com/p/xyz",
      "image_url": "https://...",
      "context": "Instagram post",
      "chain_of_custody": {...}
    }
  ],
  "investigation_recommendations": [...]
}
```

### CSV Output
Spreadsheet-friendly format with columns:
- Evidence_ID
- Platform
- Similarity_Score
- Confidence_Category
- URL
- Discovery_Time
- Verification_Status

## Law Enforcement Features

### Case Management
- Unique case IDs for tracking
- Complete audit trail
- Evidence chain documentation
- Operator identification fields

### Investigation Workflow
1. **Initial Search**: Run comprehensive search across all platforms
2. **Results Review**: Examine high-confidence matches first
3. **Manual Verification**: Verify all matches before acting
4. **Documentation**: Export results for case files
5. **Follow-up**: Use leads for further investigation

### Best Practices
- Always obtain proper legal authority before searching
- Document the investigative need and legal basis
- Verify all matches through independent means
- Maintain chain of custody for digital evidence
- Follow agency policies for digital investigations

## Rate Limiting & Ethics

### Respectful Scraping
- Built-in rate limiting for all platforms
- Respects robots.txt files
- Randomized delays between requests
- User agent rotation

### Privacy Considerations
- Only searches publicly available content
- Does not attempt to bypass privacy settings
- Includes warnings about verification needs
- Maintains audit logs for accountability

## Troubleshooting

### Common Issues
1. **No faces detected**: Ensure clear, frontal face images
2. **API rate limits**: Wait and retry, or use less aggressive settings
3. **Driver errors**: Update Chrome and chromedriver
4. **Network issues**: Check proxy settings and connectivity

### Platform-Specific Notes
- **Facebook**: Very limited due to privacy restrictions
- **Instagram**: Best results with hashtag searches
- **Twitter**: Requires API keys for full functionality
- **Reddit**: Most accessible, good for missing persons
- **Google Images**: Most comprehensive reverse search

## Security Notes

### Data Handling
- Face encodings are cached locally only
- No data transmitted to third parties
- Results stored locally by default
- Secure deletion of temporary files

### Operational Security
- Use VPN for sensitive investigations
- Rotate user agents and IP addresses
- Monitor for detection/blocking
- Follow agency cybersecurity policies

## Legal Compliance

### Required Documentation
- Legal authority for the search
- Investigative necessity
- Platforms searched and methods used
- Results obtained and verification status
- Chain of custody for evidence

### Limitations
- Tool provides investigative leads only
- All results require manual verification
- No guarantee of accuracy or completeness
- Subject to platform terms of service
- May produce false positives/negatives

## Support & Updates

### Maintenance
- Regular updates for platform changes
- Security patches for dependencies
- Performance optimizations
- New platform integrations

### Training
- Operator training recommended
- Understanding of facial recognition limitations
- Legal and ethical guidelines
- Technical troubleshooting

---

**Version**: 1.0.0  
**Last Updated**: January 2024  
**Classification**: Law Enforcement Use Only

For technical support or training requests, contact your agency's digital forensics unit.
