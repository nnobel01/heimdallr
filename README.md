# Heimdallr - Advanced Facial Recognition Search Tool

🚔 **LAW ENFORCEMENT USE ONLY** 🚔

## Overview

Heimdallr is a professional-grade facial recognition search tool designed exclusively for authorized law enforcement investigations. It searches across multiple platforms to locate instances of faces and similar individuals with comprehensive audit trails and evidence chain management.

## ⚠️ LEGAL DISCLAIMER

**THIS TOOL IS INTENDED FOR USE BY AUTHORIZED LAW ENFORCEMENT PERSONNEL ONLY**

- All searches must be conducted under proper legal authority
- Results are investigative leads only and require manual verification
- Respect applicable privacy laws and constitutional protections
- Maintain proper chain of custody for any evidence derived from this tool
- Document all uses in accordance with agency policies
- Results may include false positives - verify before acting

By using this tool, operator confirms proper legal authority and training.

## 🚀 Quick Installation

### Option 1: Automated Installation (Recommended)
```bash
# Download and run installation script
wget https://raw.githubusercontent.com/your-repo/heimdallr/main/scripts/deploy.sh
chmod +x deploy.sh
./deploy.sh
```

### Option 2: Docker Deployment
```bash
# Clone repository
git clone https://github.com/your-repo/heimdallr.git
cd heimdallr

# Build and run with Docker
docker-compose up -d heimdallr
docker-compose exec heimdallr heimdallr photo.jpg
```

### Option 3: Manual Installation
```bash
# Install system dependencies (Ubuntu/Debian)
sudo apt update && sudo apt install -y cmake build-essential libopencv-dev

# Clone and install
git clone https://github.com/your-repo/heimdallr.git
cd heimdallr
python3 install.py
```

## 🎯 Features

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
- Fallback mode when advanced libraries unavailable

### 📊 Professional Results
- **JSON/CSV Export**: Structured data for analysis
- **Evidence Chain**: Complete audit trail with integrity verification
- **Confidence Scoring**: High/Medium/Low match categories
- **Case Management**: Unique case IDs and metadata tracking
- **Investigation Recommendations**: Automated analysis and next steps

### 🛡️ Law Enforcement Features
- **Audit Logging**: Complete operation tracking for legal proceedings
- **Evidence Chain Management**: Cryptographic integrity verification
- **Secure Configuration**: Encrypted storage of sensitive data
- **Case Documentation**: Professional reporting with legal disclaimers
- **Multi-Operator Support**: User authentication and access controls

### 🔒 Security & Compliance
- **Anti-Detection**: User agent rotation, rate limiting, proxy support
- **Encrypted Storage**: Sensitive data protection with AES encryption
- **Secure Deletion**: Cryptographic wiping of temporary files
- **Network Security**: TLS verification, timeout controls
- **Privacy Controls**: Configurable data retention and deletion

## 📋 System Requirements

### Minimum Requirements
- Python 3.8+
- 4GB RAM
- 2GB disk space
- Internet connection
- Chrome/Chromium browser

### Recommended Configuration
- Python 3.9+
- 8GB RAM
- 10GB disk space
- High-speed internet
- Dedicated investigation workstation

### Supported Platforms
- Ubuntu 18.04+ / Debian 10+
- macOS 10.15+
- Windows 10+ (with WSL recommended)
- Docker containers

## ⚙️ Configuration

### Initial Setup Wizard
```bash
# Run interactive setup wizard
python3 -m heimdallr.setup_wizard
```

The setup wizard will configure:
- Agency information and operator credentials
- Platform preferences and rate limiting
- API keys for enhanced functionality
- Security settings and encryption
- Audit logging and evidence management

### API Keys (Optional but Recommended)

#### Twitter API (Enhanced tweet search)
1. Apply at: https://developer.twitter.com
2. Create app and generate keys
3. Add to configuration during setup

#### Reddit API (Advanced subreddit search)
1. Create app at: https://reddit.com/prefs/apps
2. Note client ID and secret
3. Configure during setup

#### Instagram (Risky - may cause suspension)
- Not recommended for production use
- Use web scraping mode instead

### Configuration Files
- `~/.heimdallr_config.json` - Main configuration
- `.env` - API keys and sensitive data
- `~/.heimdallr_audit.log` - Audit trail (read-only)

## 📖 Usage Guide

### Basic Commands
```bash
# Simple face search
heimdallr photo.jpg

# Specify output directory and format
heimdallr photo.jpg --output case_2024_001 --format json

# Set custom similarity threshold
heimdallr photo.jpg --threshold 85

# Search specific platforms only
heimdallr photo.jpg --platforms instagram,reddit,google_images
```

### Advanced Options
```bash
# Aggressive search mode (higher speed, detection risk)
heimdallr photo.jpg --aggressive

# Verbose logging for debugging
heimdallr photo.jpg --verbose

# Custom configuration file
heimdallr photo.jpg --config /path/to/custom/config.json

# Platform-specific searches
heimdallr photo.jpg --platforms social  # Instagram, Facebook, Twitter, Reddit
heimdallr photo.jpg --platforms web     # Google Images, reverse search
heimdallr photo.jpg --platforms instagram,reddit  # Specific platforms
```

### Output Formats

#### JSON Output (Default)
```json
{
  "case_metadata": {
    "case_id": "HEIMDALLR-A1B2C3D4",
    "timestamp": "2024-01-15T10:30:00Z",
    "operator": "Badge123",
    "agency": "Metro Police Dept",
    "legal_authority": "Warrant 2024-001"
  },
  "search_summary": {
    "total_platforms_searched": 5,
    "total_matches_found": 12,
    "search_duration": 127.3,
    "high_confidence_matches": 3
  },
  "high_confidence_matches": [
    {
      "evidence_id": "INSTAGRAM-001",
      "platform": "instagram",
      "similarity_score": 96.8,
      "url": "https://instagram.com/p/xyz",
      "discovery_timestamp": "2024-01-15T10:32:15Z",
      "chain_of_custody": {
        "discovered_by": "HEIMDALLR",
        "collection_method": "automated_search",
        "verification_needed": true
      }
    }
  ],
  "evidence_chain": [...],
  "investigation_recommendations": [
    "PRIORITY: 3 high-confidence matches (95%+) require immediate manual verification",
    "LEGAL: Ensure proper legal authority before acting on any matches"
  ]
}
```

#### CSV Output
Spreadsheet-friendly format with columns:
- Evidence_ID, Platform, Similarity_Score, Confidence_Category
- URL, Image_URL, Context, Discovery_Time
- Verification_Status, Notes

## 🔍 Investigation Workflow

### 1. Case Preparation
- Obtain proper legal authority (warrant, court order, etc.)
- Document investigative necessity
- Prepare high-quality subject photographs
- Configure case-specific parameters

### 2. Search Execution
```bash
# Start comprehensive search
heimdallr subject_photo.jpg --output case_2024_001 --format both

# Monitor progress and logs
tail -f ~/.heimdallr_audit.log
```

### 3. Results Analysis
- Review high-confidence matches first (95%+)
- Examine medium-confidence matches (85-94%)
- Follow investigation recommendations
- Document verification steps

### 4. Evidence Management
- Export results in both JSON and CSV formats
- Maintain chain of custody documentation
- Verify all matches through independent means
- Prepare reports for legal proceedings

### 5. Case Documentation
- Save complete audit trail
- Document verification procedures
- Prepare investigative summary
- Archive evidence according to agency policy

## 🛠️ Troubleshooting

### Common Issues

#### "No faces detected"
- Ensure clear, frontal face images
- Check image quality and resolution
- Try different face detection models
- Verify image file integrity

#### "Rate limited" errors
- Reduce search aggressiveness
- Increase rate limiting delays
- Use different IP address/proxy
- Wait and retry later

#### API authentication failures
- Verify API keys in configuration
- Check key expiration dates
- Confirm account status
- Review API usage limits

#### Selenium/Browser errors
- Update Chrome/Chromium browser
- Install latest ChromeDriver
- Check browser permissions
- Verify network connectivity

### Performance Optimization

#### For Large-Scale Operations
```bash
# Use aggressive mode with caution
heimdallr photo.jpg --aggressive --platforms instagram,reddit

# Batch processing multiple subjects
for photo in case_photos/*.jpg; do
    heimdallr "$photo" --output "results/$(basename $photo .jpg)"
done
```

#### Memory and CPU Optimization
- Close unnecessary applications
- Use SSD storage for cache
- Increase virtual memory if needed
- Consider distributed processing

### Error Recovery
- Check audit logs for detailed error information
- Verify network connectivity and firewall settings
- Restart services if browser drivers crash
- Use fallback mode if face recognition fails

## 📊 Platform-Specific Notes

### Instagram
- **Strengths**: Large user base, good image quality
- **Limitations**: Aggressive anti-scraping, requires careful rate limiting
- **Best Practices**: Use hashtag searches, avoid direct profile access

### Facebook
- **Strengths**: Comprehensive user profiles, marketplace listings
- **Limitations**: Heavy restrictions on automated access
- **Best Practices**: Focus on public pages and marketplace

### Twitter/X
- **Strengths**: Real-time content, API access available
- **Limitations**: Rate limiting, API costs
- **Best Practices**: Use API when possible, focus on image tweets

### Reddit
- **Strengths**: Open communities, missing persons subreddits
- **Limitations**: Volunteer moderators, varied image quality
- **Best Practices**: Search help and missing persons communities

### Google Images
- **Strengths**: Comprehensive reverse search, high accuracy
- **Limitations**: CAPTCHA challenges, detection risk
- **Best Practices**: Use as primary search method, respect rate limits

## 🔒 Security Considerations

### Operational Security
- Use dedicated investigation workstations
- Enable full disk encryption
- Use VPN for sensitive investigations
- Regularly update software components
- Monitor for detection/blocking

### Data Protection
- Encrypt all configuration files
- Secure API keys and credentials
- Implement secure deletion procedures
- Maintain access logs and audit trails
- Follow agency data retention policies

### Legal Compliance
- Document legal authority for each search
- Maintain chain of custody records
- Respect platform terms of service
- Consider international jurisdiction issues
- Prepare for legal discovery requests

### Privacy Safeguards
- Only search publicly available content
- Avoid collection of unrelated data
- Implement data minimization practices
- Provide notice when legally required
- Respect constitutional protections

## 📚 Training and Certification

### Operator Training Requirements
- Understanding of facial recognition limitations
- Legal and ethical guidelines
- Technical troubleshooting skills
- Evidence handling procedures
- Report writing and documentation

### Recommended Training Program
1. **Technical Foundation** (8 hours)
   - Tool capabilities and limitations
   - Platform-specific search strategies
   - Configuration and customization
   - Troubleshooting common issues

2. **Legal and Ethical Training** (4 hours)
   - Constitutional considerations
   - Privacy laws and regulations
   - Evidence handling requirements
   - Documentation standards

3. **Practical Exercises** (8 hours)
   - Case study walkthroughs
   - Hands-on search practice
   - Report preparation
   - Quality assurance procedures

### Certification Maintenance
- Annual recertification required
- Continuing education on new platforms
- Legal update training
- Technical skills assessment

## 📞 Support and Updates

### Technical Support
- **Documentation**: Complete user manual and API reference
- **Issue Tracking**: GitHub issues for bug reports
- **Community**: Law enforcement user community
- **Training**: Professional training programs available

### Maintenance Schedule
- **Monthly**: Security patches and bug fixes
- **Quarterly**: Platform adapter updates
- **Annually**: Major feature releases
- **Emergency**: Critical security updates

### Version Control
- Semantic versioning (MAJOR.MINOR.PATCH)
- Automated security scanning
- Regression testing for all updates
- Rollback procedures for failed updates

## 📜 License and Distribution

### Licensing
- Restricted to authorized law enforcement agencies
- Requires signed license agreement
- Subject to export control regulations
- Non-transferable between agencies

### Distribution Control
- Secure distribution channels only
- Digital signature verification required
- Access logging and audit trails
- Revocation capabilities for compromised installations

---

**Version**: 1.0.0  
**Last Updated**: January 2024  
**Classification**: Law Enforcement Use Only  
**Support**: [Contact your agency's digital forensics unit]

## 🚨 Emergency Contact

For urgent technical issues during active investigations:
- Technical Hotline: [Agency Specific]
- Emergency Escalation: [24/7 Support]
- Legal Consultation: [Agency Legal Counsel]

---

*This software is provided for law enforcement use only. Unauthorized use, modification, or distribution is strictly prohibited and may be subject to criminal and civil penalties.*
