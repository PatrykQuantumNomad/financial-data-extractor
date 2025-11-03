"""
OpenRouter API client wrapper with retry logic and cost tracking.

Uses OpenRouter to access multiple LLM providers for financial statement extraction.
Follows official OpenRouter API documentation: https://openrouter.ai/docs/quickstart

Author: Patryk Golabek
Copyright: 2025 Patryk Golabek
"""

import asyncio
import logging
import time
from typing import Any

import httpx
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

logger = logging.getLogger(__name__)


class OpenRouterClient:
    """Wrapper for OpenRouter API with retry logic and monitoring.

    Implements OpenRouter API best practices:
    - App attribution headers (HTTP-Referer, X-Title)
    - User tracking for analytics
    - Proper error handling and retries
    - Cost tracking
    """

    def __init__(
        self,
        api_key: str,
        base_url: str = "https://openrouter.ai/api/v1",
        default_model: str = "openai/gpt-4o-mini",
        timeout: int = 120,
        max_retries: int = 3,
        http_referer: str | None = None,
        x_title: str | None = None,
    ):
        """Initialize OpenRouter client.

        Args:
            api_key: OpenRouter API key.
            base_url: OpenRouter API base URL (defaults to official endpoint).
            default_model: Default model to use (provider/model format).
            timeout: Request timeout in seconds.
            max_retries: Maximum number of retries for failed requests.
            http_referer: Optional site URL for app attribution (shows in OpenRouter rankings).
            x_title: Optional app name for app attribution (shows in OpenRouter rankings).
        """
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.default_model = default_model
        self.timeout = timeout
        self.max_retries = max_retries
        self.http_referer = (
            http_referer or "https://github.com/patrykquantumnomad/financial-data-extractor"
        )
        self.x_title = x_title or "Financial Data Extractor"

    @retry(
        retry=retry_if_exception_type((httpx.HTTPError, httpx.TimeoutException)),
        wait=wait_exponential(multiplier=1, min=4, max=60),
        stop=stop_after_attempt(3),
    )
    async def create_completion(
        self,
        messages: list[dict[str, str]],
        model: str | None = None,
        temperature: float = 0.0,
        max_tokens: int = 8000,
        response_format: dict[str, Any] | None = None,
        user: str | None = None,
    ) -> dict[str, Any]:
        """Create a chat completion with retry logic.

        Follows OpenRouter API specification from https://openrouter.ai/docs/quickstart

        Args:
            messages: List of message dicts with 'role' and 'content'.
            model: Model to use (defaults to self.default_model).
            temperature: Sampling temperature (0.0 for deterministic).
            max_tokens: Maximum tokens in response.
            response_format: Optional response format (e.g., {"type": "json_object"}).
            user: Optional user identifier for tracking and analytics.

        Returns:
            Dictionary with 'content', 'usage', 'model', 'cost_usd', and 'elapsed_time' keys.

        Raises:
            httpx.HTTPError: If request fails after retries.
        """
        model = model or self.default_model
        start_time = time.time()

        url = f"{self.base_url}/chat/completions"

        # Build headers according to OpenRouter documentation
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": self.http_referer,  # For app attribution and rankings
            "X-Title": self.x_title,  # For app attribution and rankings
        }

        # Build request payload according to OpenRouter API spec
        # Enable usage accounting for accurate cost tracking
        payload: dict[str, Any] = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "usage": {
                "include": True,  # Enable usage accounting for accurate cost tracking
            },
        }

        if response_format:
            payload["response_format"] = response_format

        if user:
            payload["user"] = user

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.post(url, headers=headers, json=payload)
                response.raise_for_status()

                result = response.json()
                elapsed_time = time.time() - start_time

                # Extract usage and content
                usage = result.get("usage", {})
                choices = result.get("choices", [])
                content = choices[0].get("message", {}).get("content", "") if choices else ""
                actual_cost = usage.get("cost")

                if actual_cost is not None:
                    # Use actual cost from OpenRouter (in credits, treated as USD)
                    cost_usd = float(actual_cost)
                    logger.debug(
                        f"Using actual cost from OpenRouter usage accounting: ${cost_usd:.6f}",
                        extra={"model": model, "cost_source": "usage_accounting"},
                    )

                # Extract additional usage details from usage accounting
                prompt_tokens_details = usage.get("prompt_tokens_details", {})
                completion_tokens_details = usage.get("completion_tokens_details", {})
                cached_tokens = prompt_tokens_details.get("cached_tokens", 0)
                reasoning_tokens = completion_tokens_details.get("reasoning_tokens", 0)
                cost_details = usage.get("cost_details", {})

                logger.info(
                    "OpenRouter API call completed",
                    extra={
                        "model": model,
                        "prompt_tokens": usage.get("prompt_tokens", 0),
                        "completion_tokens": usage.get("completion_tokens", 0),
                        "total_tokens": usage.get("total_tokens", 0),
                        "cached_tokens": cached_tokens,  # From usage accounting
                        "reasoning_tokens": reasoning_tokens,  # For reasoning models
                        "cost_usd": cost_usd,
                        "cost_details": cost_details,
                        "cost_source": "usage_accounting"
                        if actual_cost is not None
                        else "estimate",
                        "elapsed_time": elapsed_time,
                    },
                )

                return {
                    "content": content,
                    "usage": usage,
                    "model": model,
                    "cost_usd": cost_usd,
                    "elapsed_time": elapsed_time,
                }

            except httpx.HTTPStatusError as e:
                status_code = e.response.status_code

                # Handle rate limiting (429) with longer backoff
                if status_code == 429:
                    logger.warning(
                        "Rate limit hit (429), waiting before retry",
                        extra={"model": model, "retry_after": 60},
                    )
                    await asyncio.sleep(60)
                    raise  # Re-raise to trigger retry decorator

                # Handle authentication errors (401)
                elif status_code == 401:
                    logger.error("OpenRouter authentication failed - check API key")
                    raise ValueError("Invalid OpenRouter API key") from e

                # Handle model not found or unavailable (404)
                elif status_code == 404:
                    logger.error(f"Model not found: {model}")
                    raise ValueError(f"Model not found or unavailable: {model}") from e

                # Handle other HTTP errors
                else:
                    error_text = e.response.text[:500] if e.response.text else "No error details"
                    logger.error(
                        f"OpenRouter API error: {status_code} - {error_text}",
                        extra={"model": model, "status_code": status_code},
                    )
                    raise

            except httpx.TimeoutException:
                logger.warning(
                    f"OpenRouter request timeout for model {model}",
                    extra={"model": model, "timeout": self.timeout},
                )
                raise

            except httpx.RequestError as e:
                logger.error(
                    f"OpenRouter request error: {e}",
                    extra={"model": model},
                    exc_info=True,
                )
                raise
