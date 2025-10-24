"""LLM Service - Handles all LLM interactions via LiteLLM proxy"""

import httpx
import logging
from typing import Optional, Dict, Any
from tenacity import retry, stop_after_attempt, wait_exponential
from app.core.config import settings
from app.core.exceptions import LLMServiceException
from app.models.domain import LLMRequest, LLMResponse

logger = logging.getLogger(__name__)


class LLMService:
    """Service for LLM interactions"""
    
    def __init__(self):
        self.base_url = settings.LITELLM_URL
        self.timeout = settings.LITELLM_TIMEOUT
        self.max_retries = settings.LITELLM_MAX_RETRIES
        self.client = httpx.AsyncClient(timeout=self.timeout)
    
    async def __aenter__(self):
        """Async context manager entry"""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.client.aclose()
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    async def generate_completion(
        self,
        request: LLMRequest,
        stream: bool = False
    ) -> LLMResponse:
        """
        Generate completion from LLM
        
        Args:
            request: LLM request with prompt and parameters
            stream: Whether to stream the response
            
        Returns:
            LLMResponse with generated content
        """
        try:
            logger.info(f"Generating completion with model: {request.model}")
            
            # Prepare request payload for LiteLLM/OpenAI compatible API
            payload = {
                "model": request.model,
                "messages": [
                    {
                        "role": "user",
                        "content": request.prompt
                    }
                ],
                "max_tokens": request.max_tokens,
                "temperature": request.temperature,
                "top_p": request.top_p,
                "stream": stream
            }
            
            # Make request to LiteLLM proxy
            response = await self.client.post(
                f"{self.base_url}/chat/completions",
                json=payload,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {settings.LITELLM_MASTER_KEY}"
                }
            )
            
            response.raise_for_status()
            result = response.json()
            
            # Extract response data
            choice = result["choices"][0]
            content = choice["message"]["content"]
            
            # Extract token usage
            usage = result.get("usage", {})
            tokens_used = usage.get("total_tokens", 0)
            
            # Debug: Log content details
            print(f"DEBUG LLM Service: Content length: {len(content) if content else 0}")
            print(f"DEBUG LLM Service: Content preview: {content[:100] if content else 'None'}")
            print(f"DEBUG LLM Service: Content is empty: {not content}")
            
            # Save full content to file for inspection
            import os
            debug_file = "/app/storage/logs/llm_full_responses.log"
            os.makedirs(os.path.dirname(debug_file), exist_ok=True)
            
            with open(debug_file, "a", encoding="utf-8") as f:
                f.write(f"\n=== LLM FULL RESPONSE ===\n")
                f.write(f"Model: {request.model}\n")
                f.write(f"Tokens used: {tokens_used}\n")
                f.write(f"Content length: {len(content) if content else 0}\n")
                f.write(f"Content:\n{content}\n")
                f.write("=" * 100 + "\n")
            
            print(f"DEBUG LLM Service: Full response saved to {debug_file}")
            
            logger.info(
                f"Completion generated successfully. Tokens used: {tokens_used}"
            )
            
            return LLMResponse(
                content=content,
                model=result.get("model", request.model),
                tokens_used=tokens_used,
                finish_reason=choice.get("finish_reason", "stop"),
                metadata={
                    "usage": usage,
                    "model": result.get("model")
                }
            )
            
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error from LLM service: {e}")
            raise LLMServiceException(
                f"LLM service returned error: {e.response.status_code}",
                details={"status_code": e.response.status_code}
            )
        except httpx.RequestError as e:
            logger.error(f"Request error to LLM service: {e}")
            raise LLMServiceException(
                f"Failed to connect to LLM service: {str(e)}",
                details={"error": str(e)}
            )
        except Exception as e:
            logger.exception(f"Unexpected error in LLM service: {e}")
            raise LLMServiceException(
                f"Unexpected error: {str(e)}",
                details={"error": str(e)}
            )
    
    async def generate_code(
        self,
        prompt: str,
        model: str = "gemini-2.5-pro",  # Updated to Gemini 2.5 Pro
        max_tokens: int = 20000,  # Pushing to maximum possible limit for Gemini models
        temperature: float = 0.7
    ) -> str:
        """
        Generate code based on prompt
        
        Args:
            prompt: The code generation prompt
            model: LLM model to use
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            
        Returns:
            Generated code as string
        """
        request = LLMRequest(
            model=model,
            prompt=prompt,
            max_tokens=max_tokens,
            temperature=temperature
        )
        
        response = await self.generate_completion(request)
        return response.content
    
    async def health_check(self) -> bool:
        """
        Check if LLM service is healthy
        
        Returns:
            True if service is healthy
        """
        try:
            response = await self.client.get(f"{self.base_url}/health")
            return response.status_code == 200
        except Exception:
            return False


# Singleton instance
_llm_service: Optional[LLMService] = None


def get_llm_service() -> LLMService:
    """Get or create LLM service singleton"""
    global _llm_service
    if _llm_service is None:
        _llm_service = LLMService()
    return _llm_service

