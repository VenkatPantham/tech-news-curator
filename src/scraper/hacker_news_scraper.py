import requests
import logging
from bs4 import BeautifulSoup
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
    
    def scrape(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Scrape top articles from Hacker News.
        
        Args:
            limit: Maximum number of articles to scrape
            
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
                
                articles.append({
                    'title': title, 
                    'link': link,
                    'comments_link': comments_link,
                    'score': score_text,
                    'author': author,
                    'date': pub_date,
                    'source': 'Hacker News'
                })
                
                if len(articles) >= limit:
                    break
            
            logger.info(f"Successfully scraped {len(articles)} articles from Hacker News")
            return articles
            
        except Exception as e:
            logger.error(f"Error scraping Hacker News: {e}")
            return []
            
    def get_newest(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Scrape newest articles from Hacker News.
        
        Args:
            limit: Maximum number of articles to scrape
            
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
            return articles
            
        except Exception as e:
            logger.error(f"Error scraping Hacker News newest: {e}")
            return []
            
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