import requests
import logging
from bs4 import BeautifulSoup
import time
import random
from typing import List, Dict, Any, Optional
from datetime import datetime

# Configure logger
logger = logging.getLogger(__name__)

class HackerNewsScraper:
    """
    A class for scraping tech articles from Hacker News.
    
    This class retrieves top articles from the Hacker News front page,
    providing structured data including title, link, and score.
    """
    
    def __init__(self):
        """Initialize the Hacker News scraper with base URL and headers."""
        self.base_url = "https://news.ycombinator.com/"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36'
        }
        logger.info("Initialized Hacker News scraper")
    
    def scrape(self, limit: int = 10, fetch_content: bool = True) -> List[Dict[str, Any]]:
        """
        Scrape top articles from Hacker News.
        
        Args:
            limit: Maximum number of articles to scrape
            fetch_content: Whether to fetch full content for each article
            
        Returns:
            List of article dictionaries
        """
        try:
            logger.info(f"Fetching up to {limit} articles from Hacker News")
            response = requests.get(self.base_url, headers=self.headers, timeout=10)
            
            if response.status_code != 200:
                logger.warning(f"Failed to fetch Hacker News. Status code: {response.status_code}")
                return []
                
            soup = BeautifulSoup(response.text, 'html.parser')
            
            articles = []
            for item in soup.select('tr.athing'):
                title_element = item.select_one('span.titleline > a')
                if not title_element:
                    continue
                    
                title = title_element.get_text(strip=True)
                link = title_element['href']
                if not link.startswith('http'):
                    link = self.base_url + link
                
                # Extract item ID for comments link
                item_id = item.get('id')
                comments_link = f"{self.base_url}item?id={item_id}" if item_id else None
                
                # Extract metadata from the subtext row
                subtext_row = item.find_next_sibling('tr')
                score_text = 'Unknown'
                author = None
                pub_date = None
                
                if subtext_row:
                    subtext = subtext_row.select_one('td.subtext')
                    if subtext:
                        # Extract score
                        score_element = subtext.select_one('.score')
                        if score_element:
                            score_text = score_element.get_text(strip=True)
                        
                        # Extract author
                        author_element = subtext.select_one('.hnuser')
                        if author_element:
                            author = author_element.get_text(strip=True)
                        
                        # Extract approximate date from the "age" element
                        age_element = subtext.select_one('.age')
                        if age_element and age_element.get('title'):
                            # The title attribute contains the exact timestamp
                            try:
                                timestamp = age_element.get('title')
                                pub_date = datetime.strptime(timestamp, '%Y-%m-%dT%H:%M:%S').strftime('%Y-%m-%d')
                            except ValueError:
                                pub_date = datetime.now().strftime('%Y-%m-%d')
                
                article = {
                    'title': title, 
                    'link': link,
                    'comments_link': comments_link,
                    'score': score_text,
                    'author': author,
                    'date': pub_date,
                    'source': 'Hacker News'
                }
                
                articles.append(article)
                
                if len(articles) >= limit:
                    break
            
            logger.info(f"Successfully scraped {len(articles)} articles from Hacker News")
            
            # Fetch full content for each article if requested
            if fetch_content:
                logger.info(f"Fetching content for {len(articles)} articles")
                articles_with_content = []
                for article in articles:
                    try:
                        article_with_content = self.fetch_article_content(article)
                        articles_with_content.append(article_with_content)
                        # Add a small delay to avoid being blocked
                        time.sleep(random.uniform(0.5, 1.5))
                    except Exception as e:
                        logger.error(f"Error fetching content for {article['title']}: {str(e)}")
                        articles_with_content.append(article)  # Use original article without content
                return articles_with_content
            else:
                return articles
            
        except Exception as e:
            logger.error(f"Error scraping Hacker News: {e}")
            return []
            
    def get_newest(self, limit: int = 10, fetch_content: bool = True) -> List[Dict[str, Any]]:
        """
        Scrape newest articles from Hacker News.
        
        Args:
            limit: Maximum number of articles to scrape
            fetch_content: Whether to fetch full content for each article
            
        Returns:
            List of article dictionaries
        """
        try:
            newest_url = f"{self.base_url}newest"
            logger.info(f"Fetching up to {limit} newest articles from Hacker News")
            
            response = requests.get(newest_url, headers=self.headers, timeout=10)
            
            if response.status_code != 200:
                logger.warning(f"Failed to fetch Hacker News newest. Status code: {response.status_code}")
                return []
                
            soup = BeautifulSoup(response.text, 'html.parser')
            
            articles = []
            for item in soup.select('tr.athing'):
                title_element = item.select_one('span.titleline > a')
                if not title_element:
                    continue
                    
                title = title_element.get_text(strip=True)
                link = title_element['href']
                if not link.startswith('http'):
                    link = self.base_url + link
                
                # Get additional information from the next row
                subtext_row = item.find_next_sibling('tr')
                
                # Create article dict with title and link
                article = {
                    'title': title, 
                    'link': link,
                    'source': 'Hacker News (New)'
                }
                
                # Extract metadata if available
                if subtext_row:
                    self._extract_metadata(article, subtext_row)
                
                articles.append(article)
                
                if len(articles) >= limit:
                    break
            
            logger.info(f"Successfully scraped {len(articles)} newest articles from Hacker News")
            
            # Fetch full content for each article if requested
            if fetch_content:
                logger.info(f"Fetching content for {len(articles)} newest articles")
                articles_with_content = []
                for article in articles:
                    try:
                        article_with_content = self.fetch_article_content(article)
                        articles_with_content.append(article_with_content)
                        # Add a small delay to avoid being blocked
                        time.sleep(random.uniform(0.5, 1.5))
                    except Exception as e:
                        logger.error(f"Error fetching content for {article['title']}: {str(e)}")
                        articles_with_content.append(article)  # Use original article without content
                return articles_with_content
            else:
                return articles
            
        except Exception as e:
            logger.error(f"Error scraping Hacker News newest: {e}")
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
                return {**article, 'content': '', 'summary': ''}
            
            # Add a slight delay to avoid hitting rate limits
            time.sleep(random.uniform(0.2, 0.8))
            
            response = requests.get(url, headers=self.headers, timeout=15)
            
            if response.status_code != 200:
                logger.warning(f"Failed to fetch article content. Status code: {response.status_code}")
                return {**article, 'content': '', 'summary': ''}
            
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
                
                # Create a brief summary (first 500 characters)
                summary = content[:500] + ("..." if len(content) > 500 else "")
                
                logger.debug(f"Successfully fetched content for: {article['title']}")
                
                # Add content and summary to article dictionary
                return {
                    **article,
                    'content': content,
                    'summary': summary
                }
            else:
                logger.warning(f"Could not extract content from: {url}")
                return {**article, 'content': '', 'summary': ''}
            
        except Exception as e:
            logger.error(f"Error fetching article content: {str(e)}")
            return {**article, 'content': '', 'summary': ''}
            
    def _extract_metadata(self, article: Dict[str, Any], subtext_row) -> None:
        """
        Extract metadata from a Hacker News article's subtext row.
        
        Args:
            article: Article dictionary to update with metadata
            subtext_row: BeautifulSoup element containing the subtext
        """
        subtext = subtext_row.select_one('td.subtext')
        if not subtext:
            return
            
        # Extract score
        score_element = subtext.select_one('.score')
        if score_element:
            article['score'] = score_element.get_text(strip=True)
        else:
            article['score'] = 'Unknown'
            
        # Extract author
        author_element = subtext.select_one('.hnuser')
        if author_element:
            article['author'] = author_element.get_text(strip=True)
            
        # Extract approximate date from the "age" element
        age_element = subtext.select_one('.age')
        if age_element and age_element.get('title'):
            # The title attribute contains the exact timestamp
            try:
                timestamp = age_element.get('title')
                article['date'] = datetime.strptime(timestamp, '%Y-%m-%dT%H:%M:%S').strftime('%Y-%m-%d')
            except ValueError:
                article['date'] = datetime.now().strftime('%Y-%m-%d')