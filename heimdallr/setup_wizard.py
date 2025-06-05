#!/usr/bin/env python3
"""
Heimdallr Setup Wizard - Interactive Configuration for Law Enforcement
"""

import os
import json
import getpass
from pathlib import Path
from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.panel import Panel
from rich.table import Table
import secrets

console = Console()

class SetupWizard:
    """Interactive setup wizard for Heimdallr configuration"""
    
    def __init__(self):
        self.config_path = Path.home() / ".heimdallr_config.json"
        self.env_path = Path.cwd() / ".env"
        self.config_data = {}
    
    def run_wizard(self):
        """Run the complete setup wizard"""
        self.show_welcome()
        self.verify_authorization()
        self.collect_agency_info()
        self.configure_platforms()
        self.setup_api_keys()
        self.configure_security()
        self.save_configuration()
        self.show_completion()
    
    def show_welcome(self):
        """Display welcome screen"""
        console.print(Panel.fit(
            "[bold red]🚔 HEIMDALLR SETUP WIZARD[/bold red]\n"
            "[yellow]Advanced Facial Recognition Search Tool[/yellow]\n\n"
            "[bold red]⚠️  LAW ENFORCEMENT USE ONLY ⚠️[/bold red]\n"
            "[dim]This tool must only be used by authorized personnel\n"
            "with proper legal authority for investigations.[/dim]",
            border_style="red"
        ))
    
    def verify_authorization(self):
        """Verify operator authorization"""
        console.print("\n[bold]🔐 Authorization Verification[/bold]")
        
        badge_number = Prompt.ask("Badge/ID Number")
        agency = Prompt.ask("Agency Name")
        supervisor = Prompt.ask("Supervising Officer")
        case_authority = Prompt.ask("Legal Authority/Case Number")
        
        confirmed = Confirm.ask(
            f"\nConfirm authorization:\n"
            f"Badge: {badge_number}\n"
            f"Agency: {agency}\n"
            f"Supervisor: {supervisor}\n"
            f"Authority: {case_authority}\n"
            f"\nIs this information correct?"
        )
        
        if not confirmed:
            console.print("[red]Setup cancelled.[/red]")
            exit(1)
        
        self.config_data["authorization"] = {
            "badge_number": badge_number,
            "agency": agency,
            "supervisor": supervisor,
            "legal_authority": case_authority,
            "setup_timestamp": self._get_timestamp()
        }
    
    def collect_agency_info(self):
        """Collect agency information"""
        console.print("\n[bold]🏢 Agency Configuration[/bold]")
        
        agency_info = {
            "name": Prompt.ask("Full Agency Name"),
            "jurisdiction": Prompt.ask("Jurisdiction"),
            "state_country": Prompt.ask("State/Country"),
            "contact_email": Prompt.ask("Technical Contact Email"),
            "contact_phone": Prompt.ask("Emergency Contact Phone"),
            "cybercrime_unit": Prompt.ask("Cybercrime Unit Contact (optional)", default="N/A")
        }
        
        self.config_data["agency"] = agency_info
    
    def configure_platforms(self):
        """Configure platform preferences"""
        console.print("\n[bold]🌐 Platform Configuration[/bold]")
        
        platforms = {
            "instagram": "Instagram (public posts, hashtags)",
            "facebook": "Facebook (public pages, marketplace)",
            "twitter": "Twitter/X (tweets, profiles)", 
            "reddit": "Reddit (image subreddits, help communities)",
            "google_images": "Google Images (reverse search)"
        }
        
        platform_config = {}
        
        for platform, description in platforms.items():
            enabled = Confirm.ask(f"Enable {description}?", default=True)
            
            if enabled:
                aggressive = Confirm.ask(f"Use aggressive mode for {platform}?", default=False)
                rate_limit = Prompt.ask(
                    f"Rate limit delay for {platform} (seconds)", 
                    default="2.0"
                )
                
                platform_config[platform] = {
                    "enabled": True,
                    "aggressive_mode": aggressive,
                    "rate_limit_delay": float(rate_limit),
                    "max_requests_per_minute": 30 if not aggressive else 60
                }
            else:
                platform_config[platform] = {"enabled": False}
        
        self.config_data["platforms"] = platform_config
    
    def setup_api_keys(self):
        """Setup API keys for platforms"""
        console.print("\n[bold]🔑 API Keys Configuration[/bold]")
        console.print("[dim]API keys enable full platform functionality but are optional[/dim]")
        
        api_keys = {}
        
        # Twitter API
        if Confirm.ask("Configure Twitter API keys?"):
            console.print("\n[blue]Twitter API Setup:[/blue]")
            console.print("Get keys from: https://developer.twitter.com")
            
            api_keys.update({
                "TWITTER_API_KEY": Prompt.ask("Twitter API Key", password=True),
                "TWITTER_API_SECRET": Prompt.ask("Twitter API Secret", password=True),
                "TWITTER_ACCESS_TOKEN": Prompt.ask("Twitter Access Token", password=True),
                "TWITTER_ACCESS_TOKEN_SECRET": Prompt.ask("Twitter Access Token Secret", password=True),
                "TWITTER_BEARER_TOKEN": Prompt.ask("Twitter Bearer Token (optional)", default="", password=True)
            })
        
        # Reddit API
        if Confirm.ask("Configure Reddit API keys?"):
            console.print("\n[blue]Reddit API Setup:[/blue]")
            console.print("Get keys from: https://reddit.com/prefs/apps")
            
            api_keys.update({
                "REDDIT_CLIENT_ID": Prompt.ask("Reddit Client ID", password=True),
                "REDDIT_CLIENT_SECRET": Prompt.ask("Reddit Client Secret", password=True)
            })
        
        # Instagram (optional)
        if Confirm.ask("Configure Instagram credentials? (risky - may cause account suspension)"):
            console.print("\n[red]⚠️  Instagram Warning:[/red]")
            console.print("Using credentials may violate ToS and cause account suspension")
            
            if Confirm.ask("Continue anyway?"):
                api_keys.update({
                    "INSTAGRAM_USERNAME": Prompt.ask("Instagram Username"),
                    "INSTAGRAM_PASSWORD": Prompt.ask("Instagram Password", password=True)
                })
        
        self.api_keys = api_keys
    
    def configure_security(self):
        """Configure security settings"""
        console.print("\n[bold]🛡️  Security Configuration[/bold]")
        
        # Generate encryption key for sensitive data
        encryption_key = secrets.token_hex(32)
        
        security_config = {
            "encryption_key": encryption_key,
            "log_level": Prompt.ask(
                "Logging level", 
                choices=["DEBUG", "INFO", "WARNING", "ERROR"], 
                default="INFO"
            ),
            "audit_enabled": Confirm.ask("Enable audit logging?", default=True),
            "evidence_chain": Confirm.ask("Enable evidence chain tracking?", default=True),
            "secure_delete": Confirm.ask("Enable secure deletion of temporary files?", default=True),
            "network_timeout": int(Prompt.ask("Network timeout (seconds)", default="30")),
            "max_concurrent_searches": int(Prompt.ask("Max concurrent platform searches", default="3"))
        }
        
        # Browser settings
        browser_config = {
            "headless": Confirm.ask("Run browsers in headless mode?", default=True),
            "disable_images": Confirm.ask("Disable image loading (faster but may miss content)?", default=False),
            "user_agent_rotation": Confirm.ask("Enable user agent rotation?", default=True),
            "proxy_support": Confirm.ask("Enable proxy support?", default=False)
        }
        
        if browser_config["proxy_support"]:
            proxy_config = {
                "http_proxy": Prompt.ask("HTTP Proxy (optional)", default=""),
                "https_proxy": Prompt.ask("HTTPS Proxy (optional)", default=""),
                "proxy_auth": Confirm.ask("Proxy requires authentication?", default=False)
            }
            browser_config["proxy_config"] = proxy_config
        
        self.config_data["security"] = security_config
        self.config_data["browser"] = browser_config
    
    def save_configuration(self):
        """Save configuration files"""
        console.print("\n[bold]💾 Saving Configuration[/bold]")
        
        # Save main config
        with open(self.config_path, 'w') as f:
            json.dump(self.config_data, f, indent=2)
        
        # Set restrictive permissions
        self.config_path.chmod(0o600)
        
        # Save API keys to .env file
        if hasattr(self, 'api_keys') and self.api_keys:
            with open(self.env_path, 'w') as f:
                f.write("# Heimdallr API Keys - CONFIDENTIAL\n")
                f.write("# For law enforcement use only\n\n")
                for key, value in self.api_keys.items():
                    if value:  # Only save non-empty values
                        f.write(f"{key}={value}\n")
            
            self.env_path.chmod(0o600)
        
        console.print(f"✅ Configuration saved to {self.config_path}")
        if hasattr(self, 'api_keys'):
            console.print(f"✅ API keys saved to {self.env_path}")
    
    def show_completion(self):
        """Show completion summary"""
        
        # Create summary table
        table = Table(title="🎯 Setup Complete - Configuration Summary")
        table.add_column("Setting", style="cyan")
        table.add_column("Value", style="green")
        
        table.add_row("Agency", self.config_data["agency"]["name"])
        table.add_row("Operator", self.config_data["authorization"]["badge_number"])
        table.add_row("Platforms Enabled", str(sum(1 for p in self.config_data["platforms"].values() if p.get("enabled"))))
        table.add_row("API Keys Configured", str(len(getattr(self, 'api_keys', {}))))
        table.add_row("Audit Logging", "✅" if self.config_data["security"]["audit_enabled"] else "❌")
        table.add_row("Evidence Chain", "✅" if self.config_data["security"]["evidence_chain"] else "❌")
        
        console.print(table)
        
        console.print(Panel.fit(
            "[bold green]🚀 Heimdallr is Ready![/bold green]\n\n"
            "[yellow]Quick Start Commands:[/yellow]\n"
            f"[dim]heimdallr photo.jpg[/dim]\n"
            f"[dim]heimdallr photo.jpg --aggressive --threshold 85[/dim]\n"
            f"[dim]heimdallr photo.jpg --platforms instagram,reddit[/dim]\n\n"
            "[red]⚠️  Remember:[/red]\n"
            "[dim]• Obtain proper legal authority before use\n"
            "• All results require manual verification\n"
            "• Maintain chain of custody for evidence\n"
            "• Follow agency policies and procedures[/dim]",
            border_style="green"
        ))
    
    def _get_timestamp(self):
        """Get current timestamp"""
        from datetime import datetime
        return datetime.now().isoformat()

def main():
    """Main entry point for setup wizard"""
    wizard = SetupWizard()
    wizard.run_wizard()

if __name__ == "__main__":
    main()
