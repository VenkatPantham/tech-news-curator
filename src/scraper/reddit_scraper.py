import os
import logging
import praw
from typing import List, Dict, Any, Optional

# Configure logger
logger = logging.getLogger(__name__)

class RedditScraper:
    """
    A class for scraping tech-related content from Reddit subreddits.
    
    This class handles authentication with the Reddit API and 
    provides methods to retrieve top posts from specified subreddits.
    """
    
    def __init__(self, subreddits: List[str]):
        """
        Initialize the Reddit scraper with subreddits to monitor.
        
        Args:
            subreddits: List of subreddit names to scrape
        """
        self.subreddits = subreddits
        logger.info(f"Initialized Reddit scraper for subreddits: {', '.join(subreddits)}")
        
    def scrape(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Scrape top posts from specified subreddits.
        
        Args:
            limit: Maximum number of posts to scrape per subreddit
            
        Returns:
            List of post dictionaries
        """
        try:
            # Get Reddit API credentials from environment variables
            client_id = os.getenv("REDDIT_CLIENT_ID")
            client_secret = os.getenv("REDDIT_CLIENT_SECRET")
            user_agent = os.getenv("REDDIT_USER_AGENT", "tech-news-curator (by /u/your_username)")
            
            # Check if credentials are set
            if not client_id or not client_secret:
                logger.error("Reddit API credentials not found in environment variables")
                return []
                
            reddit = praw.Reddit(
                client_id=client_id,
                client_secret=client_secret,
                user_agent=user_agent
            )
            
            articles = []
            for subreddit in self.subreddits:
                try:
                    logger.debug(f"Scraping subreddit: r/{subreddit}")
                    submissions = reddit.subreddit(subreddit).new(limit=limit)
                    
                    for submission in submissions:
                        # Format the creation date
                        from datetime import datetime
                        created_date = datetime.fromtimestamp(submission.created_utc).strftime('%Y-%m-%d')
                        
                        articles.append({
                            'title': submission.title,
                            'link': submission.url,
                            'score': submission.score,
                            'date': created_date,
                            'subreddit': subreddit,
                            'source': f"Reddit r/{subreddit}"
                        })
                        
                    logger.info(f"Scraped {limit} posts from r/{subreddit}")
                    
                except Exception as e:
                    logger.error(f"Error scraping subreddit {subreddit}: {str(e)}")
                    
            logger.info(f"Successfully scraped {len(articles)} total posts from Reddit")
            return articles
            
        except Exception as e:
            logger.error(f"Error initializing Reddit scraper: {str(e)}")
            return []
            
    def filter_articles(self, articles: List[Dict[str, Any]], keyword: str) -> List[Dict[str, Any]]:
        """
        Filter articles based on keyword presence in title.
        
        Args:
            articles: List of article dictionaries
            keyword: Keyword to filter by
            
        Returns:
            Filtered list of article dictionaries
        """
        filtered = [article for article in articles if keyword.lower() in article['title'].lower()]
        logger.info(f"Filtered Reddit articles by keyword '{keyword}': {len(filtered)}/{len(articles)} matches")
        return filtered