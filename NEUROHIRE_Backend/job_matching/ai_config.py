"""
Configuration for Google Generative AI services.
This file handles setup and configuration for the Google Generative AI models.
"""

import os
import logging
import google.generativeai as genai
from django.conf import settings

# Setup logger
logger = logging.getLogger(__name__)

# API key from environment variable or settings
GOOGLE_API_KEY = os.environ.get('GOOGLE_API_KEY', 'AIzaSyCb_eDymSFfFXurIN1o0RcUzW2TaYs-W4I')
MODEL_NAME = os.environ.get('GEMINI_MODEL', 'gemini-2.0-flash')

def initialize_genai():
    """Initialize the Google Generative AI API with the appropriate configuration."""
    try:
        # Configure the API
        genai.configure(api_key=GOOGLE_API_KEY)
        logger.info(f"Initialized Google Generative AI with model: {MODEL_NAME}")
        
        # Test the configuration by listing available models
        for model in genai.list_models():
            if 'generateContent' in model.supported_generation_methods:
                logger.debug(f"Available model: {model.name}")
        
        return True
    except Exception as e:
        logger.error(f"Failed to initialize Google Generative AI: {str(e)}")
        return False

# Run the initialization
is_genai_available = initialize_genai()
