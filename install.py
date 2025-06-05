#!/usr/bin/env python3
"""
Heimdallr Installation Script
Automated setup for law enforcement agencies
"""

import os
import sys
import subprocess
import platform
from pathlib import Path
import json

class HeimdallrInstaller:
    def __init__(self):
        self.system = platform.system().lower()
        self.is_root = os.geteuid() == 0 if hasattr(os, 'geteuid') else False
        
    def print_banner(self):
        print("""
╔══════════════════════════════════════════════════╗
║                 🔍 HEIMDALLR                     ║
║         Law Enforcement Installation             ║
║                                                  ║
║  ⚠️  FOR AUTHORIZED LAW ENFORCEMENT USE ONLY ⚠️   ║
╚══════════════════════════════════════════════════╝
        """)

    def check_python_version(self):
        """Check Python version compatibility"""
        if sys.version_info < (3, 8):
            print("❌ Error: Python 3.8 or higher required")
            print(f"   Current version: {sys.version}")
            sys.exit(1)
        print(f"✅ Python {sys.version.split()[0]} - Compatible")

    def install_system_dependencies(self):
        """Install system-level dependencies"""
        print("\n📦 Installing system dependencies...")
        
        if self.system == "linux":
            self._install_linux_deps()
        elif self.system == "darwin":
            self._install_macos_deps()
        elif self.system == "windows":
            self._install_windows_deps()
        else:
            print("⚠️  Unknown system - manual dependency installation may be required")

    def _install_linux_deps(self):
        """Install Linux dependencies"""
        deps = [
            "cmake", "build-essential", "libopencv-dev", 
            "libdlib-dev", "libboost-all-dev", "chromium-browser"
        ]
        
        # Detect package manager
        if subprocess.run(["which", "apt"], capture_output=True).returncode == 0:
            cmd = ["apt", "update", "&&", "apt", "install", "-y"] + deps
            self._run_command(" ".join(cmd), shell=True, sudo=True)
        elif subprocess.run(["which", "yum"], capture_output=True).returncode == 0:
            yum_deps = ["cmake", "gcc-c++", "opencv-devel", "boost-devel", "chromium"]
            cmd = ["yum", "install", "-y"] + yum_deps
            self._run_command(" ".join(cmd), shell=True, sudo=True)
        else:
            print("⚠️  Please install cmake, build tools, and OpenCV manually")

    def _install_macos_deps(self):
        """Install macOS dependencies"""
        if subprocess.run(["which", "brew"], capture_output=True).returncode != 0:
            print("❌ Homebrew required. Install from: https://brew.sh")
            sys.exit(1)
        
        deps = ["cmake", "opencv", "dlib", "chromium"]
        cmd = ["brew", "install"] + deps
        self._run_command(cmd)

    def _install_windows_deps(self):
        """Install Windows dependencies"""
        print("📋 Windows Installation Notes:")
        print("1. Install Visual Studio Build Tools")
        print("2. Install CMake from cmake.org")
        print("3. Download Chrome browser")
        print("\nContinuing with Python dependencies...")

    def install_python_dependencies(self):
        """Install Python packages with proper error handling"""
        print("\n🐍 Installing Python dependencies...")
        
        # Core dependencies (always work)
        core_deps = [
            "click>=8.1.7", "colorama>=0.4.6", "rich>=13.7.0", "tqdm>=4.66.1",
            "requests>=2.31.0", "beautifulsoup4>=4.12.2", "pandas>=2.1.4",
            "python-dotenv>=1.0.0", "Pillow>=10.1.0", "opencv-python>=4.8.1.78"
        ]
        
        # Optional advanced dependencies
        advanced_deps = [
            "face-recognition>=1.3.0", "dlib>=19.24.2", "selenium>=4.15.2",
            "instaloader>=4.10.3", "tweepy>=4.14.0", "praw>=7.7.1"
        ]
        
        # Install core dependencies first
        print("Installing core dependencies...")
        for dep in core_deps:
            self._install_pip_package(dep, critical=True)
        
        # Install advanced dependencies with fallbacks
        print("Installing advanced dependencies...")
        for dep in advanced_deps:
            self._install_pip_package(dep, critical=False)
        
        # Install Heimdallr package
        self._run_command([sys.executable, "-m", "pip", "install", "-e", "."])

    def _install_pip_package(self, package, critical=True):
        """Install a single pip package with error handling"""
        try:
            cmd = [sys.executable, "-m", "pip", "install", package]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                print(f"✅ {package.split('>=')[0]}")
            else:
                if critical:
                    print(f"❌ Failed to install {package}: {result.stderr}")
                    sys.exit(1)
                else:
                    print(f"⚠️  Optional package {package} failed - continuing")
                    
        except subprocess.TimeoutExpired:
            if critical:
                print(f"❌ Timeout installing {package}")
                sys.exit(1)
            else:
                print(f"⚠️  Timeout installing optional package {package}")

    def setup_configuration(self):
        """Run configuration wizard"""
        print("\n⚙️  Configuration Setup")
        
        config_data = {
            "installation": {
                "version": "1.0.0",
                "install_date": str(Path(__file__).stat().st_ctime),
                "system": self.system
            },
            "agency_info": {},
            "api_keys": {},
            "platforms": {
                "instagram": {"enabled": True},
                "facebook": {"enabled": True},
                "twitter": {"enabled": True},
                "reddit": {"enabled": True},
                "google_images": {"enabled": True}
            }
        }
        
        # Agency Information
        print("\n📋 Agency Information:")
        config_data["agency_info"]["name"] = input("Agency Name: ").strip()
        config_data["agency_info"]["jurisdiction"] = input("Jurisdiction: ").strip()
        config_data["agency_info"]["contact"] = input("Technical Contact: ").strip()
        
        # API Keys Setup
        print("\n🔑 API Keys Configuration:")
        print("Note: API keys are optional but enable full functionality")
        
        if self._ask_yes_no("Configure Twitter API keys?"):
            self._setup_twitter_keys(config_data)
        
        if self._ask_yes_no("Configure Reddit API keys?"):
            self._setup_reddit_keys(config_data)
        
        # Save configuration
        config_path = Path.home() / ".heimdallr_config.json"
        with open(config_path, 'w') as f:
            json.dump(config_data, f, indent=2)
        
        print(f"✅ Configuration saved to {config_path}")

    def _setup_twitter_keys(self, config_data):
        """Setup Twitter API keys"""
        print("\nTwitter API Setup:")
        print("Get keys from: https://developer.twitter.com")
        
        config_data["api_keys"]["twitter_api_key"] = input("API Key: ").strip()
        config_data["api_keys"]["twitter_api_secret"] = input("API Secret: ").strip()
        config_data["api_keys"]["twitter_access_token"] = input("Access Token: ").strip()
        config_data["api_keys"]["twitter_access_token_secret"] = input("Access Token Secret: ").strip()
        config_data["api_keys"]["twitter_bearer_token"] = input("Bearer Token (optional): ").strip()

    def _setup_reddit_keys(self, config_data):
        """Setup Reddit API keys"""
        print("\nReddit API Setup:")
        print("Get keys from: https://reddit.com/prefs/apps")
        
        config_data["api_keys"]["reddit_client_id"] = input("Client ID: ").strip()
        config_data["api_keys"]["reddit_client_secret"] = input("Client Secret: ").strip()

    def verify_installation(self):
        """Verify the installation works"""
        print("\n🧪 Verifying installation...")
        
        try:
            # Test basic import
            result = subprocess.run([
                sys.executable, "-c", 
                "import heimdallr; print('✅ Heimdallr package imported successfully')"
            ], capture_output=True, text=True)
            
            if result.returncode != 0:
                print("❌ Package import failed")
                return False
            
            print(result.stdout.strip())
            
            # Test CLI command
            result = subprocess.run(["heimdallr", "--help"], capture_output=True, text=True)
            if result.returncode == 0:
                print("✅ CLI command working")
            else:
                print("⚠️  CLI command may need PATH update")
            
            return True
            
        except Exception as e:
            print(f"❌ Verification failed: {e}")
            return False

    def create_desktop_shortcuts(self):
        """Create desktop shortcuts and start menu entries"""
        print("\n🖥️  Creating shortcuts...")
        
        if self.system == "linux":
            self._create_linux_shortcuts()
        elif self.system == "darwin":
            self._create_macos_shortcuts()
        elif self.system == "windows":
            self._create_windows_shortcuts()

    def _create_linux_shortcuts(self):
        """Create Linux desktop shortcuts"""
        desktop_file = f"""[Desktop Entry]
Name=Heimdallr
Comment=Facial Recognition Search Tool - Law Enforcement
Exec=heimdallr
Icon=application-x-executable
Terminal=true
Type=Application
Categories=Security;Investigation;
"""
        
        desktop_path = Path.home() / "Desktop" / "Heimdallr.desktop"
        with open(desktop_path, 'w') as f:
            f.write(desktop_file)
        
        # Make executable
        desktop_path.chmod(0o755)
        print(f"✅ Desktop shortcut created: {desktop_path}")

    def _create_macos_shortcuts(self):
        """Create macOS shortcuts"""
        print("✅ macOS: Use Terminal to run 'heimdallr' command")

    def _create_windows_shortcuts(self):
        """Create Windows shortcuts"""
        print("✅ Windows: Heimdallr available in Command Prompt")

    def _ask_yes_no(self, question):
        """Ask yes/no question"""
        while True:
            answer = input(f"{question} (y/n): ").strip().lower()
            if answer in ['y', 'yes']:
                return True
            elif answer in ['n', 'no']:
                return False
            print("Please answer 'y' or 'n'")

    def _run_command(self, cmd, shell=False, sudo=False):
        """Run system command with proper error handling"""
        if sudo and not self.is_root:
            if isinstance(cmd, list):
                cmd = ["sudo"] + cmd
            else:
                cmd = f"sudo {cmd}"
        
        try:
            if shell:
                result = subprocess.run(cmd, shell=True, check=True)
            else:
                result = subprocess.run(cmd, check=True)
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Command failed: {e}")
            return False

    def run_installation(self):
        """Run complete installation process"""
        self.print_banner()
        
        print("🔍 Checking system requirements...")
        self.check_python_version()
        
        if self._ask_yes_no("Install system dependencies?"):
            self.install_system_dependencies()
        
        self.install_python_dependencies()
        self.setup_configuration()
        
        if self.verify_installation():
            self.create_desktop_shortcuts()
            
            print("""
╔══════════════════════════════════════════════════╗
║                 ✅ INSTALLATION COMPLETE!        ║
╠══════════════════════════════════════════════════╣
║                                                  ║
║  🚀 Quick Start:                                 ║
║     heimdallr photo.jpg                          ║
║                                                  ║
║  📖 Documentation:                               ║
║     heimdallr --help                             ║
║                                                  ║
║  ⚙️  Configuration:                              ║
║     ~/.heimdallr_config.json                     ║
║                                                  ║
║  🚔 Remember: Law enforcement use only!          ║
║     Obtain proper legal authority before use     ║
╚══════════════════════════════════════════════════╝
            """)
        else:
            print("❌ Installation verification failed. Please check logs above.")
            sys.exit(1)

if __name__ == "__main__":
    installer = HeimdallrInstaller()
    installer.run_installation()
