"""LLM client wrapper for easy model switching via environment variables"""
from typing import Optional, Dict, Any, List
import google.generativeai as genai
from .config import Config


class LLMClient:
    """Unified LLM client that wraps Google Gemini
    
    Designed for easy model switching via environment variables.
    All LLM calls in the application should use this wrapper.
    """
    
    def __init__(self, config: Config):
        """Initialize LLM client
        
        Args:
            config: Application configuration
        """
        self.config = config
        self.model_name = config.gemini_model
        
        # Configure Gemini
        genai.configure(api_key=config.gemini_api_key)
        self.model = genai.GenerativeModel(self.model_name)
        
        # Track usage for cost monitoring
        self.total_input_tokens = 0
        self.total_output_tokens = 0
    
    def generate(
        self,
        prompt: str,
        max_tokens: int = 1000,
        temperature: float = 0.7,
        system_instruction: Optional[str] = None
    ) -> str:
        """Generate text completion
        
        Args:
            prompt: Input prompt
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature (0.0 to 1.0)
            system_instruction: Optional system instruction
        
        Returns:
            Generated text
        """
        try:
            generation_config = genai.GenerationConfig(
                max_output_tokens=max_tokens,
                temperature=temperature,
            )
            
            # Add system instruction if provided
            if system_instruction:
                model = genai.GenerativeModel(
                    self.model_name,
                    system_instruction=system_instruction
                )
            else:
                model = self.model
            
            response = model.generate_content(
                prompt,
                generation_config=generation_config
            )
            
            # Track token usage
            if hasattr(response, 'usage_metadata'):
                self.total_input_tokens += response.usage_metadata.prompt_token_count
                self.total_output_tokens += response.usage_metadata.candidates_token_count
            
            return response.text
            
        except Exception as e:
            print(f"Error generating content: {e}")
            raise
    
    def generate_json(
        self,
        prompt: str,
        max_tokens: int = 1000,
        temperature: float = 0.7,
        system_instruction: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate JSON response
        
        Args:
            prompt: Input prompt (should request JSON output)
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            system_instruction: Optional system instruction
        
        Returns:
            Parsed JSON response
        """
        import json
        
        # Add JSON instruction to prompt
        json_prompt = f"{prompt}\n\nRespond ONLY with valid JSON. No other text."
        
        response_text = self.generate(
            json_prompt,
            max_tokens=max_tokens,
            temperature=temperature,
            system_instruction=system_instruction
        )
        
        # Parse JSON from response
        # Handle markdown code blocks if present
        response_text = response_text.strip()
        if response_text.startswith('```json'):
            response_text = response_text[7:]
        if response_text.startswith('```'):
            response_text = response_text[3:]
        if response_text.endswith('```'):
            response_text = response_text[:-3]
        
        try:
            return json.loads(response_text.strip())
        except json.JSONDecodeError as e:
            print(f"Failed to parse JSON response: {e}")
            print(f"Response text: {response_text}")
            raise
    
    def get_usage_stats(self) -> Dict[str, Any]:
        """Get token usage statistics
        
        Returns:
            Dictionary with usage stats and cost estimate
        """
        # Gemini Flash 2.0 pricing (as of late 2024)
        # Input: $0.075 per 1M tokens
        # Output: $0.30 per 1M tokens
        
        input_cost = (self.total_input_tokens / 1_000_000) * 0.075
        output_cost = (self.total_output_tokens / 1_000_000) * 0.30
        total_cost = input_cost + output_cost
        
        return {
            'model': self.model_name,
            'input_tokens': self.total_input_tokens,
            'output_tokens': self.total_output_tokens,
            'total_tokens': self.total_input_tokens + self.total_output_tokens,
            'input_cost_usd': round(input_cost, 6),
            'output_cost_usd': round(output_cost, 6),
            'total_cost_usd': round(total_cost, 6)
        }
    
    def reset_usage_stats(self) -> None:
        """Reset token usage counters"""
        self.total_input_tokens = 0
        self.total_output_tokens = 0
    
    def count_tokens(self, text: str) -> int:
        """Count tokens in text
        
        Args:
            text: Input text
        
        Returns:
            Approximate token count
        """
        try:
            result = self.model.count_tokens(text)
            return result.total_tokens
        except Exception:
            # Fallback: rough estimate (4 chars per token)
            return len(text) // 4


def create_llm_client(config: Optional[Config] = None) -> LLMClient:
    """Factory function to create LLM client
    
    Args:
        config: Optional configuration (loads from env if not provided)
    
    Returns:
        Configured LLM client
    """
    from .config import load_config
    
    if config is None:
        config = load_config()
    
    return LLMClient(config)

