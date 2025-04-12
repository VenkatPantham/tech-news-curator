#!/usr/bin/env python3
"""
Tech News Curator - Main Application

This module orchestrates the scraping, summarization, and distribution
of technology news articles from various sources.
"""

import os
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional

# Third-party imports
from dotenv import load_dotenv

# Local imports - utilities
from utils.logger import configure_logging

# Local imports - scrapers
from scraper import get_all_scrapers

# Local imports - other modules
from summarizer.summarizer import Summarizer
from storage.email_digest import EmailDigest
from storage.markdown_storage import MarkdownStorage


class TechNewsConfiguration:
    """Configuration settings for the Tech News Curator application."""
    
    def __init__(self, config_file: Optional[str] = None):
        """
        Initialize configuration from environment variables and optional config file.
        
        Args:
            config_file: Optional path to a configuration file
        """
        # Load environment variables
        load_dotenv()
        
        # Scraping configuration
        self.articles_per_source = int(os.getenv("ARTICLES_PER_SOURCE", "5"))
        self.reddit_subreddits = os.getenv("REDDIT_SUBREDDITS", "programming,webdev,MachineLearning").split(",")
        self.arxiv_categories = os.getenv("ARXIV_CATEGORIES", "cs.AI,cs.LG").split(",")
        
        # API keys and credentials
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.smtp_email = os.getenv("SMTP_EMAIL")
        self.smtp_password = os.getenv("SMTP_PASSWORD")
        self.email_recipients = os.getenv("EMAIL_RECIPIENTS", "").split(",")
        # Output configuration
        self.output_directory = os.getenv("OUTPUT_DIRECTORY", "output")
        self.should_send_email = os.getenv("SEND_EMAIL", "true").lower() in ("true", "yes", "1")
    
        
        # Logging configuration
        self.log_level = os.getenv("LOG_LEVEL", "INFO").upper()
        self.log_file = os.getenv("LOG_FILE", "tech_news_curator.log")
        self.log_dir = os.getenv("LOG_DIR", "logs")
        
        # Load from config file if provided
        if config_file and os.path.exists(config_file):
            self._load_config_file(config_file)
            
        # Validate configuration
        self._validate_config()
        
    def _load_config_file(self, config_file: str) -> None:
        """Load configuration from a file."""
        # Implement config file loading logic if needed
        logger.info(f"Loading configuration from {config_file}")
        pass
            
    def _validate_config(self) -> None:
        """Validate configuration settings and log warnings for missing values."""
        if not self.openai_api_key:
            logger.warning("OpenAI API key not found! Summarization will not work.")
            
        if self.should_send_email:
            if not self.smtp_email or not self.smtp_password:
                logger.warning("Email sending is enabled but SMTP credentials are missing")
                self.should_send_email = False
            
            if not self.email_recipients or not any(self.email_recipients):
                logger.warning("Email sending is enabled but no recipients are configured")
                self.should_send_email = False


class ArticleProcessor:
    """Processes articles from various sources into a standardized format."""
    
    @staticmethod
    def standardize_article(article: Dict[str, Any], source: str) -> Dict[str, Any]:
        """
        Standardize article structure to ensure consistent format.
        
        Args:
            article: Raw article data from a scraper
            source: Name of the article source
            
        Returns:
            Standardized article dictionary
        """
        return {
            "title": article.get("title", "No Title"),
            "link": article.get("link", article.get("url", "")),
            "source": source,
            "date": article.get("date", datetime.now().strftime("%Y-%m-%d")),
            "summary": article.get("summary", ""),
            "original": article  # Preserve original data
        }
    
    @staticmethod
    def filter_duplicates(articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Filter out duplicate articles based on title and URL.
        
        Args:
            articles: List of standardized articles
            
        Returns:
            List of unique articles
        """
        unique_articles = []
        seen_links = set()
        seen_titles = set()
        
        for article in articles:
            title_fingerprint = article["title"].lower().strip()
            link_fingerprint = article["link"].strip()
            
            # Skip if we've seen this title or URL before
            if title_fingerprint in seen_titles or (link_fingerprint and link_fingerprint in seen_links):
                continue
                
            seen_titles.add(title_fingerprint)
            if link_fingerprint:
                seen_links.add(link_fingerprint)
            unique_articles.append(article)
        
        return unique_articles


class TechNewsCurator:
    """Main application controller for the Tech News Curator."""
    
    def __init__(self, config: TechNewsConfiguration):
        """
        Initialize with configuration settings.
        
        Args:
            config: Application configuration object
        """
        self.config = config
        self.scrapers = get_all_scrapers(self.config.reddit_subreddits)
        
        # Initialize other components
        self.summarizer = Summarizer()
        
        self.markdown_storage = MarkdownStorage(output_dir=self.config.output_directory)
        self.email_digest = EmailDigest(
            smtp_server="smtp.gmail.com",
            smtp_port=587,
            sender_email=self.config.smtp_email,
            sender_password=self.config.smtp_password,
        )
        
    def run(self) -> None:
        """Execute the complete news curation workflow."""
        try:
            # Step 1: Scrape articles from all sources
            logger.info("Starting article scraping process")
            all_articles = self._scrape_all_sources()
            
            # Step 2: Standardize and filter articles
            total_articles = sum(len(articles) for articles in all_articles.values())
            logger.info(f"Standardizing {total_articles} articles")
            processor = ArticleProcessor()
            standardized_articles = []
            
            for source, articles in all_articles.items():
                for article in articles:
                    standardized_articles.append(
                        processor.standardize_article(article, source)
                    )
            
            # Step 3: Remove duplicates
            unique_articles = processor.filter_duplicates(standardized_articles)
            logger.info(f"Filtered to {len(unique_articles)} unique articles")
            
            # Step 4: Summarize articles
            logger.info("Generating summaries")
            summaries = self.summarizer.summarize_articles(unique_articles)
            
            # Step 5: Save to markdown
            logger.info("Saving digest to markdown")
            markdown_path = self.markdown_storage.save_digest(summaries)
            logger.info(f"Markdown digest saved to: {markdown_path}")
            
            # Step 6: Send email if enabled
            if self.config.should_send_email and self.config.email_recipients:
                logger.info(f"Sending email digest to {len(self.config.email_recipients)} recipients")
                email_sent = self.email_digest.send_digest(self.config.email_recipients, summaries)
                
                if email_sent:
                    logger.info("Email digest sent successfully")
                else:
                    logger.error("Failed to send email digest")
            else:
                logger.info("Email sending is disabled. Set should_send_email to True to enable.")
            
            logger.info("Tech news curation complete!")
            
        except Exception as e:
            logger.error(f"Error in curation process: {str(e)}", exc_info=True)
    
    def _scrape_all_sources(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Scrape articles from all configured sources.
        
        Returns:
            Dictionary mapping source names to lists of articles
        """
        results = {}
        limit = self.config.articles_per_source
        
        for source_name, scraper in self.scrapers.items():
            try:
                if source_name == "arXiv" and hasattr(scraper, "scrape") and callable(scraper.scrape):
                    results[source_name] = scraper.scrape(
                        category=self.config.arxiv_categories[0], 
                        limit=limit
                    )
                elif hasattr(scraper, "scrape") and callable(scraper.scrape):
                    results[source_name] = scraper.scrape(limit=limit)
                else:
                    logger.error(f"Scraper for {source_name} does not have a valid scrape method")
                    results[source_name] = []
                    
                logger.info(f"Scraped {len(results[source_name])} items from {source_name}")
                
            except Exception as e:
                logger.error(f"Error scraping {source_name}: {str(e)}")
                results[source_name] = []
            
        return results


def main():
    """Main entry point for the application."""
    # Initialize configuration
    config = TechNewsConfiguration()
    
    # Configure logging
    log_level = getattr(logging, config.log_level, logging.INFO)
    configure_logging(
        level=log_level,
        log_file=config.log_file,
        log_dir=config.log_dir
    )
    
    # Log startup information
    global logger
    logger = logging.getLogger(__name__)
    logger.info(f"Starting Tech News Curator (log level: {config.log_level})")
    
    # Create and run the curator
    curator = TechNewsCurator(config)
    curator.run()


if __name__ == "__main__":
    main()