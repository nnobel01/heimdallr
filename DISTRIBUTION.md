# Heimdallr Distribution Package

## 📦 Distribution Contents

This package contains the complete Heimdallr facial recognition search tool for law enforcement use.

### Package Structure
```
heimdallr/
├── heimdallr/                 # Main application package
│   ├── cli.py                # Command-line interface
│   ├── core/                 # Core functionality
│   ├── scrapers/             # Platform scrapers
│   ├── security/             # Security and encryption
│   └── setup_wizard.py       # Interactive setup
├── scripts/                  # Installation and deployment
│   └── deploy.sh             # Automated deployment script
├── docker/                   # Container deployment
│   ├── Dockerfile            # Container definition
│   └── docker-compose.yml    # Multi-service deployment
├── docs/                     # Complete documentation
├── install.py                # Interactive installer
├── requirements.txt          # Python dependencies
├── requirements-full.txt     # Complete dependency list
├── setup.py                  # Package definition
└── README.md                 # Main documentation
```

## 🚀 Quick Start

### Option 1: Automated Installation (Recommended)
```bash
# Make installer executable
chmod +x install.py
python3 install.py
```

### Option 2: Script-Based Deployment
```bash
# For Ubuntu/Debian systems
chmod +x scripts/deploy.sh
./scripts/deploy.sh
```

### Option 3: Docker Container
```bash
# Build and run container
docker-compose up -d heimdallr
docker-compose exec heimdallr heimdallr photo.jpg
```

## 🔧 Manual Installation

### 1. System Dependencies
```bash
# Ubuntu/Debian
sudo apt update && sudo apt install -y cmake build-essential libopencv-dev chromium-browser

# macOS
brew install cmake opencv dlib chromium

# Windows (requires Visual Studio Build Tools)
# Install CMake from cmake.org
# Install Chrome browser
```

### 2. Python Dependencies
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
# or: venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements-full.txt

# Install Heimdallr
pip install -e .
```

### 3. Configuration
```bash
# Run setup wizard
python3 -m heimdallr.setup_wizard

# Or manual configuration
cp .env.example .env
# Edit .env with your API keys
```

## 🧪 Verification

### Test Installation
```bash
# Check CLI help
heimdallr --help

# Test with sample image
heimdallr test_image.jpg --verbose

# Verify all components
python3 -c "import heimdallr; print('✅ Installation successful')"
```

### Expected Output
```
🔍 HEIMDALLR
Advanced Facial Recognition Search
⚠️  Use responsibly and respect privacy

✅ Found 1 face(s) in image
🚀 Starting search across 5 platforms...
🎯 Search completed in X.Xs

🎯 Search Results Summary
[Results table showing platform matches]

✅ Search completed! Results saved to 'results'
```

## 📋 System Requirements

### Minimum Requirements
- **OS**: Ubuntu 18.04+, macOS 10.15+, Windows 10+
- **Python**: 3.8+
- **RAM**: 4GB
- **Storage**: 2GB free space
- **Network**: Broadband internet connection

### Recommended Specifications
- **OS**: Latest LTS/Stable releases
- **Python**: 3.9+
- **RAM**: 8GB+
- **Storage**: 10GB+ (for cache and results)
- **Network**: High-speed internet
- **Hardware**: Dedicated investigation workstation

### Dependencies
- **Core**: Python 3.8+, pip, virtualenv
- **System**: cmake, build-essential, OpenCV, Chrome/Chromium
- **Optional**: Docker (for container deployment)

## 🔑 API Configuration

### Required for Full Functionality
1. **Twitter API** (Enhanced tweet searching)
   - Developer account: https://developer.twitter.com
   - Required: API Key, API Secret, Access Tokens

2. **Reddit API** (Advanced subreddit access)
   - App registration: https://reddit.com/prefs/apps
   - Required: Client ID, Client Secret

### Optional Configurations
- **Instagram**: Credentials (not recommended - ToS violation risk)
- **Proxy Settings**: For advanced network configurations
- **Custom User Agents**: For stealth operations

## 🛡️ Security Setup

### File Permissions
```bash
# Secure configuration files
chmod 600 ~/.heimdallr_config.json
chmod 600 .env

# Secure results directory
chmod 700 results/
```

### Audit Logging
- All operations logged to `~/.heimdallr_audit.log`
- Evidence chain tracking enabled by default
- Encrypted storage for sensitive data

### Network Security
- TLS certificate verification enabled
- Rate limiting to avoid detection
- User agent rotation for anonymity

## 📊 Performance Tuning

### For High-Volume Operations
```bash
# Increase concurrent searches
export HEIMDALLR_MAX_WORKERS=6

# Enable aggressive mode (higher detection risk)
heimdallr photo.jpg --aggressive

# Use specific high-performance platforms
heimdallr photo.jpg --platforms google_images,reddit
```

### Memory Optimization
```bash
# Reduce cache size
export HEIMDALLR_CACHE_SIZE=100MB

# Enable cleanup mode
export HEIMDALLR_AUTO_CLEANUP=true
```

## 🐳 Docker Deployment

### Single Container
```bash
# Build image
docker build -t heimdallr:latest .

# Run container
docker run -it -v $(pwd)/results:/app/results heimdallr:latest

# Execute search
docker exec -it container_name heimdallr photo.jpg
```

### Full Stack with Database
```bash
# Start all services
docker-compose up -d

# Access web interface
open http://localhost:8080

# Run CLI in container
docker-compose exec heimdallr bash
```

## 🔧 Troubleshooting

### Common Installation Issues

#### Python Version Conflicts
```bash
# Use specific Python version
python3.9 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

#### CMake/Build Issues
```bash
# Ubuntu/Debian: Install build tools
sudo apt install build-essential cmake libboost-all-dev

# macOS: Install Xcode tools
xcode-select --install

# Windows: Install Visual Studio Build Tools
# Download from: https://visualstudio.microsoft.com/downloads/
```

#### ChromeDriver Issues
```bash
# Manual ChromeDriver installation
CHROME_VERSION=$(google-chrome --version | cut -d' ' -f3 | cut -d'.' -f1)
wget -O chromedriver.zip "https://chromedriver.storage.googleapis.com/LATEST_RELEASE_${CHROME_VERSION}/chromedriver_linux64.zip"
unzip chromedriver.zip
sudo mv chromedriver /usr/local/bin/
```

#### Permission Errors
```bash
# Fix ownership issues
sudo chown -R $USER:$USER ~/.heimdallr*
chmod 600 ~/.heimdallr_config.json
```

### Runtime Issues

#### "No faces detected"
- Use clear, high-resolution images
- Ensure frontal face visibility
- Try different face detection models
- Verify image file integrity

#### API Rate Limiting
- Reduce search frequency
- Use different IP addresses
- Configure proxy rotation
- Wait for rate limit reset

#### Network Connectivity
- Check firewall settings
- Verify DNS resolution
- Test with different networks
- Use VPN if geo-blocked

## 📞 Support

### Self-Service Resources
- **Documentation**: Complete user manual in `/docs`
- **FAQ**: Frequently asked questions and solutions
- **Community**: Law enforcement user forum
- **Updates**: Automated update notifications

### Professional Support
- **Technical Helpdesk**: 24/7 support for active investigations
- **Training Programs**: Certification and advanced techniques
- **Custom Development**: Agency-specific modifications
- **Legal Consultation**: Compliance and evidence handling

### Issue Reporting
```bash
# Generate diagnostic report
heimdallr --diagnose > diagnostic_report.txt

# Include in support request:
# - Diagnostic report
# - Error messages
# - Steps to reproduce
# - System information
```

## 🔄 Updates and Maintenance

### Automatic Updates
```bash
# Enable auto-updates
heimdallr --enable-auto-update

# Check for updates
heimdallr --check-updates

# Manual update
git pull origin main
pip install -r requirements.txt
```

### Backup and Recovery
```bash
# Backup configuration
cp ~/.heimdallr_config.json ~/heimdallr_config_backup.json

# Backup results
tar -czf heimdallr_results_backup.tar.gz results/

# Restore configuration
cp ~/heimdallr_config_backup.json ~/.heimdallr_config.json
```

### Version Management
- **Stable**: Production releases (recommended)
- **Beta**: Pre-release testing versions
- **Development**: Latest features (not recommended for investigations)

## 📜 Compliance and Legal

### Documentation Requirements
- Maintain installation logs
- Document configuration changes
- Keep audit trails for all searches
- Record operator training and certification

### Evidence Handling
- Follow agency digital evidence procedures
- Maintain chain of custody documentation
- Verify results through independent means
- Prepare reports for legal proceedings

### Privacy and Ethics
- Respect platform terms of service
- Follow applicable privacy laws
- Obtain proper legal authority
- Document investigative necessity

---

## 🚀 Ready to Deploy!

This distribution package provides everything needed for professional law enforcement deployment of Heimdallr. Choose your preferred installation method and follow the verification steps to ensure proper setup.

For additional assistance, consult the complete documentation or contact professional support services.

**Remember**: This tool is for authorized law enforcement use only. Ensure proper legal authority and training before conducting any searches.
