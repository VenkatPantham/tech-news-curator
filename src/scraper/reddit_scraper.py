import os
import logging
import praw
import requests
import time
import random
from bs4 import BeautifulSoup
from typing import List, Dict, Any, Optional
from datetime import datetime

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
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36'
        }
        logger.info(f"Initialized Reddit scraper for subreddits: {', '.join(subreddits)}")
        
    def scrape(self, limit: int = 10, fetch_content: bool = True) -> List[Dict[str, Any]]:
        """
        Scrape top posts from specified subreddits.
        
        Args:
            limit: Maximum number of posts to scrape per subreddit
            fetch_content: Whether to fetch full content from article links
            
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
                        created_date = datetime.fromtimestamp(submission.created_utc).strftime('%Y-%m-%d')
                        
                        # Get the submission URL and determine type
                        url = submission.url
                        is_self_post = submission.is_self
                        
                        # For self posts, include the post body
                        if is_self_post:
                            content = submission.selftext
                            summary = content[:300] + ("..." if len(content) > 300 else "")
                        else:
                            content = ""
                            summary = ""
                            
                        articles.append({
                            'title': submission.title,
                            'link': url,
                            'score': submission.score,
                            'date': created_date,
                            'subreddit': subreddit,
                            'source': f"Reddit r/{subreddit}",
                            'is_self_post': is_self_post,
                            'content': content,
                            'summary': summary,
                            'comments_link': f"https://reddit.com{submission.permalink}"
                        })
                        
                    logger.info(f"Scraped {limit} posts from r/{subreddit}")
                    
                except Exception as e:
                    logger.error(f"Error scraping subreddit {subreddit}: {str(e)}")
                    
            logger.info(f"Successfully scraped {len(articles)} total posts from Reddit")
            
            # For non-self posts, fetch external article content if requested
            if fetch_content:
                logger.info(f"Fetching external content for Reddit posts")
                articles_with_content = []
                for article in articles:
                    if not article['is_self_post'] and article['link'].startswith('http'):
                        try:
                            article_with_content = self.fetch_article_content(article)
                            articles_with_content.append(article_with_content)
                            # Add delay to avoid being blocked
                            time.sleep(random.uniform(0.5, 1.5))
                        except Exception as e:
                            logger.error(f"Error fetching content for {article['title']}: {str(e)}")
                            articles_with_content.append(article)  # Use original without content
                    else:
                        articles_with_content.append(article)  # Already has content or not applicable
                return articles_with_content
            else:
                return articles
            
        except Exception as e:
            logger.error(f"Error initializing Reddit scraper: {str(e)}")
            return []
    
    def fetch_article_content(self, article: Dict[str, Any]) -> Dict[str, Any]:
        """
        Fetch and parse the content of an article from its URL.
        
        Args:
            article: Article dictionary containing at least a 'link' key
            
        Returns:
            Article dictionary with additional 'content' and 'summary' fields
        """
        try:
            url = article['link']
            logger.debug(f"Fetching content from: {url}")
            
            # Skip non-HTTP links or known file types that wouldn't have readable content
            if not url.startswith('http') or url.endswith(('.pdf', '.zip', '.jpg', '.png', '.gif')):
                logger.debug(f"Skipping non-web content: {url}")
                return article
            
            # Add a slight delay to avoid hitting rate limits
            time.sleep(random.uniform(0.2, 0.8))
            
            response = requests.get(url, headers=self.headers, timeout=15)
            
            if response.status_code != 200:
                logger.warning(f"Failed to fetch article content. Status code: {response.status_code}")
                return article
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Try to extract the article content using common patterns
            # Remove script, style elements and comments first
            for element in soup(['script', 'style', 'header', 'footer', 'nav', 'aside']):
                element.extract()
            
            # Try to find the main content using common article containers
            main_content = None
            content_selectors = [
                'article', 'div.post-content', 'div.article-content', 'div.content', 
                'div#content', 'div.post', 'main', 'div.main', 'div.entry-content',
                'div.story-body', 'div.article-body'
            ]
            
            for selector in content_selectors:
                content = soup.select_one(selector)
                if content and len(content.get_text(strip=True)) > 100:
                    main_content = content
                    break
            
            # If we didn't find content with common selectors, use the body
            if not main_content:
                main_content = soup.body
            
            # Extract text and clean it up
            if main_content:
                # Get text content with preserved spacing for paragraphs
                paragraphs = main_content.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
                if paragraphs:
                    content = "\n\n".join(p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True))
                else:
                    # Fallback to all text if no paragraphs found
                    content = main_content.get_text(strip=True)
                    
                # Clean up excess whitespace
                content = ' '.join(content.split())
                
                # Create a brief summary (first 300 characters)
                summary = content[:300] + ("..." if len(content) > 300 else "")
                
                logger.debug(f"Successfully fetched content for: {article['title']}")
                
                # Add content and summary to article dictionary
                article['content'] = content
                article['summary'] = summary
            
            return article
            
        except Exception as e:
            logger.error(f"Error fetching article content: {str(e)}")
            return article
            
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