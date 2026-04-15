"""
AI Orchestrator: Unified coordination layer for all AI provider calls.

Replaces scattered OpenAI/HuggingFace imports across 30+ files with
a single, governed, fallback-enabled orchestration layer.
"""

from __future__ import annotations

import logging
import os
from dataclasses import dataclass
from typing import Any, Literal

logger = logging.getLogger(__name__)

AIProvider = Literal["openai", "huggingface", "perplexity", "local"]


@dataclass
class AIRequest:
    """Request to AI orchestrator."""

    task_type: Literal["chat", "completion", "image", "embedding", "analysis"]
    prompt: str
    model: str | None = None
    provider: AIProvider | None = None  # None = auto-fallback
    config: dict[str, Any] | None = None
    context: dict[str, Any] | None = None


@dataclass
class AIResponse:
    """Response from AI orchestrator."""

    status: Literal["success", "error", "fallback"]
    result: Any
    provider_used: AIProvider
    metadata: dict[str, Any]
    error: str | None = None


def run_ai(request: AIRequest) -> AIResponse:
    """
    Execute AI request with provider fallback and governance.

    Fallback order:
        1. Specified provider (if request.provider set)
        2. OpenAI (default, most reliable)
        3. HuggingFace (fallback)
        4. Perplexity (web-enhanced fallback)
        5. Local models (offline fallback)

    Args:
        request: AI request with task type, prompt, optional provider

    Returns:
        AIResponse with result, provider used, metadata

    Raises:
        RuntimeError: If all providers fail
    """
    logger.info(
        f"AI orchestrator request: {request.task_type} via {request.provider or 'auto-fallback'}"
    )

    # If specific provider requested, try it only
    if request.provider:
        try:
            return _call_provider(request.provider, request)
        except Exception as e:
            logger.error(f"Requested provider {request.provider} failed: {e}")
            return AIResponse(
                status="error",
                result=None,
                provider_used=request.provider,
                metadata={"error_message": str(e)},
                error=str(e),
            )

    # Auto-fallback: Try providers in order
    providers: list[AIProvider] = ["openai", "huggingface", "perplexity", "local"]
    last_error = None

    for provider in providers:
        try:
            logger.info(f"Trying provider: {provider}")
            response = _call_provider(provider, request)
            if response.status == "success":
                return response
        except Exception as e:
            logger.warning(f"Provider {provider} failed: {e}")
            last_error = e
            continue

    # All providers failed
    raise RuntimeError(
        f"All AI providers failed. Last error: {last_error}"
    )


def _call_provider(provider: AIProvider, request: AIRequest) -> AIResponse:
    """Call specific AI provider with error handling."""
    if provider == "openai":
        return _call_openai(request)
    elif provider == "huggingface":
        return _call_huggingface(request)
    elif provider == "perplexity":
        return _call_perplexity(request)
    elif provider == "local":
        return _call_local(request)
    else:
        raise ValueError(f"Unknown provider: {provider}")


def _call_openai(request: AIRequest) -> AIResponse:
    """Call OpenAI API with proper error handling."""
    try:
        from openai import OpenAI

        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY not set")

        client = OpenAI(api_key=api_key)

        # Route by task type
        if (
            request.task_type == "chat"
            or request.task_type == "completion"
            or request.task_type == "analysis"
        ):
            model = request.model or "gpt-4"
            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": request.prompt}],
                **(request.config or {}),
            )
            result = response.choices[0].message.content

        elif request.task_type == "image":
            model = request.model or "dall-e-3"
            response = client.images.generate(
                model=model,
                prompt=request.prompt,
                **(request.config or {}),
            )
            result = response.data[0].url

        elif request.task_type == "embedding":
            model = request.model or "text-embedding-3-small"
            response = client.embeddings.create(
                model=model,
                input=request.prompt,
                **(request.config or {}),
            )
            result = response.data[0].embedding

        else:
            raise ValueError(f"Unsupported task type for OpenAI: {request.task_type}")

        return AIResponse(
            status="success",
            result=result,
            provider_used="openai",
            metadata={"model": model, "task_type": request.task_type},
        )

    except Exception as e:
        logger.error(f"OpenAI call failed: {e}")
        raise


def _call_huggingface(request: AIRequest) -> AIResponse:
    """Call HuggingFace API or local models with proper error handling."""
    config = request.config or {}
    use_local = config.get("use_local", False)

    if use_local:
        return _call_huggingface_local(request)
    else:
        return _call_huggingface_api(request)


def _call_huggingface_api(request: AIRequest) -> AIResponse:
    """Call HuggingFace Inference API."""
    try:
        import requests

        api_key = os.getenv("HUGGINGFACE_API_KEY")
        if not api_key:
            raise RuntimeError("HUGGINGFACE_API_KEY not set")

        # Route by task type
        if request.task_type == "image":
            model = request.model or "stabilityai/stable-diffusion-2-1"
            api_url = f"https://api-inference.huggingface.co/models/{model}"

            headers = {"Authorization": f"Bearer {api_key}"}
            response = requests.post(
                api_url,
                headers=headers,
                json={"inputs": request.prompt},
                timeout=60,
            )
            response.raise_for_status()
            result = response.content  # Binary image data

        elif (
            request.task_type == "chat"
            or request.task_type == "completion"
            or request.task_type == "analysis"
        ):
            model = request.model or "mistralai/Mistral-7B-Instruct-v0.2"
            api_url = f"https://api-inference.huggingface.co/models/{model}"

            headers = {"Authorization": f"Bearer {api_key}"}
            response = requests.post(
                api_url,
                headers=headers,
                json={"inputs": request.prompt},
                timeout=30,
            )
            response.raise_for_status()
            result = response.json()[0]["generated_text"]

        else:
            raise ValueError(
                f"Unsupported task type for HuggingFace: {request.task_type}"
            )

        return AIResponse(
            status="success",
            result=result,
            provider_used="huggingface",
            metadata={"model": model, "task_type": request.task_type},
        )

    except Exception as e:
        logger.error(f"HuggingFace API call failed: {e}")
        raise


def _call_huggingface_local(request: AIRequest) -> AIResponse:
    """Call HuggingFace models locally using transformers."""
    try:
        from transformers import AutoModelForCausalLM, AutoTokenizer

        config = request.config or {}
        model_name = request.model or "mistralai/Mistral-7B-Instruct-v0.2"

        # Extract generation parameters
        device = config.get("device", "cpu")
        max_new_tokens = config.get("max_new_tokens", 512)
        temperature = config.get("temperature", 0.7)
        top_p = config.get("top_p", 0.9)
        top_k = config.get("top_k", 50)
        do_sample = config.get("do_sample", True)
        use_cache = config.get("use_cache", True)

        logger.info(f"Loading local HuggingFace model: {model_name}")

        # Load tokenizer
        tokenizer = AutoTokenizer.from_pretrained(
            model_name,
            trust_remote_code=True,
        )

        # Load model with appropriate device settings
        if device == "cpu":
            model = AutoModelForCausalLM.from_pretrained(
                model_name,
                trust_remote_code=True,
                torch_dtype="auto",
            )
            model = model.to(device)
        else:
            model = AutoModelForCausalLM.from_pretrained(
                model_name,
                trust_remote_code=True,
                torch_dtype="auto",
                device_map="auto",
            )

        # Route by task type
        if request.task_type == "chat":
            # Handle chat messages
            messages = config.get("messages", [])
            if not messages and request.prompt:
                messages = [{"role": "user", "content": request.prompt}]

            # Apply chat template if available
            if hasattr(tokenizer, "apply_chat_template"):
                prompt = tokenizer.apply_chat_template(
                    messages,
                    tokenize=False,
                    add_generation_prompt=True,
                )
            else:
                # Fallback: simple concatenation
                prompt = "\n".join([f"{m['role']}: {m['content']}" for m in messages])
                prompt += "\nassistant:"
        else:
            # Use prompt as-is for completion
            prompt = request.prompt

        # Tokenize input
        inputs = tokenizer(prompt, return_tensors="pt").to(device)

        # Generate
        outputs = model.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            temperature=temperature,
            top_p=top_p,
            top_k=top_k,
            do_sample=do_sample,
            use_cache=use_cache,
            pad_token_id=tokenizer.eos_token_id,
        )

        # Decode output
        result = tokenizer.decode(outputs[0], skip_special_tokens=True)

        # Cleanup
        del model
        del tokenizer
        try:
            import torch
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
        except ImportError:
            pass

        return AIResponse(
            status="success",
            result=result,
            provider_used="huggingface",
            metadata={
                "model": model_name,
                "task_type": request.task_type,
                "device": device,
                "local": True,
            },
        )

    except ImportError as e:
        logger.error(f"Required library not installed: {e}")
        raise RuntimeError(
            f"Local HuggingFace inference requires transformers and torch: {e}"
        ) from e
    except Exception as e:
        logger.error(f"HuggingFace local inference failed: {e}")
        raise


def _call_perplexity(request: AIRequest) -> AIResponse:
    """Call Perplexity API (web-enhanced search + completion)."""
    # Placeholder - implement when Perplexity API is available
    raise NotImplementedError("Perplexity provider not yet implemented")


def _call_local(request: AIRequest) -> AIResponse:
    """Call local models (offline fallback)."""
    # Placeholder - implement with local model inference
    raise NotImplementedError("Local provider not yet implemented")
