"""
Scraper Package - Collection of web scrapers for tech news sources

This package contains classes for scraping various tech news sources including
Hacker News, Reddit, Dev.to and GitHub Trending. Each scraper follows a
consistent interface with a `scrape()` method that returns a list of articles.
"""

import logging

from .hacker_news_scraper import HackerNewsScraper
from .reddit_scraper import RedditScraper
from .devto_scraper import DevToScraper
from .github_trending_scraper import GitHubTrendingScraper

# Configure package-level logger
logger = logging.getLogger(__name__)

__all__ = [
    'HackerNewsScraper',
    'RedditScraper',
    'DevToScraper',
    'GitHubTrendingScraper',
    'get_all_scrapers'
]

def get_all_scrapers(reddit_subreddits=None):
    """
    Create instances of all available scrapers.
    
    Args:
        reddit_subreddits: List of subreddit names for the Reddit scraper
        
    Returns:
        Dictionary mapping scraper names to scraper instances
    """
    if reddit_subreddits is None:
        reddit_subreddits = ["programming", "webdev", "MachineLearning"]
        
    return {
        "Hacker News": HackerNewsScraper(),
        "Reddit": RedditScraper(reddit_subreddits),
        "Dev.to": DevToScraper(),
        "GitHub Trending": GitHubTrendingScraper(),
    }