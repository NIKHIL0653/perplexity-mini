#!/usr/bin/env python3
"""
OpenRouter API Integration for AI Research Assistant

This module is like the brain of our research assistant - it takes all the
information we've gathered from web searches and uses advanced AI to synthesize
it into clear, comprehensive answers that actually make sense.

We're using OpenRouter, which gives us access to cutting-edge models like
DeepSeek V3 without having to manage our own AI infrastructure. It's like
having a world-class research assistant that can read through dozens of
sources and give you the key insights in seconds.

Features:
- Integration with DeepSeek V3 via OpenRouter
- Intelligent synthesis of multiple sources
- Proper citation handling
- Error handling and fallbacks
- Optimized prompts for research tasks
"""
import requests
import os
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

@dataclass
class ChatMessage:
    """
    Represents a single message in our conversation with the AI.
    
    Think of this as one part of a conversation - it could be us asking
    a question (user role), the AI responding (assistant role), or us
    giving the AI instructions about how to behave (system role).
    
    This structure helps the AI understand the context and respond
    appropriately to our research requests.
    """
    role: str     # 'system' (instructions), 'user' (our question), or 'assistant' (AI response)
    content: str  # The actual text of the message

@dataclass
class ChatResponse:
    """
    The AI's response to our research query.
    
    When we send our search results and question to the AI, this is what
    we get back - a thoughtful analysis with optional usage statistics
    so we can track how much AI processing we're using.
    """
    content: str                           # The AI's synthesized answer
    usage: Optional[Dict[str, int]] = None # Token usage stats (input/output tokens)

class OpenRouterClient:
    """
    Our gateway to advanced AI models through OpenRouter.
    
    This class handles all the technical details of communicating with
    AI models, so the rest of our app can just focus on asking good
    questions and presenting great answers to users.
    
    OpenRouter is fantastic because it gives us access to the latest
    and greatest AI models without having to worry about infrastructure,
    scaling, or keeping up with the rapidly evolving AI landscape.
    """
    
    def __init__(self, api_key: str):
        """
        Set up our connection to the AI service.
        
        Args:
            api_key: Your OpenRouter API key (get one at https://openrouter.ai)
        """
        self.api_key = api_key
        self.base_url = 'https://openrouter.ai/api/v1'
        self.model = 'deepseek/deepseek-chat'  # DeepSeek V3 - excellent for research tasks

    def chat(self, messages: List[ChatMessage]) -> ChatResponse:
        """
        Send our research query to the AI and get back a synthesized answer.
        
        This is where the magic happens! We send all our search results
        along with the user's question, and the AI reads through everything
        to give us a comprehensive, well-researched response.
        
        Args:
            messages: List of ChatMessage objects forming our conversation
            
        Returns:
            ChatResponse containing the AI's synthesized answer
            
        Raises:
            Exception: If the AI service is unavailable or returns an error
        """
        try:
            response = requests.post(
                f'{self.base_url}/chat/completions',
                headers={
                    'Authorization': f'Bearer {self.api_key}',
                    'Content-Type': 'application/json',
                    'HTTP-Referer': os.getenv('APP_URL', 'http://localhost:7860'),
                    'X-Title': 'AI Research Assistant - Powered by DeepSeek V3'
                },
                json={
                    'model': self.model,
                    'messages': [{'role': msg.role, 'content': msg.content} for msg in messages],
                    'temperature': 0.2,    # Lower temperature for more focused, factual responses
                    'max_tokens': 4000,    # Generous limit for comprehensive answers
                    'stream': False,       # Get the complete response at once
                    'top_p': 0.9,         # Slight randomness to keep responses natural
                    'frequency_penalty': 0.1,  # Reduce repetition
                    'presence_penalty': 0.1    # Encourage diverse vocabulary
                }
            )

            # Check if the AI service responded successfully
            if not response.ok:
                error_data = response.json() if response.content else {}
                error_message = error_data.get('error', {}).get('message', 'Unknown error occurred')
                raise Exception(f'AI service error: {response.status_code} - {error_message}')

            data = response.json()
            
            # Make sure we actually got a response from the AI
            if not data.get('choices') or len(data['choices']) == 0:
                raise Exception('The AI model did not generate a response. This might be due to content filtering or a temporary service issue.')

            return ChatResponse(
                content=data['choices'][0]['message']['content'],
                usage=data.get('usage')  # Track token usage for monitoring
            )
            
        except requests.exceptions.RequestException as e:
            # Handle network-related errors
            raise Exception(f'Network error while connecting to AI service: {str(e)}')
        except Exception as error:
            print(f'OpenRouter API error: {error}')
            raise error

    def synthesize_search_results(self, query: str, search_results: List[Any]) -> str:
        """
        Transform raw search results into a comprehensive, well-researched answer.
        
        This is where our app really shines! We take all the information we've
        gathered from various sources and ask our AI to read through it all,
        identify the key insights, resolve any contradictions, and present
        everything in a clear, engaging way.
        
        Args:
            query: The user's original research question
            search_results: List of SearchResult objects with source information
            
        Returns:
            A comprehensive answer with proper citations and analysis
        """
        # Craft a detailed system prompt that guides the AI to be helpful and accurate
        system_prompt = """You are an expert research assistant with a talent for synthesizing information from multiple sources into clear, comprehensive answers.

Your expertise includes:
- Reading and analyzing diverse sources quickly and accurately
- Identifying key insights and connecting related information
- Presenting complex topics in an accessible, engaging way
- Maintaining objectivity while acknowledging different perspectives
- Providing proper citations so readers can verify and explore further

When synthesizing information:
1. Lead with the most important insights that directly answer the question
2. Organize information logically with clear headings when helpful
3. Include relevant details and context that enhance understanding
4. Note any conflicting information and explain different viewpoints
5. Use citations [1], [2], etc. that correspond to the numbered sources
6. Write in a conversational but authoritative tone
7. Ensure accuracy while making the content engaging and readable

Remember: Your goal is to save the reader time while giving them confidence in the information and the ability to dive deeper if they want."""

        # Prepare the search context in a clear, structured format
        search_context = '\n'.join([
            f"[{index + 1}] {result.title}\nSource: {result.domain}\nURL: {result.url}\nContent: {result.snippet}\n"
            for index, result in enumerate(search_results)
        ])

        # Create a detailed user prompt that gives the AI everything it needs
        user_prompt = f"""Research Question: {query}

Sources Found:
{search_context}

Please provide a comprehensive, well-researched answer based on these sources. Structure your response to be informative and engaging, with proper citations using [1], [2], etc. format. If sources present different perspectives, acknowledge them. Focus on accuracy and clarity while maintaining a conversational tone."""

        # Send our carefully crafted messages to the AI
        messages = [
            ChatMessage(role='system', content=system_prompt),
            ChatMessage(role='user', content=user_prompt)
        ]

        response = self.chat(messages)
        return response.content

# Global client instance for efficient resource usage
_openrouter_client = None

def get_openrouter_client() -> OpenRouterClient:
    """
    Get or create our AI client instance.
    
    This function implements the singleton pattern, which means we only
    create one AI client for the entire application. This is more efficient
    than creating a new client for every request, and it helps us manage
    our API usage more effectively.
    
    Returns:
        OpenRouterClient: Ready-to-use AI client
        
    Raises:
        Exception: If the OpenRouter API key is not configured
    """
    global _openrouter_client
    
    if _openrouter_client is None:
        api_key = os.getenv('OPENROUTER_API_KEY')
        
        if not api_key:
            raise Exception(
                'OpenRouter API key not configured. '
                'Please add OPENROUTER_API_KEY to your .env file. '
                'Get your key at https://openrouter.ai'
            )
            
        _openrouter_client = OpenRouterClient(api_key)
        
    return _openrouter_client