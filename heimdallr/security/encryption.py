"""
Security and encryption utilities for Heimdallr
"""

import os
import hashlib
import secrets
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
from pathlib import Path
import json
from typing import Dict, Any, Optional

class SecurityManager:
    """Manages encryption, secure storage, and audit trails"""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or str(Path.home() / ".heimdallr_config.json")
        self.key = None
        self._load_encryption_key()
    
    def _load_encryption_key(self):
        """Load or generate encryption key"""
        try:
            with open(self.config_path, 'r') as f:
                config = json.load(f)
                key_hex = config.get("security", {}).get("encryption_key")
                
                if key_hex:
                    self.key = Fernet(base64.urlsafe_b64encode(bytes.fromhex(key_hex)[:32]))
                else:
                    self._generate_new_key()
        except (FileNotFoundError, json.JSONDecodeError):
            self._generate_new_key()
    
    def _generate_new_key(self):
        """Generate new encryption key"""
        key_bytes = secrets.token_bytes(32)
        self.key = Fernet(base64.urlsafe_b64encode(key_bytes))
    
    def encrypt_sensitive_data(self, data: str) -> str:
        """Encrypt sensitive data"""
        if not self.key:
            return data
        
        encrypted = self.key.encrypt(data.encode())
        return base64.b64encode(encrypted).decode()
    
    def decrypt_sensitive_data(self, encrypted_data: str) -> str:
        """Decrypt sensitive data"""
        if not self.key:
            return encrypted_data
        
        try:
            encrypted_bytes = base64.b64decode(encrypted_data.encode())
            decrypted = self.key.decrypt(encrypted_bytes)
            return decrypted.decode()
        except Exception:
            return encrypted_data  # Return as-is if decryption fails
    
    def hash_file(self, file_path: str) -> str:
        """Generate SHA-256 hash of file for integrity verification"""
        sha256_hash = hashlib.sha256()
        try:
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(chunk)
            return sha256_hash.hexdigest()
        except FileNotFoundError:
            return ""
    
    def secure_delete(self, file_path: str, passes: int = 3) -> bool:
        """Securely delete file by overwriting with random data"""
        try:
            if not os.path.exists(file_path):
                return True
            
            file_size = os.path.getsize(file_path)
            
            with open(file_path, "r+b") as file:
                for _ in range(passes):
                    file.seek(0)
                    file.write(secrets.token_bytes(file_size))
                    file.flush()
                    os.fsync(file.fileno())
            
            os.remove(file_path)
            return True
            
        except Exception:
            # Fallback to normal deletion
            try:
                os.remove(file_path)
                return True
            except:
                return False
    
    def create_audit_entry(self, action: str, details: Dict[str, Any]) -> Dict[str, Any]:
        """Create audit log entry"""
        from datetime import datetime
        
        audit_entry = {
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "details": details,
            "integrity_hash": self._calculate_entry_hash(action, details)
        }
        
        return audit_entry
    
    def _calculate_entry_hash(self, action: str, details: Dict[str, Any]) -> str:
        """Calculate integrity hash for audit entry"""
        data = f"{action}{json.dumps(details, sort_keys=True)}"
        return hashlib.sha256(data.encode()).hexdigest()

class AuditLogger:
    """Audit logging for law enforcement compliance"""
    
    def __init__(self, log_path: Optional[str] = None):
        self.log_path = log_path or str(Path.home() / ".heimdallr_audit.log")
        self.security_manager = SecurityManager()
    
    def log_search_start(self, image_path: str, operator_id: str, case_id: str):
        """Log start of facial recognition search"""
        entry = self.security_manager.create_audit_entry(
            "SEARCH_START",
            {
                "image_path": image_path,
                "operator_id": operator_id,
                "case_id": case_id,
                "image_hash": self.security_manager.hash_file(image_path)
            }
        )
        self._write_audit_entry(entry)
    
    def log_platform_search(self, platform: str, query_type: str, results_count: int):
        """Log platform-specific search"""
        entry = self.security_manager.create_audit_entry(
            "PLATFORM_SEARCH",
            {
                "platform": platform,
                "query_type": query_type,
                "results_count": results_count
            }
        )
        self._write_audit_entry(entry)
    
    def log_match_found(self, platform: str, similarity_score: float, url: str):
        """Log when a match is found"""
        entry = self.security_manager.create_audit_entry(
            "MATCH_FOUND",
            {
                "platform": platform,
                "similarity_score": similarity_score,
                "url_hash": hashlib.sha256(url.encode()).hexdigest()  # Hash URL for privacy
            }
        )
        self._write_audit_entry(entry)
    
    def log_results_export(self, export_format: str, file_path: str, operator_id: str):
        """Log results export"""
        entry = self.security_manager.create_audit_entry(
            "RESULTS_EXPORT",
            {
                "format": export_format,
                "file_path": file_path,
                "operator_id": operator_id,
                "file_hash": self.security_manager.hash_file(file_path)
            }
        )
        self._write_audit_entry(entry)
    
    def log_error(self, error_type: str, error_message: str, context: Dict[str, Any]):
        """Log errors and exceptions"""
        entry = self.security_manager.create_audit_entry(
            "ERROR",
            {
                "error_type": error_type,
                "error_message": error_message,
                "context": context
            }
        )
        self._write_audit_entry(entry)
    
    def _write_audit_entry(self, entry: Dict[str, Any]):
        """Write audit entry to log file"""
        try:
            with open(self.log_path, 'a') as f:
                f.write(json.dumps(entry) + "\n")
            
            # Set restrictive permissions
            os.chmod(self.log_path, 0o600)
            
        except Exception as e:
            # Critical: if audit logging fails, we should know
            print(f"CRITICAL: Audit logging failed: {e}")

class EvidenceChain:
    """Manages evidence chain of custody for legal compliance"""
    
    def __init__(self):
        self.chain = []
        self.security_manager = SecurityManager()
    
    def add_link(self, action: str, operator_id: str, timestamp: str, 
                 file_hash: str, details: Dict[str, Any]) -> str:
        """Add link to evidence chain"""
        link_id = secrets.token_hex(8)
        
        link = {
            "link_id": link_id,
            "action": action,
            "operator_id": operator_id,
            "timestamp": timestamp,
            "file_hash": file_hash,
            "details": details,
            "chain_hash": self._calculate_chain_hash()
        }
        
        self.chain.append(link)
        return link_id
    
    def verify_chain_integrity(self) -> bool:
        """Verify evidence chain integrity"""
        for i, link in enumerate(self.chain):
            # Recalculate hash for this point in chain
            temp_chain = self.chain[:i]
            expected_hash = self._calculate_chain_hash(temp_chain)
            
            if link["chain_hash"] != expected_hash:
                return False
        
        return True
    
    def export_chain(self) -> Dict[str, Any]:
        """Export evidence chain for legal proceedings"""
        return {
            "evidence_chain": self.chain,
            "total_links": len(self.chain),
            "integrity_verified": self.verify_chain_integrity(),
            "export_timestamp": self._get_timestamp(),
            "chain_signature": self._calculate_chain_hash()
        }
    
    def _calculate_chain_hash(self, chain_subset: Optional[list] = None) -> str:
        """Calculate hash of entire chain for integrity verification"""
        chain_data = chain_subset or self.chain[:-1]  # Exclude current link when calculating
        chain_str = json.dumps(chain_data, sort_keys=True)
        return hashlib.sha256(chain_str.encode()).hexdigest()
    
    def _get_timestamp(self) -> str:
        """Get current timestamp"""
        from datetime import datetime
        return datetime.now().isoformat()
