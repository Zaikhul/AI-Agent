"""
Multi-provider API management with async support and fallback
"""
import asyncio
import aiohttp
from typing import Dict, Any, Optional, List
from enum import Enum
from abc import ABC, abstractmethod

class ProviderType(Enum):
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GLM = "glm"

class APIProvider(ABC):
    """Abstract base class for API providers"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.provider_type = self._get_provider_type()
    
    @abstractmethod
    def _get_provider_type(self) -> ProviderType:
        pass
    
    @abstractmethod
    async def call_api(self, messages: List[Dict], **kwargs) -> Dict[str, Any]:
        pass
    
    @abstractmethod
    def parse_response(self, response: Dict) -> str:
        pass

class OpenAIProvider(APIProvider):
    """OpenAI API provider"""
    
    def _get_provider_type(self) -> ProviderType:
        return ProviderType.OPENAI
    
    async def call_api(self, messages: List[Dict], **kwargs) -> Dict[str, Any]:
        """Make async API call to OpenAI"""
        url = f"{self.config.get('base_url', 'https://api.openai.com/v1')}/chat/completions"
        
        headers = {
            "Authorization": f"Bearer {self.config['api_key']}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.config["model"],
            "messages": messages,
            "temperature": self.config.get("temperature", 0.7),
            "max_tokens": self.config.get("max_tokens", 4096),
            **kwargs
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=payload, timeout=120) as resp:
                if resp.status != 200:
                    error_text = await resp.text()
                    raise Exception(f"API call failed: {resp.status} - {error_text}")
                
                return await resp.json()
    
    def parse_response(self, response: Dict) -> str:
        """Parse OpenAI response"""
        return response["choices"][0]["message"]["content"]

class AnthropicProvider(APIProvider):
    """Anthropic Claude API provider"""
    
    def _get_provider_type(self) -> ProviderType:
        return ProviderType.ANTHROPIC
    
    async def call_api(self, messages: List[Dict], **kwargs) -> Dict[str, Any]:
        """Make async API call to Anthropic"""
        url = f"{self.config.get('base_url', 'https://api.anthropic.com')}/v1/messages"
        
        headers = {
            "x-api-key": self.config['api_key'],
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json"
        }
        
        # Convert OpenAI-style messages to Anthropic format
        system_msg = next((m["content"] for m in messages if m["role"] == "system"), None)
        user_messages = [m for m in messages if m["role"] != "system"]
        
        payload = {
            "model": self.config["model"],
            "messages": user_messages,
            "max_tokens": self.config.get("max_tokens", 4096),
            "temperature": self.config.get("temperature", 0.7),
            **kwargs
        }
        
        if system_msg:
            payload["system"] = system_msg
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=payload, timeout=120) as resp:
                if resp.status != 200:
                    error_text = await resp.text()
                    raise Exception(f"API call failed: {resp.status} - {error_text}")
                
                return await resp.json()
    
    def parse_response(self, response: Dict) -> str:
        """Parse Anthropic response"""
        return response["content"][0]["text"]

class ProviderManager:
    """Manages multiple API providers with fallback"""
    
    def __init__(self, config_manager: ConfigManager):
        self.config_manager = config_manager
        self.providers: Dict[str, APIProvider] = {}
        self._init_providers()
    
    def _init_providers(self):
        """Initialize available providers"""
        configs = self.config_manager.configs
        
        for name, config in configs.items():
            model = config.get("model", "")
            
            if "gpt" in model.lower() or "glm" in model.lower():
                self.providers[name] = OpenAIProvider(config)
            elif "claude" in model.lower():
                self.providers[name] = AnthropicProvider(config)
    
    @trace_operation("api_call")
    async def call_with_fallback(
        self,
        primary_provider: str,
        fallback_providers: List[str],
        messages: List[Dict],
        max_retries: int = 3,
        **kwargs
    ) -> Dict[str, Any]:
        """Call API with automatic fallback"""
        
        providers_to_try = [primary_provider] + fallback_providers
        last_error = None
        
        for provider_name in providers_to_try:
            if provider_name not in self.providers:
                continue
            
            provider = self.providers[provider_name]
            
            for attempt in range(max_retries):
                try:
                    observability.logger.log(
                        "info",
                        "api_call_attempt",
                        provider=provider_name,
                        attempt=attempt + 1
                    )
                    
                    start_time = time.time()
                    response = await provider.call_api(messages, **kwargs)
                    duration = time.time() - start_time
                    
                    # Record metrics
                    observability.metrics.record(
                        "api_call_duration",
                        duration,
                        tags={"provider": provider_name, "success": True}
                    )
                    
                    # Estimate token usage (simplified)
                    tokens_used = len(str(messages)) // 4 + len(str(response)) // 4
                    observability.metrics.record(
                        "tokens_used",
                        tokens_used,
                        tags={"provider": provider_name}
                    )
                    
                    parsed_content = provider.parse_response(response)
                    
                    return {
                        "success": True,
                        "content": parsed_content,
                        "provider": provider_name,
                        "duration": duration,
                        "tokens": tokens_used
                    }
                
                except Exception as e:
                    last_error = e
                    wait_time = 2 ** attempt  # Exponential backoff
                    
                    observability.log_error(
                        "api_call_failed",
                        str(e),
                        provider=provider_name,
                        attempt=attempt + 1
                    )
                    
                    if attempt < max_retries - 1:
                        observability.logger.log(
                            "warning",
                            "api_retry",
                            provider=provider_name,
                            wait_time=wait_time
                        )
                        await asyncio.sleep(wait_time)
        
        # All providers failed
        observability.logger.log(
            "error",
            "all_providers_failed",
            last_error=str(last_error)
        )
        
        return {
            "success": False,
            "error": str(last_error),
            "requires_escalation": True
        }