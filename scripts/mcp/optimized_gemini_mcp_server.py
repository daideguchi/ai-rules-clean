#!/usr/bin/env python3
"""
💎 Optimized Gemini MCP Server
=============================
Enhanced Gemini MCP server with performance and security optimizations
"""

import asyncio
import os
import sys
import time
from pathlib import Path
from typing import Any, Dict, Optional

import google.generativeai as genai

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from scripts.mcp.optimized_mcp_base import MCPRequest, OptimizedMCPBase


class OptimizedGeminiMCPServer(OptimizedMCPBase):
    """
    Optimized Gemini MCP Server with:
    - Connection pooling for API calls
    - Retry logic with exponential backoff
    - Response caching
    - Enhanced error handling
    - Performance monitoring
    """

    def __init__(self):
        super().__init__("gemini")
        self.model = None
        self.response_cache = {}
        self.cache_ttl = 300  # 5 minutes cache TTL
        self.max_retries = 3
        self.base_delay = 1.0

        # Gemini-specific configuration
        self.model_config = {
            "temperature": 0.7,
            "top_p": 0.8,
            "top_k": 40,
            "max_output_tokens": 8192,
        }

    async def _server_initialize(self):
        """Initialize Gemini-specific components"""
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable is required")

        try:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel(
                "gemini-2.5-flash",
                generation_config=self.model_config
            )

            # Test the model with a simple query
            await self._test_model()

            self.logger.info("✅ Gemini model initialized successfully")

        except Exception as e:
            self.logger.error(f"❌ Failed to initialize Gemini model: {str(e)}")
            raise

    async def _test_model(self):
        """Test the Gemini model with a simple query"""
        try:
            test_prompt = "Hello, respond with just 'OK' if you're working."
            response = await self._call_gemini_with_retry(test_prompt)
            if "OK" not in response:
                raise ValueError("Model test failed - unexpected response")
        except Exception as e:
            raise ValueError(f"Model test failed: {str(e)}")

    async def _process_request_impl(self, request: MCPRequest) -> Any:
        """Process Gemini-specific requests"""
        method = request.method
        params = request.params

        if method == "generate_content":
            return await self._handle_generate_content(params)
        elif method == "chat":
            return await self._handle_chat(params)
        elif method == "analyze_code":
            return await self._handle_analyze_code(params)
        elif method == "get_model_info":
            return await self._handle_get_model_info()
        else:
            raise ValueError(f"Unknown method: {method}")

    async def _handle_generate_content(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle content generation requests"""
        prompt = params.get("prompt", "")
        context = params.get("context", "")

        if not prompt:
            raise ValueError("Prompt is required for content generation")

        # Check cache first
        cache_key = self._get_cache_key(prompt, context)
        cached_response = self._get_cached_response(cache_key)
        if cached_response:
            self.logger.info("📋 Returning cached response")
            return cached_response

        # Generate new content
        full_prompt = self._build_prompt(prompt, context)
        response_text = await self._call_gemini_with_retry(full_prompt)

        result = {
            "content": response_text,
            "model": "gemini-2.5-flash",
            "timestamp": time.time(),
            "cached": False
        }

        # Cache the response
        self._cache_response(cache_key, result)

        return result

    async def _handle_chat(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle chat requests"""
        message = params.get("message", "")
        chat_history = params.get("history", [])

        if not message:
            raise ValueError("Message is required for chat")

        # Build chat prompt with history
        prompt = self._build_chat_prompt(message, chat_history)
        response_text = await self._call_gemini_with_retry(prompt)

        return {
            "response": response_text,
            "model": "gemini-2.5-flash",
            "timestamp": time.time()
        }

    async def _handle_analyze_code(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle code analysis requests"""
        code = params.get("code", "")
        language = params.get("language", "python")
        analysis_type = params.get("type", "review")

        if not code:
            raise ValueError("Code is required for analysis")

        prompt = f"""You are a code analysis expert. Analyze the following {language} code.
        
Analysis type: {analysis_type}

Code:
```{language}
{code}
```

Provide a detailed analysis including:
1. Code quality and best practices
2. Potential issues or bugs
3. Performance considerations
4. Suggestions for improvement

Format your response as structured analysis."""

        response_text = await self._call_gemini_with_retry(prompt)

        return {
            "analysis": response_text,
            "code_length": len(code),
            "language": language,
            "analysis_type": analysis_type,
            "timestamp": time.time()
        }

    async def _handle_get_model_info(self) -> Dict[str, Any]:
        """Get model information"""
        return {
            "model_name": "gemini-2.5-flash",
            "capabilities": ["text_generation", "code_analysis", "chat"],
            "config": self.model_config,
            "status": "healthy" if self.model else "unhealthy"
        }

    def _build_prompt(self, prompt: str, context: str = "") -> str:
        """Build a comprehensive prompt"""
        system_prompt = """You are Gemini AI, a helpful and knowledgeable assistant. 
Provide accurate, detailed, and helpful responses. Focus on being informative and constructive."""

        if context:
            return f"{system_prompt}\n\nContext: {context}\n\nUser request: {prompt}"
        else:
            return f"{system_prompt}\n\nUser request: {prompt}"

    def _build_chat_prompt(self, message: str, history: list) -> str:
        """Build chat prompt with history"""
        prompt = "You are Gemini AI in a conversation. Maintain context and provide helpful responses.\n\n"

        # Add conversation history
        for i, turn in enumerate(history[-10:]):  # Last 10 turns
            user_msg = turn.get("user", "")
            assistant_msg = turn.get("assistant", "")

            if user_msg:
                prompt += f"User: {user_msg}\n"
            if assistant_msg:
                prompt += f"Gemini: {assistant_msg}\n"

        prompt += f"User: {message}\nGemini:"

        return prompt

    async def _call_gemini_with_retry(self, prompt: str) -> str:
        """Call Gemini with retry logic and exponential backoff"""
        last_error = None

        for attempt in range(self.max_retries):
            try:
                response = await asyncio.get_event_loop().run_in_executor(
                    None, self.model.generate_content, prompt
                )

                if response.text:
                    return response.text
                else:
                    raise ValueError("Empty response from Gemini")

            except Exception as e:
                last_error = e

                if attempt < self.max_retries - 1:
                    delay = self.base_delay * (2 ** attempt)
                    self.logger.warning(f"⚠️ Gemini call failed (attempt {attempt + 1}), retrying in {delay}s: {str(e)}")
                    await asyncio.sleep(delay)
                else:
                    self.logger.error(f"❌ Gemini call failed after {self.max_retries} attempts: {str(e)}")

        raise last_error

    def _get_cache_key(self, prompt: str, context: str = "") -> str:
        """Generate cache key for request"""
        import hashlib
        content = f"{prompt}:{context}"
        return hashlib.md5(content.encode()).hexdigest()

    def _get_cached_response(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """Get cached response if valid"""
        if cache_key in self.response_cache:
            cached_item = self.response_cache[cache_key]
            if time.time() - cached_item["timestamp"] < self.cache_ttl:
                result = cached_item["response"].copy()
                result["cached"] = True
                return result
            else:
                # Remove expired cache entry
                del self.response_cache[cache_key]

        return None

    def _cache_response(self, cache_key: str, response: Dict[str, Any]):
        """Cache response"""
        self.response_cache[cache_key] = {
            "response": response,
            "timestamp": time.time()
        }

        # Clean up old cache entries (keep last 100)
        if len(self.response_cache) > 100:
            oldest_keys = sorted(
                self.response_cache.keys(),
                key=lambda k: self.response_cache[k]["timestamp"]
            )[:50]

            for key in oldest_keys:
                del self.response_cache[key]

    async def _server_health_check(self) -> Dict[str, Any]:
        """Gemini-specific health check"""
        health_data = {
            "model_status": "healthy" if self.model else "unhealthy",
            "cache_size": len(self.response_cache),
            "api_key_configured": bool(os.getenv("GEMINI_API_KEY"))
        }

        # Test simple generation
        try:
            test_response = await self._call_gemini_with_retry("Health check test - respond with 'OK'")
            health_data["api_test"] = "passed" if "OK" in test_response else "failed"
        except Exception as e:
            health_data["api_test"] = f"failed: {str(e)}"

        return health_data


# Main execution
async def main():
    """Main function for running the server"""
    server = OptimizedGeminiMCPServer()

    try:
        await server.initialize()

        # Keep server running
        while server.get_status().value != "stopped":
            await asyncio.sleep(1)

            # Periodic health check
            if time.time() - server.last_health_check > server.health_check_interval:
                health = await server.health_check()
                server.logger.info(f"📊 Health check: {health['status']}")

    except KeyboardInterrupt:
        server.logger.info("🔄 Received shutdown signal")
    except Exception as e:
        server.logger.error(f"❌ Server error: {str(e)}")
    finally:
        await server.shutdown()


if __name__ == "__main__":
    asyncio.run(main())
