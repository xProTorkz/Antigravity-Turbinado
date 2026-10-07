"""Cloud-First AI Provider Abstraction and Workload Router for Antigravity Control Plane.

Invariants:
- Mac M1 is a lightweight orchestrator/client, NOT an LLM farm.
- Heavy reasoning, planning, summarization, and content generation are cloud-first.
- Standardized, extensible interface across OpenAI, OpenRouter, and future cloud providers.
- Local LLM on port 8088 is strictly a legacy fallback, not required for reasoning or summarization.
- Zero secrets in logs, exceptions, or git.
"""
from __future__ import annotations

import getpass
import json
import logging
import os
import re
import subprocess
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

import httpx

logger = logging.getLogger("ag-llm-provider")

OPENAI_KEYCHAIN_SERVICE = "jarvis-openai-api-key"
OPENROUTER_KEYCHAIN_SERVICE = "jarvis-openrouter-api-key"

FORBIDDEN_SECRET_REGEXES = [
    (re.compile(r"(sk-or-v1-[a-zA-Z0-9]{64})", re.IGNORECASE), "[REDACTED_OPENROUTER_KEY]"),
    (re.compile(r"(sk-[a-zA-Z0-9]{20,})", re.IGNORECASE), "[REDACTED_OPENAI_KEY]"),
    (re.compile(r"(bearer\s+)([a-zA-Z0-9_\-\.]{20,})", re.IGNORECASE), r"\1[REDACTED_TOKEN]"),
]


def sanitize_log_message(msg: str) -> str:
    """Sanitizes sensitive tokens and keys from error messages and logs."""
    if not msg:
        return ""
    result = str(msg)
    for pattern, replacement in FORBIDDEN_SECRET_REGEXES:
        result = pattern.sub(replacement, result)
    return result


def get_openrouter_api_key() -> Optional[str]:
    """Retrieves OpenRouter API Key from environment or macOS Keychain.

    Resolution order:
    1. OPENROUTER_API_KEY environment variable
    2. macOS Keychain generic password named jarvis-openrouter-api-key
    """
    key = os.environ.get("OPENROUTER_API_KEY", "").strip()
    if key:
        return key

    try:
        res = subprocess.run(
            [
                "security",
                "find-generic-password",
                "-a",
                getpass.getuser(),
                "-s",
                OPENROUTER_KEYCHAIN_SERVICE,
                "-w",
            ],
            capture_output=True,
            text=True,
            timeout=3,
            check=False,
        )
        if res.returncode == 0:
            val = res.stdout.strip()
            if val:
                return val
    except Exception:
        pass
    return None


def get_openai_api_key() -> Optional[str]:
    """Retrieves OpenAI API Key from environment or macOS Keychain."""
    key = os.environ.get("OPENAI_API_KEY", "").strip()
    if key:
        return key

    try:
        res = subprocess.run(
            [
                "security",
                "find-generic-password",
                "-a",
                getpass.getuser(),
                "-s",
                OPENAI_KEYCHAIN_SERVICE,
                "-w",
            ],
            capture_output=True,
            text=True,
            timeout=3,
            check=False,
        )
        if res.returncode == 0:
            val = res.stdout.strip()
            if val:
                return val
    except Exception:
        pass
    return None


class AIProviderError(Exception):
    """Base exception for AI provider errors, sanitized against secret leakage."""

    def __init__(self, message: str, provider: str = ""):
        sanitized = sanitize_log_message(message)
        super().__init__(sanitized)
        self.provider = provider
        self.raw_message = sanitized


class AIProviderAuthError(AIProviderError):
    """Authentication or missing API key error."""
    pass


class AIProviderUnavailableError(AIProviderError):
    """Provider offline, rate limited or unreachable."""
    pass


class AIProviderTimeoutError(AIProviderError):
    """Provider call timed out."""
    pass


@dataclass
class LLMResponse:
    content: str
    provider: str
    model: str
    latency_sec: float
    usage: Dict[str, Any] = field(default_factory=dict)
    raw_response: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "content": self.content,
            "provider": self.provider,
            "model": self.model,
            "latency_sec": round(self.latency_sec, 3),
            "usage": self.usage,
        }


class BaseAIProvider(ABC):
    """Abstract contract for all cloud and local AI completion providers."""

    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    def is_configured(self) -> bool:
        """Returns True if required credentials or endpoints are configured."""
        pass

    @abstractmethod
    def is_healthy(self) -> bool:
        """Returns True if the provider endpoint is reachable."""
        pass

    @abstractmethod
    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 0.2,
        max_tokens: int = 1000,
        timeout_sec: float = 30.0,
        **kwargs: Any,
    ) -> LLMResponse:
        """Executes chat completion returning structured LLMResponse."""
        pass


class OpenAIProvider(BaseAIProvider):
    """Cloud provider adapter for OpenAI models."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        default_model: str = "gpt-5.6-sol",
        base_url: str = "https://api.openai.com/v1",
    ):
        super().__init__("openai")
        self._api_key = api_key
        self.default_model = default_model
        self.base_url = base_url.rstrip("/")

    @property
    def api_key(self) -> Optional[str]:
        if self._api_key is not None:
            return self._api_key or None
        return get_openai_api_key()

    def is_configured(self) -> bool:
        return bool(self.api_key)

    def is_healthy(self) -> bool:
        return self.is_configured()

    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 0.2,
        max_tokens: int = 1000,
        timeout_sec: float = 30.0,
        **kwargs: Any,
    ) -> LLMResponse:
        key = self.api_key
        if not key:
            raise AIProviderAuthError("OPENAI_API_KEY_REQUIRED", provider=self.name)

        chosen_model = model or self.default_model
        headers = {
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
        }
        payload: Dict[str, Any] = {
            "model": chosen_model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        if "response_format" in kwargs:
            payload["response_format"] = kwargs["response_format"]

        start_time = time.time()
        try:
            with httpx.Client(timeout=timeout_sec) as client:
                res = client.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=payload,
                )
                latency = time.time() - start_time
                if res.status_code in (401, 403):
                    raise AIProviderAuthError(
                        f"OpenAI authentication failed: HTTP {res.status_code}",
                        provider=self.name,
                    )
                if res.status_code == 429:
                    raise AIProviderUnavailableError(
                        "OpenAI rate limit exceeded (HTTP 429)", provider=self.name
                    )
                res.raise_for_status()
                data = res.json()
                content = (
                    data.get("choices", [{}])[0]
                    .get("message", {})
                    .get("content", "")
                )
                usage = data.get("usage", {})
                return LLMResponse(
                    content=content,
                    provider=self.name,
                    model=chosen_model,
                    latency_sec=latency,
                    usage=usage,
                    raw_response=data,
                )
        except httpx.TimeoutException as exc:
            raise AIProviderTimeoutError(
                f"OpenAI request timed out after {timeout_sec}s: {exc}",
                provider=self.name,
            ) from exc
        except (AIProviderAuthError, AIProviderUnavailableError):
            raise
        except Exception as exc:
            raise AIProviderError(
                f"OpenAI request failed: {sanitize_log_message(str(exc))}",
                provider=self.name,
            ) from exc


class OpenRouterProvider(BaseAIProvider):
    """Cloud provider adapter for OpenRouter API (Inference Aggregator)."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        default_model: str = "anthropic/claude-3.7-sonnet",
        base_url: str = "https://openrouter.ai/api/v1",
        site_url: str = "https://github.com/xProTorkz/antigravity-control-plane",
        site_name: str = "Jarvis Control Plane",
    ):
        super().__init__("openrouter")
        self._api_key = api_key
        self.default_model = default_model
        self.base_url = base_url.rstrip("/")
        self.site_url = site_url
        self.site_name = site_name

    @property
    def api_key(self) -> Optional[str]:
        if self._api_key is not None:
            return self._api_key or None
        return get_openrouter_api_key()

    def is_configured(self) -> bool:
        return bool(self.api_key)

    def is_healthy(self) -> bool:
        return self.is_configured()

    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 0.2,
        max_tokens: int = 1000,
        timeout_sec: float = 30.0,
        **kwargs: Any,
    ) -> LLMResponse:
        key = self.api_key
        if not key:
            raise AIProviderAuthError("OPENROUTER_API_KEY_REQUIRED", provider=self.name)

        chosen_model = model or self.default_model
        headers = {
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
            "HTTP-Referer": self.site_url,
            "X-Title": self.site_name,
        }
        payload: Dict[str, Any] = {
            "model": chosen_model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        if "response_format" in kwargs:
            payload["response_format"] = kwargs["response_format"]

        start_time = time.time()
        try:
            with httpx.Client(timeout=timeout_sec) as client:
                res = client.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=payload,
                )
                latency = time.time() - start_time
                if res.status_code in (401, 403):
                    raise AIProviderAuthError(
                        f"OpenRouter authentication failed: HTTP {res.status_code}",
                        provider=self.name,
                    )
                if res.status_code == 429:
                    raise AIProviderUnavailableError(
                        "OpenRouter rate limit or credit ceiling reached (HTTP 429)",
                        provider=self.name,
                    )
                res.raise_for_status()
                data = res.json()
                content = (
                    data.get("choices", [{}])[0]
                    .get("message", {})
                    .get("content", "")
                )
                usage = data.get("usage", {})
                return LLMResponse(
                    content=content,
                    provider=self.name,
                    model=chosen_model,
                    latency_sec=latency,
                    usage=usage,
                    raw_response=data,
                )
        except httpx.TimeoutException as exc:
            raise AIProviderTimeoutError(
                f"OpenRouter request timed out after {timeout_sec}s: {exc}",
                provider=self.name,
            ) from exc
        except (AIProviderAuthError, AIProviderUnavailableError):
            raise
        except Exception as exc:
            raise AIProviderError(
                f"OpenRouter request failed: {sanitize_log_message(str(exc))}",
                provider=self.name,
            ) from exc


class LocalLLMProvider(BaseAIProvider):
    """Local inference adapter (Legacy Fallback Only via llama-server port 8088)."""

    def __init__(
        self,
        base_url: str = "http://127.0.0.1:8088/v1",
        default_model: str = "qwen2.5-0.5b-instruct-q4_k_m.gguf",
    ):
        super().__init__("local")
        self.base_url = base_url.rstrip("/")
        self.default_model = default_model

    def is_configured(self) -> bool:
        return True

    def is_healthy(self) -> bool:
        try:
            with httpx.Client(timeout=1.0) as client:
                res = client.get(f"{self.base_url}/models")
                return res.status_code == 200
        except Exception:
            return False

    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 0.2,
        max_tokens: int = 500,
        timeout_sec: float = 5.0,
        **kwargs: Any,
    ) -> LLMResponse:
        chosen_model = model or self.default_model
        payload = {
            "model": chosen_model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        start_time = time.time()
        try:
            with httpx.Client(timeout=timeout_sec) as client:
                res = client.post(
                    f"{self.base_url}/chat/completions",
                    headers={"Content-Type": "application/json"},
                    json=payload,
                )
                latency = time.time() - start_time
                res.raise_for_status()
                data = res.json()
                content = (
                    data.get("choices", [{}])[0]
                    .get("message", {})
                    .get("content", "")
                )
                usage = data.get("usage", {})
                return LLMResponse(
                    content=content,
                    provider=self.name,
                    model=chosen_model,
                    latency_sec=latency,
                    usage=usage,
                    raw_response=data,
                )
        except Exception as exc:
            raise AIProviderUnavailableError(
                f"Local LLM (8088) unavailable: {sanitize_log_message(str(exc))}",
                provider=self.name,
            ) from exc


class AIProviderRegistry:
    """Registry managing available cloud and local AI providers."""

    def __init__(self) -> None:
        self._providers: Dict[str, BaseAIProvider] = {}

    def register(self, provider: BaseAIProvider) -> None:
        self._providers[provider.name.lower()] = provider

    def get(self, name: str) -> Optional[BaseAIProvider]:
        return self._providers.get(name.lower())

    def list_providers(self) -> List[str]:
        return sorted(list(self._providers.keys()))

    def get_health_status(self) -> Dict[str, Any]:
        """Returns sanitized status of registered providers without credentials."""
        status: Dict[str, Any] = {}
        for name, provider in self._providers.items():
            status[f"{name}_configured"] = provider.is_configured()
            if name == "local":
                status["local_llm_8088"] = provider.is_healthy()
        return status

    @classmethod
    def default_registry(cls) -> AIProviderRegistry:
        reg = cls()
        reg.register(OpenAIProvider())
        reg.register(OpenRouterProvider())
        reg.register(LocalLLMProvider())
        return reg


@dataclass
class WorkloadRouteItem:
    provider: str
    model: Optional[str] = None


class WorkloadRouter:
    """Deterministic workload router selecting the appropriate cloud AI provider.

    Workloads are mapped to priority chains. If the top provider lacks credentials
    or is unavailable, the router automatically fails over to the next allowed provider.
    """

    DEFAULT_POLICIES: Dict[str, List[WorkloadRouteItem]] = {
        "engineering": [
            WorkloadRouteItem("openai", "gpt-5.6-sol"),
            WorkloadRouteItem("openrouter", "anthropic/claude-3.7-sonnet"),
        ],
        "reasoning": [
            WorkloadRouteItem("openai", "gpt-5.6-sol"),
            WorkloadRouteItem("openrouter", "deepseek/deepseek-r1"),
        ],
        "research": [
            WorkloadRouteItem("openrouter", "perplexity/sonar-reasoning"),
            WorkloadRouteItem("openai", "gpt-4o"),
        ],
        "summarization": [
            WorkloadRouteItem("openrouter", "meta-llama/llama-3.3-70b-instruct"),
            WorkloadRouteItem("openai", "gpt-4o-mini"),
        ],
        "copywriting": [
            WorkloadRouteItem("openrouter", "anthropic/claude-3.7-sonnet"),
            WorkloadRouteItem("openai", "gpt-4o"),
        ],
        "creative": [
            WorkloadRouteItem("openrouter", "meta-llama/llama-3.3-70b-instruct"),
            WorkloadRouteItem("openai", "gpt-4o"),
        ],
        "uncensored_creative": [
            WorkloadRouteItem("openrouter", "meta-llama/llama-3.3-70b-instruct"),
        ],
        "fast": [
            WorkloadRouteItem("openrouter", "meta-llama/llama-3.3-70b-instruct"),
            WorkloadRouteItem("openai", "gpt-4o-mini"),
        ],
        "cheap": [
            WorkloadRouteItem("openrouter", "deepseek/deepseek-chat"),
            WorkloadRouteItem("openai", "gpt-4o-mini"),
        ],
        "long_context": [
            WorkloadRouteItem("openrouter", "google/gemini-2.0-flash-001"),
            WorkloadRouteItem("openai", "gpt-4o"),
        ],
        "privacy_sensitive": [
            WorkloadRouteItem("local", None),
        ],
    }

    def __init__(
        self,
        registry: Optional[AIProviderRegistry] = None,
        policies: Optional[Dict[str, List[WorkloadRouteItem]]] = None,
    ):
        self.registry = registry or AIProviderRegistry.default_registry()
        self.policies = policies or dict(self.DEFAULT_POLICIES)

    def resolve_chain(
        self,
        workload: str,
        provider_override: Optional[str] = None,
        model_override: Optional[str] = None,
    ) -> List[WorkloadRouteItem]:
        """Resolves ordered list of (provider, model) candidates."""
        if provider_override:
            return [WorkloadRouteItem(provider=provider_override, model=model_override)]

        normalized_workload = workload.strip().lower() if workload else "engineering"
        chain = self.policies.get(normalized_workload)
        if not chain:
            chain = self.policies.get("engineering", [WorkloadRouteItem("openai", None)])

        if model_override:
            # Apply model override to the primary candidate
            return [WorkloadRouteItem(chain[0].provider, model=model_override)] + chain[1:]

        return list(chain)

    def route_and_execute(
        self,
        workload: str,
        messages: List[Dict[str, str]],
        provider_override: Optional[str] = None,
        model_override: Optional[str] = None,
        temperature: float = 0.2,
        max_tokens: int = 1000,
        timeout_sec: float = 30.0,
        **kwargs: Any,
    ) -> LLMResponse:
        """Selects suitable provider and executes completion with graceful fallback."""
        chain = self.resolve_chain(
            workload=workload,
            provider_override=provider_override,
            model_override=model_override,
        )

        attempt_errors: List[str] = []
        for item in chain:
            provider = self.registry.get(item.provider)
            if not provider:
                attempt_errors.append(f"Provider '{item.provider}' not registered")
                continue

            if not provider.is_configured():
                attempt_errors.append(f"Provider '{item.provider}' has no configured credentials")
                continue

            try:
                logger.info(
                    "Executing workload '%s' via provider '%s' (model=%s)",
                    workload,
                    item.provider,
                    item.model or "default",
                )
                return provider.chat_completion(
                    messages=messages,
                    model=item.model,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    timeout_sec=timeout_sec,
                    **kwargs,
                )
            except Exception as exc:
                sanitized_err = sanitize_log_message(str(exc))
                logger.warning(
                    "Provider '%s' failed for workload '%s': %s. Trying next candidate...",
                    item.provider,
                    workload,
                    sanitized_err,
                )
                attempt_errors.append(f"{item.provider}: {sanitized_err}")

        err_summary = "; ".join(attempt_errors) if attempt_errors else "No viable provider available"
        raise AIProviderUnavailableError(
            f"All providers in fallback chain exhausted for workload '{workload}': {err_summary}",
            provider="workload_router",
        )
