import os
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional

# Configure logger
logger = logging.getLogger(__name__)

class MarkdownStorage:
    """
    A class for storing article digests in Markdown format.
    
    This class provides functionality to create and save article digests
    as Markdown files in a specified output directory.
    """
    
    def __init__(self, output_dir: str = "output"):
        """
        Initialize the markdown storage with a directory for saving files.
        
        Args:
            output_dir: Directory where markdown files will be stored
        """
        self.output_dir = output_dir
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        logger.info(f"Initialized markdown storage in directory: {output_dir}")
        
    def create_digest(self, summaries: List[Dict[str, Any]]) -> str:
        """
        Creates markdown content from article summaries.
        
        Args:
            summaries: List of dictionaries containing article summaries
            
        Returns:
            Formatted markdown content
        """
        # Create header with title and timestamp
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        digest_content = "# Daily Tech News Digest\n\n"
        digest_content += f"Generated on: {current_time}\n\n"
        
        # Add table of contents if there are more than 5 articles
        if len(summaries) > 5:
            digest_content += "## Table of Contents\n\n"
            for i, summary in enumerate(summaries, 1):
                title = summary.get('title', 'Untitled Article')
                digest_content += f"{i}. [{title}](#{i}-{self._format_anchor(title)})\n"
            digest_content += "\n---\n\n"
        
        # Add each article with consistent formatting
        for i, summary in enumerate(summaries, 1):
            title = summary.get('title', 'Untitled Article')
            
            # Add article header with index
            digest_content += f"## {i}. {title}\n\n"
            
            # Add source information
            source_name = summary.get('source', 'Unknown Source')
            digest_content += f"**Source**: {source_name}\n\n"
            
            # Add link with proper Markdown formatting
            link = summary.get('link', '')
            if link:
                digest_content += f"**Link**: [{link}]({link})\n\n"
            else:
                digest_content += f"**Link**: [No link available]()\n\n"
            
            # Add publication date if available
            date = summary.get('date')
            if date:
                digest_content += f"**Date**: {date}\n\n"
            
            # Add the summary content
            summary_text = summary.get('summary', 'No summary available.')
            digest_content += f"{summary_text}\n\n"
            
            # Add separator between articles
            digest_content += "---\n\n"
        
        return digest_content
    
    def save_digest(self, summaries: List[Dict[str, Any]], filename: Optional[str] = None) -> str:
        """
        Saves the digest content to a markdown file.
        
        Args:
            summaries: List of dictionaries containing article summaries
            filename: Custom filename. If None, uses current date
            
        Returns:
            Path to the saved file
        """
        if not summaries:
            logger.warning("No summaries provided to save")
            return ""
        
        # Generate default filename if none provided
        if not filename:
            filename = f"tech_digest_{datetime.now().strftime('%Y%m%d')}.md"
        
        # Create full file path
        file_path = os.path.join(self.output_dir, filename)
        
        try:
            # Generate digest content
            digest_content = self.create_digest(summaries)
            
            # Write content to file
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(digest_content)
            
            logger.info(f"Digest saved to {file_path}")
            return file_path
            
        except Exception as e:
            logger.error(f"Error saving digest to {file_path}: {str(e)}", exc_info=True)
            return ""
    
    @staticmethod
    def _format_anchor(text: str) -> str:
        """
        Format text for use as a Markdown anchor.
        
        Args:
            text: The title text to format
            
        Returns:
            Anchor-formatted text
        """
        # Convert to lowercase, replace spaces with hyphens, remove special characters
        anchor = text.lower()
        anchor = anchor.replace(' ', '-')
        anchor = ''.join(c for c in anchor if c.isalnum() or c == '-')
        return anchor