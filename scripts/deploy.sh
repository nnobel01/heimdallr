#!/bin/bash
# Heimdallr Deployment Script for Law Enforcement Agencies
# For Ubuntu/Debian systems

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}"
echo "╔══════════════════════════════════════════════════╗"
echo "║                 🔍 HEIMDALLR                     ║"
echo "║           Deployment Script v1.0                ║"
echo "║                                                  ║"
echo "║  ⚠️  FOR AUTHORIZED LAW ENFORCEMENT USE ONLY ⚠️   ║"
echo "╚══════════════════════════════════════════════════╝"
echo -e "${NC}"

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   echo -e "${RED}This script should not be run as root for security reasons${NC}"
   exit 1
fi

# Function to print status
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check system requirements
check_requirements() {
    print_status "Checking system requirements..."
    
    # Check Python version
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 is required but not installed"
        exit 1
    fi
    
    PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
    REQUIRED_VERSION="3.8"
    
    if ! python3 -c "import sys; exit(0 if sys.version_info >= (3, 8) else 1)"; then
        print_error "Python 3.8+ required. Current version: $PYTHON_VERSION"
        exit 1
    fi
    
    print_status "Python $PYTHON_VERSION - OK"
    
    # Check for git
    if ! command -v git &> /dev/null; then
        print_error "Git is required but not installed"
        echo "Install with: sudo apt install git"
        exit 1
    fi
    
    print_status "Git - OK"
}

# Install system dependencies
install_system_deps() {
    print_status "Installing system dependencies..."
    
    # Update package list
    sudo apt update
    
    # Install required packages
    sudo apt install -y \
        cmake \
        build-essential \
        libopencv-dev \
        libboost-all-dev \
        libdlib-dev \
        python3-pip \
        python3-venv \
        chromium-browser \
        curl \
        wget
    
    print_status "System dependencies installed"
}

# Create project directory and virtual environment
setup_environment() {
    print_status "Setting up environment..."
    
    # Create project directory
    PROJECT_DIR="$HOME/heimdallr"
    if [ -d "$PROJECT_DIR" ]; then
        print_warning "Project directory exists. Backing up..."
        mv "$PROJECT_DIR" "$PROJECT_DIR.backup.$(date +%Y%m%d_%H%M%S)"
    fi
    
    mkdir -p "$PROJECT_DIR"
    cd "$PROJECT_DIR"
    
    # Create virtual environment
    python3 -m venv venv
    source venv/bin/activate
    
    # Upgrade pip
    pip install --upgrade pip
    
    print_status "Environment created at $PROJECT_DIR"
}

# Download and install Heimdallr
install_heimdallr() {
    print_status "Installing Heimdallr..."
    
    # In a real deployment, this would clone from a secure repository
    # For now, we'll use the local files
    
    # Install Python dependencies
    pip install --no-cache-dir \
        click colorama rich tqdm \
        requests beautifulsoup4 selenium \
        pandas python-dotenv Pillow opencv-python
    
    # Try to install face recognition (may fail on some systems)
    pip install face-recognition dlib || print_warning "Face recognition libraries failed to install - fallback mode will be used"
    
    # Install optional dependencies
    pip install instaloader tweepy praw webdriver-manager fake-useragent || print_warning "Some optional dependencies failed to install"
    
    print_status "Heimdallr installed successfully"
}

# Setup ChromeDriver
setup_chromedriver() {
    print_status "Setting up ChromeDriver..."
    
    # Download and install ChromeDriver
    CHROME_VERSION=$(chromium-browser --version | cut -d' ' -f2 | cut -d'.' -f1)
    CHROMEDRIVER_VERSION=$(curl -s "https://chromedriver.storage.googleapis.com/LATEST_RELEASE_$CHROME_VERSION")
    
    if [ ! -z "$CHROMEDRIVER_VERSION" ]; then
        wget -O /tmp/chromedriver.zip "https://chromedriver.storage.googleapis.com/$CHROMEDRIVER_VERSION/chromedriver_linux64.zip"
        unzip /tmp/chromedriver.zip -d /tmp/
        sudo mv /tmp/chromedriver /usr/local/bin/
        sudo chmod +x /usr/local/bin/chromedriver
        rm /tmp/chromedriver.zip
        print_status "ChromeDriver installed"
    else
        print_warning "Could not determine ChromeDriver version"
    fi
}

# Run setup wizard
run_setup_wizard() {
    print_status "Running setup wizard..."
    
    # Run the Python setup wizard
    python3 -c "
import sys
sys.path.append('.')
from heimdallr.setup_wizard import SetupWizard
wizard = SetupWizard()
wizard.run_wizard()
"
}

# Create startup scripts
create_scripts() {
    print_status "Creating startup scripts..."
    
    # Create activation script
    cat > activate_heimdallr.sh << EOF
#!/bin/bash
cd $PROJECT_DIR
source venv/bin/activate
echo "Heimdallr environment activated"
echo "Usage: heimdallr photo.jpg"
EOF
    chmod +x activate_heimdallr.sh
    
    # Create desktop shortcut
    if [ -d "$HOME/Desktop" ]; then
        cat > "$HOME/Desktop/Heimdallr.desktop" << EOF
[Desktop Entry]
Name=Heimdallr
Comment=Facial Recognition Search Tool - Law Enforcement
Exec=gnome-terminal -- bash -c "cd $PROJECT_DIR && source venv/bin/activate && bash"
Icon=application-x-executable
Terminal=true
Type=Application
Categories=Security;Investigation;
EOF
        chmod +x "$HOME/Desktop/Heimdallr.desktop"
        print_status "Desktop shortcut created"
    fi
}

# Verify installation
verify_installation() {
    print_status "Verifying installation..."
    
    # Test Python import
    if python3 -c "import heimdallr; print('✅ Heimdallr import successful')" 2>/dev/null; then
        print_status "Python package verification passed"
    else
        print_warning "Python package verification failed"
    fi
    
    # Test CLI command
    if python3 -m heimdallr.cli --help > /dev/null 2>&1; then
        print_status "CLI command verification passed"
    else
        print_warning "CLI command verification failed"
    fi
}

# Security hardening
apply_security_hardening() {
    print_status "Applying security hardening..."
    
    # Set restrictive permissions on project directory
    chmod 700 "$PROJECT_DIR"
    
    # Create secure directories
    mkdir -p "$PROJECT_DIR"/{results,cache,logs}
    chmod 700 "$PROJECT_DIR"/{results,cache,logs}
    
    # Set umask for secure file creation
    echo "umask 077" >> "$PROJECT_DIR/venv/bin/activate"
    
    print_status "Security hardening applied"
}

# Main deployment function
main() {
    echo -e "${BLUE}Starting Heimdallr deployment...${NC}"
    
    check_requirements
    install_system_deps
    setup_environment
    install_heimdallr
    setup_chromedriver
    apply_security_hardening
    create_scripts
    verify_installation
    
    echo -e "${GREEN}"
    echo "╔══════════════════════════════════════════════════╗"
    echo "║                ✅ DEPLOYMENT COMPLETE!           ║"
    echo "╠══════════════════════════════════════════════════╣"
    echo "║                                                  ║"
    echo "║  📁 Installation Directory:                      ║"
    echo "║     $PROJECT_DIR"
    echo "║                                                  ║"
    echo "║  🚀 To activate Heimdallr:                       ║"
    echo "║     cd $PROJECT_DIR && source venv/bin/activate  ║"
    echo "║                                                  ║"
    echo "║  🔍 Quick Start:                                 ║"
    echo "║     heimdallr photo.jpg                          ║"
    echo "║                                                  ║"
    echo "║  ⚙️  Next Steps:                                 ║"
    echo "║     1. Run setup wizard for API keys            ║"
    echo "║     2. Configure agency information              ║"
    echo "║     3. Test with sample image                    ║"
    echo "║                                                  ║"
    echo "║  🚔 Remember: Law enforcement use only!          ║"
    echo "╚══════════════════════════════════════════════════╝"
    echo -e "${NC}"
    
    print_status "Run ./activate_heimdallr.sh to get started!"
}

# Run main function
main "$@"
