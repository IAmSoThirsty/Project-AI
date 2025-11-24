"""
AI Image Generation Module with Professional Content Filtering
Uses Hugging Face Stable Diffusion API (free, no key required)
"""

from io import BytesIO
from typing import List, Optional

import requests  # type: ignore
from PIL import Image  # type: ignore


class ImageGenerator:
    """Professional AI image generator with content safety filtering."""
    
    BLOCKED_KEYWORDS = [
        "nude", "naked", "nsfw", "explicit", "porn", "sex", "xxx",
        "erotic", "adult", "inappropriate", "graphic", "vulgar",
        "offensive", "violent", "gore"
    ]
    
    STYLE_PRESETS = {
        "Photorealistic": "highly detailed, photorealistic, 8k uhd, professional photography",
        "Digital Art": "digital art, concept art, trending on artstation, highly detailed",
        "Oil Painting": "oil painting, classical art style, detailed brushstrokes, masterpiece",
        "Watercolor": "watercolor painting, soft colors, artistic, beautiful",
        "Anime": "anime style, manga art, vibrant colors, detailed",
        "Cyberpunk": "cyberpunk style, neon lights, futuristic, dystopian, sci-fi",
        "Fantasy": "fantasy art, magical, ethereal, enchanted, mystical",
        "Minimalist": "minimalist design, clean lines, simple, modern",
        "Abstract": "abstract art, geometric shapes, creative, artistic",
        "Cinematic": "cinematic lighting, dramatic, movie still, professional"
    }
    
    SAFETY_NEGATIVE_PROMPTS = [
        "nude", "naked", "nsfw", "explicit", "inappropriate",
        "violent", "gore", "offensive", "vulgar", "adult content"
    ]
    
    def __init__(self):
        self.api_url = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-2-1"
        self.content_filtering_enabled = True
    
    def _validate_prompt(self, prompt: str) -> bool:
        if not self.content_filtering_enabled:
            return True
        prompt_lower = prompt.lower()
        for keyword in self.BLOCKED_KEYWORDS:
            if keyword in prompt_lower:
                return False
        return True
    
    def generate_image(self, prompt: str, negative_prompt: str = "", style: Optional[str] = None, width: int = 512, height: int = 512) -> Optional[Image.Image]:
        if not prompt or not prompt.strip():
            raise ValueError("Prompt cannot be empty")
        if not self._validate_prompt(prompt):
            raise ValueError("Prompt contains inappropriate content")
        full_prompt = prompt
        if style and style in self.STYLE_PRESETS:
            full_prompt = f"{prompt}, {self.STYLE_PRESETS[style]}"
        full_negative = negative_prompt
        if full_negative:
            full_negative += ", " + ", ".join(self.SAFETY_NEGATIVE_PROMPTS)
        else:
            full_negative = ", ".join(self.SAFETY_NEGATIVE_PROMPTS)
        payload = {
            "inputs": full_prompt,
            "parameters": {
                "negative_prompt": full_negative,
                "width": width,
                "height": height,
                "num_inference_steps": 30
            }
        }
        try:
            response = requests.post(self.api_url, json=payload, timeout=60)
            if response.status_code == 200:
                image = Image.open(BytesIO(response.content))
                return image
            else:
                print(f"API Error: {response.status_code} - {response.text}")
                return None
        except Exception as e:
            print(f"Image generation error: {e}")
            return None
    
    def get_available_styles(self) -> List[str]:
        return list(self.STYLE_PRESETS.keys())
    
    def get_style_description(self, style: str) -> Optional[str]:
        return self.STYLE_PRESETS.get(style)
    
    def set_content_filtering(self, enabled: bool):
        self.content_filtering_enabled = enabled