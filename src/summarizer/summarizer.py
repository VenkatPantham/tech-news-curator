import os
import logging
from typing import List, Dict, Any, Optional
from openai import OpenAI

# Configure logger
logger = logging.getLogger(__name__)

class Summarizer:
    """
    A class for summarizing articles using OpenAI's API.
    
    This class provides methods to summarize individual text content
    or batches of articles, returning concise summaries.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the Summarizer with an OpenAI API key.
        
        Args:
            api_key (str, optional): The OpenAI API key for authentication.
                                     If None, attempts to use environment variable.
        """
        if api_key is None:
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                logger.warning("No OpenAI API key provided and none found in environment")
        self.client = OpenAI(api_key=api_key) if api_key else None
            
    def summarize(self, text: str) -> str:
        """
        Summarize a single text passage using OpenAI.
        
        Args:
            text (str): The text content to summarize
            
        Returns:
            str: A concise summary of the input text
        """
        if not self.client:
            logger.error("Cannot summarize: OpenAI client not initialized (missing API key)")
            return "Summary unavailable: API not configured"
            
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that summarizes text concisely."},
                    {"role": "user", "content": f"Summarize the following text:\n\n{text}"}
                ],
                max_tokens=150
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"Error during summarization: {str(e)}")
            return f"Summary unavailable: {str(e)}"
    
    def summarize_articles(self, articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Summarize a list of articles, preserving metadata.
        
        Args:
            articles (list): List of dictionaries containing article data with at least 'title' key
                            and optionally 'summary', 'link', and 'source' keys
            
        Returns:
            list: A list of dictionaries with the same metadata plus summarized content
        """
        if not articles:
            logger.warning("No articles provided for summarization")
            return []
            
        summaries = []
        for article in articles:
            logger.debug(f"Summarizing article: {article.get('title', 'Untitled')}")
            
            # Combine title and existing summary (if any) for more context
            text_to_summarize = article['title']
            if 'summary' in article and article['summary']:
                text_to_summarize += "\n\n" + article['summary']
                
            # Generate the summary
            summary = self.summarize(text_to_summarize)
            
            # Create a new entry with all metadata preserved
            summaries.append({
                'title': article['title'],
                'summary': summary,
                'link': article.get('link', ''),
                'source': article.get('source', 'Unknown'),
                'date': article.get('date', '')
            })
            
        logger.info(f"Summarized {len(summaries)} articles")
        return summaries