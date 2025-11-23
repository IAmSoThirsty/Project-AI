"""Image generation using Hugging Face's free Stable Diffusion API.

This module provides text-to-image generation capabilities using the free
Hugging Face Inference API. No API key required for basic usage.
"""

import requests
import io
from typing import Optional
from PIL import Image


class ImageGenerator:
    """Generate images from text prompts using Stable Diffusion."""
    
    # Professional content filtering - blocked keywords
    NSFW_KEYWORDS = [
        'nsfw', 'nude', 'naked', 'explicit', 'adult', 'sexual',
        'porn', 'xxx', 'erotic', 'lewd', 'inappropriate',
        'seductive', 'provocative', 'intimate', 'mature content'
    ]
    
    # Automatic safety additions to negative prompts
    SAFETY_NEGATIVE = (
        "nsfw, nude, naked, explicit content, adult content, "
        "inappropriate, sexual, mature themes"
    )
    
    def __init__(self):
        """Initialize the image generator with Hugging Face API."""
        # Using free Stable Diffusion model from Hugging Face
        self.api_url = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-2-1"
        self.headers = {}
        
        # You can optionally add a Hugging Face token for faster/unlimited access
        # Get free token at: https://huggingface.co/settings/tokens
        # self.headers = {"Authorization": f"Bearer {HF_TOKEN}"}
    
    def _validate_prompt(self, prompt: str) -> tuple[bool, str]:
        """Validate prompt for inappropriate content.
        
        Args:
            prompt: The prompt to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        prompt_lower = prompt.lower()
        
        # Check for blocked keywords
        for keyword in self.NSFW_KEYWORDS:
            if keyword in prompt_lower:
                return False, (
                    f"Inappropriate content detected: '{keyword}'. "
                    "This application is for professional and creative use only."
                )
        
        return True, ""
    
    def generate_image(
        self,
        prompt: str,
        negative_prompt: str = "",
        timeout: int = 60
    ) -> Optional[Image.Image]:
        """Generate an image from a text prompt.
        
        Args:
            prompt: The text description of the image to generate
            negative_prompt: What to avoid in the image
            timeout: Request timeout in seconds
            
        Returns:
            PIL Image object or None if generation failed
        """
        if not prompt or not prompt.strip():
            raise ValueError("Prompt cannot be empty")
        
        # CONTENT FILTERING: Validate prompt for inappropriate content
        is_valid, error_msg = self._validate_prompt(prompt)
        if not is_valid:
            raise ValueError(error_msg)
        
        # SAFETY ENHANCEMENT: Always add safety terms to negative prompt
        if negative_prompt:
            negative_prompt = f"{negative_prompt}, {self.SAFETY_NEGATIVE}"
        else:
            negative_prompt = self.SAFETY_NEGATIVE
        
        # Build the payload
        payload = {
            "inputs": prompt,
        }
        
        if negative_prompt:
            payload["negative_prompt"] = negative_prompt
        
        try:
            # Make request to Hugging Face API
            response = requests.post(
                self.api_url,
                headers=self.headers,
                json=payload,
                timeout=timeout
            )
            
            if response.status_code == 200:
                # Convert response to PIL Image
                image = Image.open(io.BytesIO(response.content))
                return image
            elif response.status_code == 503:
                # Model is loading, this is common with free API
                raise RuntimeError(
                    "Model is loading, please wait 20-30 seconds and try again"
                )
            else:
                raise RuntimeError(
                    f"API request failed with status {response.status_code}: "
                    f"{response.text}"
                )
        
        except requests.exceptions.Timeout:
            raise RuntimeError("Request timed out. Please try again.")
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Network error: {str(e)}")
        except Exception as e:
            raise RuntimeError(f"Error generating image: {str(e)}")
    
    def generate_and_save(
        self,
        prompt: str,
        output_path: str,
        negative_prompt: str = ""
    ) -> bool:
        """Generate an image and save it to disk.
        
        Args:
            prompt: The text description of the image
            output_path: Where to save the image
            negative_prompt: What to avoid in the image
            
        Returns:
            True if successful, False otherwise
        """
        try:
            image = self.generate_image(prompt, negative_prompt)
            if image:
                image.save(output_path)
                return True
            return False
        except Exception as e:
            print(f"Error saving image: {e}")
            return False
    
    @staticmethod
    def get_style_presets() -> dict:
        """Get predefined style presets to enhance prompts.
        
        Returns:
            Dictionary of style names and their prompt modifiers
        """
        return {
            "Realistic": "photorealistic, highly detailed, 8k uhd, professional photography",
            "Artistic": "digital art, concept art, trending on artstation, highly detailed",
            "Anime": "anime style, manga, highly detailed, vibrant colors",
            "Oil Painting": "oil painting, classical art, renaissance style, masterpiece",
            "Watercolor": "watercolor painting, soft colors, artistic",
            "3D Render": "3d render, octane render, unreal engine, highly detailed",
            "Sketch": "pencil sketch, hand drawn, detailed line art",
            "Cyberpunk": "cyberpunk style, neon lights, futuristic, sci-fi",
            "Fantasy": "fantasy art, magical, epic, highly detailed",
            "Minimalist": "minimalist, clean, simple, modern"
        }
    
    @staticmethod
    def get_quality_modifiers() -> list:
        """Get quality enhancement keywords.
        
        Returns:
            List of quality modifier phrases
        """
        return [
            "highly detailed",
            "sharp focus",
            "professional",
            "8k resolution",
            "masterpiece",
            "best quality"
        ]
