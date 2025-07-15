"""
Ollama API Client for LLM Penetration Testing
"""

import aiohttp
import asyncio
import json
import time
from typing import Optional, Dict, Any, List
from dataclasses import dataclass


@dataclass
class OllamaResponse:
    """Response from Ollama API"""
    content: str
    model: str
    response_time: float
    success: bool
    error: Optional[str] = None


class OllamaClient:
    """Async client for Ollama API"""
    
    def __init__(self, base_url: str = "http://localhost:11434", timeout: int = 30, max_retries: int = 3):
        self.base_url = base_url
        self.timeout = timeout
        self.max_retries = max_retries
        self.session = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=self.timeout)
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def _get_session(self):
        """Get or create session"""
        if not self.session:
            self.session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=self.timeout)
            )
        return self.session
    
    async def generate(self, model: str, prompt: str, system_prompt: Optional[str] = None) -> OllamaResponse:
        """Generate text using Ollama model"""
        session = await self._get_session()
        
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False
        }
        
        if system_prompt:
            payload["system"] = system_prompt
        
        start_time = time.time()
        
        for attempt in range(self.max_retries):
            try:
                async with session.post(f"{self.base_url}/api/generate", json=payload) as response:
                    response_time = time.time() - start_time
                    
                    if response.status == 200:
                        data = await response.json()
                        return OllamaResponse(
                            content=data.get("response", ""),
                            model=model,
                            response_time=response_time,
                            success=True
                        )
                    else:
                        error_text = await response.text()
                        if attempt == self.max_retries - 1:
                            return OllamaResponse(
                                content="",
                                model=model,
                                response_time=response_time,
                                success=False,
                                error=f"HTTP {response.status}: {error_text}"
                            )
                        
            except asyncio.TimeoutError:
                if attempt == self.max_retries - 1:
                    return OllamaResponse(
                        content="",
                        model=model,
                        response_time=time.time() - start_time,
                        success=False,
                        error="Request timeout"
                    )
                await asyncio.sleep(1)  # Wait before retry
                
            except Exception as e:
                if attempt == self.max_retries - 1:
                    return OllamaResponse(
                        content="",
                        model=model,
                        response_time=time.time() - start_time,
                        success=False,
                        error=str(e)
                    )
                await asyncio.sleep(1)  # Wait before retry
        
        return OllamaResponse(
            content="",
            model=model,
            response_time=time.time() - start_time,
            success=False,
            error="Max retries exceeded"
        )
    
    async def chat(self, model: str, messages: List[Dict[str, str]]) -> OllamaResponse:
        """Chat with Ollama model using message format"""
        session = await self._get_session()
        
        payload = {
            "model": model,
            "messages": messages,
            "stream": False
        }
        
        start_time = time.time()
        
        for attempt in range(self.max_retries):
            try:
                async with session.post(f"{self.base_url}/api/chat", json=payload) as response:
                    response_time = time.time() - start_time
                    
                    if response.status == 200:
                        data = await response.json()
                        message = data.get("message", {})
                        return OllamaResponse(
                            content=message.get("content", ""),
                            model=model,
                            response_time=response_time,
                            success=True
                        )
                    else:
                        error_text = await response.text()
                        if attempt == self.max_retries - 1:
                            return OllamaResponse(
                                content="",
                                model=model,
                                response_time=response_time,
                                success=False,
                                error=f"HTTP {response.status}: {error_text}"
                            )
                        
            except asyncio.TimeoutError:
                if attempt == self.max_retries - 1:
                    return OllamaResponse(
                        content="",
                        model=model,
                        response_time=time.time() - start_time,
                        success=False,
                        error="Request timeout"
                    )
                await asyncio.sleep(1)
                
            except Exception as e:
                if attempt == self.max_retries - 1:
                    return OllamaResponse(
                        content="",
                        model=model,
                        response_time=time.time() - start_time,
                        success=False,
                        error=str(e)
                    )
                await asyncio.sleep(1)
        
        return OllamaResponse(
            content="",
            model=model,
            response_time=time.time() - start_time,
            success=False,
            error="Max retries exceeded"
        )
    
    async def check_model_availability(self, model: str) -> bool:
        """Check if model is available"""
        try:
            models = await self.list_models()
            return model in models
        except:
            return False
    
    async def list_models(self) -> List[str]:
        """List available models"""
        session = await self._get_session()
        
        try:
            async with session.get(f"{self.base_url}/api/tags") as response:
                if response.status == 200:
                    data = await response.json()
                    models = data.get("models", [])
                    return [model["name"] for model in models]
                else:
                    return []
        except:
            return []
    
    async def close(self):
        """Close the session"""
        if self.session:
            await self.session.close()