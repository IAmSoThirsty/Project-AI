"""
AI Image Generation with Content Filtering and Style Presets.

Supports multiple backends:
- Stable Diffusion (Hugging Face API)
- DALL-E (OpenAI API)
- Local generation (optional)
"""

import logging
import os
import time
import random
from datetime import datetime
from enum import Enum
from typing import Any

import requests
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

# Read retry configuration from environment (fallbacks)
MAX_API_RETRIES = int(os.getenv("IMAGE_API_MAX_RETRIES", "3"))
BACKOFF_FACTOR = float(os.getenv("IMAGE_API_BACKOFF_FACTOR", "0.8"))


def _request_with_retries(method: str, url: str, **kwargs) -> requests.Response:
    """Perform an HTTP request with retries and exponential backoff for transient errors.

    Retries on status codes 429, 502, 503, 504 and on network errors.
    Uses requests.post/get when available so unit tests patching those functions are effective.
    Honors `Retry-After` header when present for 429 responses.
    """
    allowed_status_retry = {429, 502, 503, 504}
    attempt = 0
    method_lower = method.lower()
    # prefer direct method helper (post/get) to allow tests to patch them
    request_func = getattr(requests, method_lower, requests.request)
    while True:
        try:
            resp = request_func(url, timeout=kwargs.pop("timeout", 60), **kwargs)
            if resp.status_code in allowed_status_retry:
                attempt += 1
                # If Retry-After provided, honor it before counting as a retry backoff
                retry_after = None
                try:
                    retry_after = resp.headers.get("Retry-After")
                except Exception:
                    retry_after = None
                if retry_after:
                    try:
                        # Retry-After can be seconds or HTTP-date; handle seconds first
                        ra = int(retry_after)
                    except Exception:
                        # fallback: don't parse HTTP-date; use exponential backoff instead
                        ra = None
                    if ra is not None:
                        if attempt > MAX_API_RETRIES:
                            logger.error("Max retries reached for %s %s (status=%s)", method, url, resp.status_code)
                            resp.raise_for_status()
                            return resp
                        logger.warning("Received Retry-After=%s for %s %s - sleeping %ds (attempt %d)", retry_after, method, url, ra, attempt)
                        time.sleep(ra)
                        continue
                if attempt > MAX_API_RETRIES:
                    logger.error("Max retries reached for %s %s (status=%s)", method, url, resp.status_code)
                    resp.raise_for_status()
                    return resp
                backoff = BACKOFF_FACTOR * (2 ** (attempt - 1)) + random.random() * 0.1
                logger.warning("Transient status %s for %s %s - retrying in %.2fs (attempt %d)", resp.status_code, method, url, backoff, attempt)
                time.sleep(backoff)
                continue
            return resp
        except requests.RequestException as exc:
            attempt += 1
            if attempt > MAX_API_RETRIES:
                logger.exception("Request failed after %d attempts: %s %s", attempt, method, url)
                raise
            backoff = BACKOFF_FACTOR * (2 ** (attempt - 1)) + random.random() * 0.1
            logger.warning("Request exception for %s %s: %s - retrying in %.2fs (attempt %d)", method, url, exc, backoff, attempt)
            time.sleep(backoff)


class ImageStyle(Enum):
    """Professional image style presets."""

    PHOTOREALISTIC = "photorealistic"
    DIGITAL_ART = "digital_art"
    OIL_PAINTING = "oil_painting"
    WATERCOLOR = "watercolor"
    ANIME = "anime"
    CYBERPUNK = "cyberpunk"
    FANTASY = "fantasy"
    MINIMALIST = "minimalist"
    ABSTRACT = "abstract"
    CINEMATIC = "cinematic"


class ImageGenerationBackend(Enum):
    """Image generation backends."""

    HUGGINGFACE = "huggingface"
    OPENAI = "openai"
    LOCAL = "local"


class ImageGenerator:
    """AI Image Generator with content filtering and style presets."""

    # Content filtering keywords
    BLOCKED_KEYWORDS = [
        "nsfw",
        "explicit",
        "nude",
        "violence",
        "gore",
        "hate",
        "illegal",
        "drug",
        "weapon",
        "harm",
        "abuse",
        "discrimin",
        "racist",
        "sexist",
        "child",
    ]

    # Style preset prompts
    STYLE_PRESETS = {
        ImageStyle.PHOTOREALISTIC: "ultra realistic, 8k, professional photography, detailed",
        ImageStyle.DIGITAL_ART: "digital art, highly detailed, vibrant colors, artstation",
        ImageStyle.OIL_PAINTING: "oil painting, classical art style, brush strokes, masterpiece",
        ImageStyle.WATERCOLOR: "watercolor painting, soft colors, artistic, delicate",
        ImageStyle.ANIME: "anime style, manga, detailed characters, vibrant",
        ImageStyle.CYBERPUNK: "cyberpunk, neon lights, futuristic, dystopian, sci-fi",
        ImageStyle.FANTASY: "fantasy art, magical, epic, detailed world building",
        ImageStyle.MINIMALIST: "minimalist, clean, simple, modern design",
        ImageStyle.ABSTRACT: "abstract art, creative, unique perspective, artistic",
        ImageStyle.CINEMATIC: "cinematic, dramatic lighting, movie poster style, epic",
    }

    # Safety negative prompts (always added)
    SAFETY_NEGATIVE = (
        "nsfw, explicit, nude, violence, gore, disturbing, "
        "inappropriate, offensive, hate, illegal"
    )

    def __init__(
        self,
        backend: ImageGenerationBackend = ImageGenerationBackend.HUGGINGFACE,
        data_dir: str = "data",
    ):
        """Initialize image generator."""
        self.backend = backend
        self.data_dir = data_dir
        self.output_dir = os.path.join(data_dir, "generated_images")
        os.makedirs(self.output_dir, exist_ok=True)

        # API keys
        self.hf_api_key = os.getenv("HUGGINGFACE_API_KEY")
        self.openai_api_key = os.getenv("OPENAI_API_KEY")

        # Configuration
        self.content_filter_enabled = True
        self.default_width = 512
        self.default_height = 512

    def check_content_filter(self, prompt: str) -> tuple[bool, str]:
        """Check if prompt passes content filter."""
        if not self.content_filter_enabled:
            return True, "Content filter disabled"

        prompt_lower = prompt.lower()
        for keyword in self.BLOCKED_KEYWORDS:
            if keyword in prompt_lower:
                return False, f"Blocked keyword detected: {keyword}"

        return True, "Content filter passed"

    def build_enhanced_prompt(
        self, prompt: str, style: ImageStyle = ImageStyle.PHOTOREALISTIC
    ) -> str:
        """Build enhanced prompt with style preset."""
        style_suffix = self.STYLE_PRESETS[style]
        return f"{prompt}, {style_suffix}"

    def generate_with_huggingface(
        self,
        prompt: str,
        negative_prompt: str = "",
        width: int = 512,
        height: int = 512,
    ) -> dict[str, Any]:
        """Generate image using Hugging Face Stable Diffusion API."""
        if not self.hf_api_key:
            return {
                "success": False,
                "error": "Hugging Face API key not configured",
            }

        api_url = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-2-1"
        headers = {"Authorization": f"Bearer {self.hf_api_key}"}

        payload = {
            "inputs": prompt,
            "parameters": {
                "negative_prompt": negative_prompt,
                "width": width,
                "height": height,
                "num_inference_steps": 50,
                "guidance_scale": 7.5,
            },
        }

        try:
            response = _request_with_retries("POST", api_url, headers=headers, json=payload, timeout=60)
            response.raise_for_status()

            # Save image
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"sd_{timestamp}.png"
            filepath = os.path.join(self.output_dir, filename)

            with open(filepath, "wb") as f:
                f.write(response.content)

            return {
                "success": True,
                "filepath": filepath,
                "filename": filename,
                "prompt": prompt,
                "timestamp": timestamp,
            }

        except Exception as e:
            logger.error(f"Hugging Face generation error: {e}")
            return {"success": False, "error": str(e)}

    def generate_with_openai(
        self,
        prompt: str,
        size: str = "512x512",
    ) -> dict[str, Any]:
        """Generate image using OpenAI DALL-E API."""
        if not self.openai_api_key:
            return {
                "success": False,
                "error": "OpenAI API key not configured",
            }

        try:
            from typing import cast

            import openai

            openai.api_key = self.openai_api_key

            # Validate size parameter
            valid_sizes = ["256x256", "512x512", "1024x1024", "1024x1792", "1792x1024"]
            if size not in valid_sizes:
                size = "1024x1024"  # Default to DALL-E 3 standard size

            attempt = 0
            while True:
                try:
                    response = openai.images.generate(
                        model="dall-e-3",
                        prompt=prompt,
                        size=cast(Any, size),  # Type cast for OpenAI API
                        quality="standard",
                        n=1,
                    )
                    break
                except Exception as exc:
                    attempt += 1
                    if attempt > MAX_API_RETRIES:
                        logger.exception("OpenAI generate failed after %d attempts", attempt)
                        raise
                    backoff = BACKOFF_FACTOR * (2 ** (attempt - 1)) + random.random() * 0.1
                    logger.warning("OpenAI transient error: %s - retrying in %.2fs (attempt %d)", exc, backoff, attempt)
                    time.sleep(backoff)

            # Validate response
            if not getattr(response, "data", None) or len(response.data) == 0:
                raise ValueError("No image data received from OpenAI")

            image_url = response.data[0].url
            if not image_url:
                raise ValueError("No image URL in response")

            # Download and save (with retries)
            img_resp = _request_with_retries("GET", str(image_url), timeout=30)
            img_resp.raise_for_status()

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"dalle_{timestamp}.png"
            filepath = os.path.join(self.output_dir, filename)

            with open(filepath, "wb") as f:
                f.write(img_resp.content)

            return {
                "success": True,
                "filepath": filepath,
                "filename": filename,
                "prompt": prompt,
                "timestamp": timestamp,
                "url": image_url,
            }

        except Exception as e:
            logger.error(f"OpenAI generation error: {e}")
            return {"success": False, "error": str(e)}

    def generate(
        self,
        prompt: str,
        style: ImageStyle = ImageStyle.PHOTOREALISTIC,
        width: int = 512,
        height: int = 512,
    ) -> dict[str, Any]:
        """
        Generate image with content filtering and style presets.

        Args:
            prompt: User's text prompt
            style: Image style preset
            width: Image width (for SD)
            height: Image height (for SD)

        Returns:
            Dictionary with success status, filepath, and metadata
        """
        # Validate prompt
        if not prompt or not prompt.strip():
            return {"success": False, "error": "Empty prompt"}

        # Content filter check
        is_safe, filter_msg = self.check_content_filter(prompt)
        if not is_safe:
            logger.warning(f"Content filter blocked: {prompt}")
            return {"success": False, "error": filter_msg, "filtered": True}

        # Build enhanced prompt
        enhanced_prompt = self.build_enhanced_prompt(prompt, style)
        negative_prompt = self.SAFETY_NEGATIVE

        # Generate based on backend
        if self.backend == ImageGenerationBackend.HUGGINGFACE:
            return self.generate_with_huggingface(
                enhanced_prompt, negative_prompt, width, height
            )
        elif self.backend == ImageGenerationBackend.OPENAI:
            return self.generate_with_openai(enhanced_prompt, f"{width}x{height}")
        else:
            return {"success": False, "error": "Backend not implemented"}

    def get_generation_history(self, limit: int = 10) -> list[dict[str, Any]]:
        """Get recent generation history."""
        history = []
        try:
            files = sorted(
                os.listdir(self.output_dir),
                key=lambda f: os.path.getmtime(os.path.join(self.output_dir, f)),
                reverse=True,
            )[:limit]

            for filename in files:
                filepath = os.path.join(self.output_dir, filename)
                history.append(
                    {
                        "filename": filename,
                        "filepath": filepath,
                        "timestamp": os.path.getmtime(filepath),
                    }
                )
        except Exception as e:
            logger.error(f"Error reading history: {e}")

        return history

    def disable_content_filter(self, override_password: str) -> bool:
        """Disable content filter (requires override password)."""
        # This should integrate with CommandOverrideSystem
        # For now, simple implementation
        if override_password == os.getenv("MASTER_PASSWORD"):
            self.content_filter_enabled = False
            logger.warning("Content filter DISABLED via override")
            return True
        return False

    def enable_content_filter(self) -> None:
        """Re-enable content filter."""
        self.content_filter_enabled = True
        logger.info("Content filter ENABLED")

    def get_statistics(self) -> dict[str, Any]:
        """Get generation statistics."""
        try:
            total_images = len(os.listdir(self.output_dir))
        except Exception:
            total_images = 0

        return {
            "total_generated": total_images,
            "backend": self.backend.value,
            "content_filter_enabled": self.content_filter_enabled,
            "available_styles": len(self.STYLE_PRESETS),
            "output_directory": self.output_dir,
        }
