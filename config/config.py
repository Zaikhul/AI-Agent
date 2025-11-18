"""
configuration management with validation and security
"""
import os
import json
from pathlib import Path
from typing import Dict, Any, Optional
from dotenv import load_dotenv
import hashlib
from datetime import datetime

load_dotenv()

class ConfigValidator:
    """Validates and secures configuration"""
    
    @staticmethod
    def validate_api_key(key: str, provider: str) -> bool:
        """Validate API key format"""
        if not key or key == "your_key_here":
            raise ValueError(f"Invalid API key for {provider}")
        return True
    
    @staticmethod
    def mask_api_key(key: str) -> str:
        """Mask API key for logging"""
        if len(key) <= 8:
            return "***"
        return f"{key[:4]}...{key[-4:]}"

class ConfigManager:
    """Centralized configuration management with versioning"""
    
    def __init__(self, config_path: str = "config/llm_config.json"):
        self.config_path = Path(config_path)
        self.config_version = self._get_config_version()
        self.configs = self._load_configs()
        
    def _get_config_version(self) -> str:
        """Get config file version based on hash"""
        if not self.config_path.exists():
            return "unknown"
        
        with open(self.config_path, 'rb') as f:
            file_hash = hashlib.md5(f.read()).hexdigest()[:8]
        return f"v{datetime.now().strftime('%Y%m%d')}-{file_hash}"
    
    def _load_configs(self) -> Dict[str, Any]:
        """Load and validate configurations"""
        with open(self.config_path, 'r') as f:
            configs = json.load(f)
        
        # Resolve environment variables
        for config_name, config in configs.items():
            for key, value in config.items():
                if isinstance(value, str) and value.startswith("${"):
                    env_var = value[2:-1]
                    resolved_value = os.getenv(env_var)
                    
                    if key in ["api_key", "api_base"] and resolved_value:
                        ConfigValidator.validate_api_key(resolved_value, config_name)
                    
                    config[key] = resolved_value
        
        return configs
    
    def get_config(self, config_name: str) -> Dict[str, Any]:
        """Get configuration by name with metadata"""
        if config_name not in self.configs:
            raise ValueError(f"Config '{config_name}' not found")
        
        config = self.configs[config_name].copy()
        
        return {
            "config_list": [config],
            "timeout": config.get("timeout", 120),
            "cache_seed": None,  # Disable caching for reproducibility
        }
    
    def get_config_info(self) -> Dict[str, Any]:
        """Get configuration metadata for auditing"""
        return {
            "version": self.config_version,
            "loaded_at": datetime.now().isoformat(),
            "configs": list(self.configs.keys()),
            "path": str(self.config_path.absolute())
        }