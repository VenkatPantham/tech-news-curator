import os
import logging
from typing import List, Dict, Any, Optional
from transformers import pipeline, AutoTokenizer

# Configure logger
logger = logging.getLogger(__name__)

class Summarizer:
    """
    A class for summarizing articles using a local LLM summarizer.
    """
    
    def __init__(self, model_name: str = "facebook/bart-large-cnn"):
        """
        Initialize the Summarizer with a local summarizer.
        
        Args:
            model_name (str): The model name to use for summarization.
                              Defaults to "facebook/bart-large-cnn".
                              Other good options: "sshleifer/distilbart-cnn-12-6",
                              "google/pegasus-xsum" (more concise summaries),
                              "facebook/bart-large-xsum" (better for news)
        """
        try:
            # Initialize the tokenizer for length calculations
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            
            # Initialize the summarization pipeline
            self.summarizer_pipeline = pipeline(
                "summarization", 
                model=model_name,
                tokenizer=self.tokenizer
            )
            logger.info(f"Local summarizer initialized successfully using {model_name}")
        except Exception as e:
            logger.error(f"Error initializing local summarizer: {str(e)}")
            self.summarizer_pipeline = None
            self.tokenizer = None
    
    def clean_text(self, text: str) -> str:
        """
        Clean and normalize input text for better summarization.
        
        Args:
            text (str): Raw text to clean
            
        Returns:
            str: Cleaned text
        """
        if not text:
            return ""
            
        # Replace multiple newlines with a single one
        cleaned = ' '.join(line.strip() for line in text.split('\n') if line.strip())
        
        # Replace multiple spaces with single space
        cleaned = ' '.join(cleaned.split())
        
        # Fix common encoding issues
        replacements = {
            '&amp;': '&',
            '&lt;': '<',
            '&gt;': '>',
            '&quot;': '"',
            '&#39;': "'"
        }
        
        for old, new in replacements.items():
            cleaned = cleaned.replace(old, new)
            
        return cleaned
            
    def summarize(self, text: str) -> str:
        """
        Summarize a single text passage using the local summarizer.
        
        Args:
            text (str): The text content to summarize.
            
        Returns:
            str: A more detailed summary of the input text.
        """
        if not self.summarizer_pipeline or not self.tokenizer:
            logger.error("Local summarizer not initialized")
            return "Summary unavailable: local summarizer not initialized"
        
        # Clean the input text
        cleaned_text = self.clean_text(text)
        if not cleaned_text:
            return "No content available for summarization."
            
        words = cleaned_text.split()
        input_length = len(words)
        
        # For very long inputs, use chunking and summarize each part
        if input_length > 1000:
            logger.info(f"Long document detected ({input_length} words). Using chunked summarization.")
            return self._summarize_long_text(cleaned_text)
        
        # Calculate token count (more accurate than word count for models)
        tokens = self.tokenizer(cleaned_text, return_tensors="pt")
        token_count = len(tokens["input_ids"][0])
        
        # Handle model context size limitations
        max_model_tokens = 1024  # Typical limit for bart models
        if token_count > max_model_tokens:
            # Truncate to fit model limits with margin for special tokens
            cleaned_text = self.tokenizer.decode(tokens["input_ids"][0][:max_model_tokens-50], skip_special_tokens=True)
            logger.warning(f"Input truncated from {token_count} tokens to fit model context window")
            words = cleaned_text.split()
            input_length = len(words)
        
        # Dynamic length parameters based on input word count
        # For summarization, typically max_length should be smaller than input_length
        if input_length < 30:
            # For very short texts, just keep most of it
            max_length = max(10, min(input_length - 1, 25))
            min_length = max(5, max_length // 2)
        elif input_length < 100:
            # For short texts, aim for 40-50% compression
            max_length = min(input_length * 3 // 5, 50)  # About 60% of input
            min_length = max(20, max_length // 2)
        elif input_length < 300:
            # For medium texts, aim for 60-70% compression
            max_length = min(input_length * 3 // 10, 90)  # About 30% of input
            min_length = max(40, max_length // 2)
        else:
            # For longer texts, cap the max length
            max_length = min(120, input_length // 4)  # Maximum length cap
            min_length = max(60, max_length // 2)

        logger.debug(f"Summarizing text with input length {input_length} words. "
                     f"Using min_length={min_length} and max_length={max_length}.")
        
        try:
            # Ensure max_length is always less than input_length to avoid warnings
            if max_length >= input_length:
                max_length = max(input_length - 1, 5)  # At least make it 1 less than input
                min_length = max(3, max_length // 2)
                logger.debug(f"Adjusted max_length to {max_length} to avoid warning")
                
            summary = self.summarizer_pipeline(
                cleaned_text,
                max_length=max_length,
                min_length=min_length,
                do_sample=False,
                num_beams=4,  # Use beam search for better quality
                early_stopping=True
            )
            
            result = summary[0]['summary_text'].strip()
            
            # Ensure the summary ends with proper punctuation
            if result and not result[-1] in ['.', '!', '?', '"', '\'']:
                result += '.'
                
            return result
            
        except Exception as e:
            logger.error(f"Error during summarization: {str(e)}")
            return f"Summary unavailable: {str(e)}"
    
    def _summarize_long_text(self, text: str, chunk_size: int = 800) -> str:
        """
        Summarize long text by chunking it into smaller pieces.
        
        Args:
            text: Long text to summarize
            chunk_size: Approximate size of each chunk in words
            
        Returns:
            Combined summary
        """
        words = text.split()
        chunks = []
        
        # Split text into chunks
        for i in range(0, len(words), chunk_size):
            chunk = ' '.join(words[i:i + chunk_size])
            chunks.append(chunk)
        
        logger.info(f"Split long text into {len(chunks)} chunks for summarization")
        
        # Summarize each chunk
        chunk_summaries = []
        for i, chunk in enumerate(chunks):
            logger.debug(f"Summarizing chunk {i+1}/{len(chunks)}")
            # Use more aggressive summarization for chunks
            max_length = min(100, len(chunk.split()) // 3)
            min_length = max(50, max_length // 2)
            
            try:
                summary = self.summarizer_pipeline(
                    chunk,
                    max_length=max_length,
                    min_length=min_length,
                    do_sample=False,
                    num_beams=4
                )
                chunk_summaries.append(summary[0]['summary_text'].strip())
            except Exception as e:
                logger.error(f"Error summarizing chunk {i+1}: {str(e)}")
                # Use first sentence if summarization fails
                sentences = chunk.split('.')
                chunk_summaries.append(sentences[0] + ('.' if not sentences[0].endswith('.') else ''))
        
        # If we have multiple chunk summaries, summarize them again
        if len(chunk_summaries) > 1:
            combined_summary = " ".join(chunk_summaries)
            logger.debug("Generating meta-summary from chunk summaries")
            
            try:
                return self.summarize(combined_summary)
            except Exception as e:
                logger.error(f"Error in meta-summarization: {str(e)}")
                return " ".join(chunk_summaries)
        elif len(chunk_summaries) == 1:
            return chunk_summaries[0]
        else:
            return "Could not generate summary."
    
    def summarize_articles(self, articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Summarize a list of articles, preserving metadata.
        
        Args:
            articles (list): List of dictionaries containing article data with at least a 'title' key
                             and optionally 'summary', 'content', 'link', and 'source' keys.
                             
        Returns:
            list: A list of dictionaries with the same metadata plus summarized content.
        """
        if not articles:
            logger.warning("No articles provided for summarization")
            return []
            
        summaries = []
        for article in articles:
            logger.debug(f"Summarizing article: {article.get('title', 'Untitled')}")
            
            # Combine all available context for better summarization
            text_to_summarize = article.get('title', '')
            
            # Use full content if available (from our enhanced scrapers)
            if 'content' in article and article['content']:
                text_to_summarize += "\n\n" + article['content']
            # Fallback to existing summary if no content but summary exists
            elif 'summary' in article and article['summary']:
                text_to_summarize += "\n\n" + article['summary']
            
            # Add description if available (common for GitHub repositories)
            if 'description' in article and article['description'] and article['description'] not in text_to_summarize:
                text_to_summarize += "\n\n" + article['description']
                
            # Generate summary
            generated_summary = self.summarize(text_to_summarize)
            
            # Format summary based on source
            formatted_summary = self._format_summary_by_source(
                source=article.get('source', 'Unknown'),
                summary=generated_summary,
                title=article.get('title', '')
            )
            
            summaries.append({
                'title': article.get('title', 'Untitled'),
                'summary': formatted_summary,
                'link': article.get('link', ''),
                'source': article.get('source', 'Unknown'),
                'date': article.get('date', '')
            })
            
        logger.info(f"Summarized {len(summaries)} articles")
        return summaries
    
    def _format_summary_by_source(self, source: str, summary: str, title: str) -> str:
        """
        Format summary based on content source for better readability.
        
        Args:
            source: Content source name
            summary: Generated summary text
            title: Article title
            
        Returns:
            Formatted summary text
        """
        if not summary:
            return f"No summary available for this {source.lower()} content."
            
        source_lower = source.lower()
        summary = summary.strip()
        
        # GitHub repository formatting
        if 'github' in source_lower:
            if not any(summary.lower().startswith(prefix) for prefix in ['this repository', 'the repository']):
                # Check if summary starts with lowercase and needs grammatical correction
                if summary[0].islower() and not summary.lower().startswith('this'):
                    summary = f"This repository {summary}"
                elif not any(term in summary.lower() for term in ['repository', 'repo', 'project']):
                    summary = f"This repository {summary}"
        
        # Paper/research formatting
        elif any(s in source_lower for s in ['paper', 'research']):
            if not any(summary.lower().startswith(prefix) for prefix in ['this paper', 'the paper', 'this study', 'the study']):
                if summary[0].islower():
                    summary = f"This paper {summary}"
                elif not any(term in summary.lower() for term in ['paper', 'study', 'research']):
                    summary = f"This paper describes {summary}"
        
        # News article formatting
        elif any(s in source_lower for s in ['news', 'hacker news', 'dev.to']):
            if summary.lower().startswith(title.lower()[:20]):
                # Summary starts with the title, trim it
                title_words = title.lower().split()
                summary_words = summary.lower().split()
                overlap_len = 0
                for i, word in enumerate(summary_words):
                    if i >= len(title_words) or word != title_words[i]:
                        break
                    overlap_len += 1
                
                if overlap_len > 3:  # If significant overlap
                    words = summary.split()
                    summary = ' '.join(words[overlap_len:])
        
        # Ensure proper capitalization and punctuation
        if summary and summary[0].islower():
            summary = summary[0].upper() + summary[1:]
            
        if summary and not summary[-1] in ['.', '!', '?']:
            summary += '.'
            
        return summary